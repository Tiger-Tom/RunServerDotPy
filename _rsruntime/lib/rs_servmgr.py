#!/bin/python3

#> Imports
from inspect import isabstract
from traceback import format_exception
import threading
from select import select
import sys
import os
# Shell
import shlex
from getpass import getpass
import subprocess
# Files
from pathlib import Path
import shutil
# Types
import typing
from types import SimpleNamespace
from abc import ABC, abstractmethod, abstractproperty
from cmd import Cmd
# Manager-specific modules
try: from rcon.source import Client as RCONClient
except ModuleNotFoundError: RCONClient = None
#</Imports

# RunServer Module
import RS
from RS import Config, LineParser
from RS.Util import Hooks, PerfCounter

#> Header >/
# Base classes
class BaseServerManager(ABC):
    __slots__ = ('logger', 'hooks', 'managers')
    basemanagers = SimpleNamespace()
    def __init__(self):
        self.logger = RS.logger.getChild(f'SM<{self.name}>')
        self.hooks = Hooks.SingleHook()
        self.hooks.register(print)
        self.hooks.register(LineParser.handle_line)
    def __init_subclass__(cls):
        logger = RS.logger.getChild('SM._base')
        logger.debug(f'subclassed by {"abstract" if isabstract(cls) else "concrete"} {cls.name}')
        if isabstract(cls):
            cls.register_base()
            return
        logger.debug(f'registering {cls.name} in ServerManager')
        ServerManager.register(cls)
        
    # Non-abstract methods
    def handle_line(self, line: str):
        sys.stdout.write(line)
        RS.LP.handle_line(line)
    def handle_input(self, line: str):
        self.write(line)
    @classmethod
    def _bias_config(cls) -> float:
        return (-float('inf') if Config(f'server_manager/blacklist/{cls.name}', False) else 0.0) + \
               (100.0 if Config(f'server_manager/prefer/{cls.name}', False) else 0.0)
    @classmethod
    def _bias_override(cls) -> float | None:
        return Config(f'override/server_manager/bias_mod/{cls.name}', None, Config.on_missing.SET_RETURN_DEFAULT)
    @classmethod
    @property
    def real_bias(cls) -> float:
        if (b := cls._bias_override()) is not None: return b
        return cls.bias + cls._bias_config()
    @classmethod
    def register_base(cls):
        setattr(cls.basemanagers, cls.name.replace('.', '_'), cls)
    @classmethod
    @property
    def name(cls) -> str:
        return f'{"_builtin" if cls.__module__ == BaseServerManager.__module__ else cls.__module__}.{cls.__qualname__}'.replace('/', '.')
    @classmethod
    @property
    def type(cls) -> str:
        return '/'.join(t for c in cls.__mro__[cls.__mro__.index(BaseServerManager)-1::-1] for t in c._type)
    @staticmethod
    def cli_line() -> list:
        return shlex.split(Config('server_manager/command_line', '{java_binary} {java_args} {server_jar_path} {server_args}').format(
            java_binary = Config('java/java_binary', 'java'),
            java_args = Config('java/java_args', '-Xmx{allocated_ram} -Xms{allocated_ram} -jar').format(allocated_ram=Config('minecraft/allocated_ram', '1024M')),
            server_jar_path = (Path(Config('minecraft/path/base', './minecraft')) / Config('minecraft/path/server_jar', 'server.jar')).absolute(),
            server_args = Config('minecraft/server_args', '--nogui'),
        ))

    # Set config defaults
    cli_line()

    # Abstract methods
    @abstractmethod
    def start(self): pass
    @abstractmethod
    def write(self): pass
    # Abstract properties
    @classmethod
    @abstractproperty
    def bias(cls) -> float: pass
    @abstractproperty
    def _type(): pass

    # Capabilities
    @abstractproperty
    def cap_arbitrary_read() -> bool: pass
    @abstractproperty
    def cap_arbitrary_write() -> bool: pass
    ## With defaults
    cap_detachable: bool = False
    cap_attachable: bool = False
    cap_stoppable: bool = True # we usually have control via /stop
    cap_restartable: bool = False # we cannot always restart it
    cap_read_from_write: bool = False # most places cannot separate normal output from command output immediately

    # Misc. attributes
    attr_is_dummy: bool = False

class BaseInputManager(BaseServerManager, Cmd):
    __slots__ = ()
    _type = ('input_reader',)
    def __init__(self):
        BaseServerManager.__init__(self)
        Cmd.__init__(self)
    def emptyline(self): return
    def completedefault(self, text, line, begidx, endidx):
        print(f'{text!r} {line!r} {line!r} {begidx!r} {endidx!r}')
    def default(self, line: str):
        print(f'{line!r}')
class BasePopenManager(BaseServerManager):
    __slots__ = ('popen',)
    _type = ('popen_writer',)
    def __init__(self):
        super().__init__()

    cap_arbitrary_write = True
    cap_restartable = True
    
    def start(self):
        self.popen = subprocess.Popen(self.cli_line(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, bufsize=1, text=True, cwd=Config('minecraft/path/base', './minecraft'))

    # Set config defaults
    Config('minecraft/path/base', './minecraft')
# Manager
class ServerManager:
    managers = SimpleNamespace()
    def __new__(cls):
        logger = RS.logger.getChild('SM._staging')
        order = cls.preferred_order()
        logger.debug(f'Instantiating server manager; preferred order: {tuple(f"{c.name}:<{c.type}>,[{c.real_bias}]" for c in order)}')
        total_pc = PerfCounter()
        if not len(order): raise NotImplementedError('No ServerManagers found')
        for i,c in enumerate(order):
            if c.real_bias <= 0:
                raise RuntimeError(f'No suitable ServerManagers found (biases are all <= {c.real_bias}, which is <= 0) (tried for total of {total_pc})')
            # Debugging
            logger.infop(f'Staging ServerManager {c.name} (type {c.type}) (bias {c.real_bias}, index {i}) (T+{total_pc})...')
            ## Print out typing
            logger.debug(f'{c.name} typing:')
            logger.debug(f' _type: {c._type}')
            logger.debug(' Chain (MRO):')
            for i,m in enumerate(c.__mro__[:(c.__mro__.index(ABC) if ABC in c.__mro__ else c.__mro__.index(object))]):
                logger.debug(f'  {"^" if i else ">"} {getattr(m, "name", f"[unnamed?]{m.__module__}.{m.__qualname__}")}<{"abstract" if isabstract(m) else "concrete"}>')
            ## Capabilities
            logger.debug(f'{c.name} capabilites:')
            for a,v in ((a, getattr(c, a)) for a in dir(c) if a.startswith('cap_')):
                logger.debug(f' [{"Y" if v else "N"}] {a}')
            ## Attributes
            logger.debug(f'{c.name} attributes:')
            for a,v in ((a, getattr(c, a)) for a in dir(c) if a.startswith('attr_')):
                logger.debug(f'  {a}: {"<empty>" if v is None else ("[Y]" if v else "[N]") if isinstance(v, bool) else repr(v)}')
            # Try to instantiate
            current_pc = PerfCounter()
            try:
                inst = c()
                logger.debug(f'Successfully instantiated {c.name} as {inst} in {current_pc} (total of {total_pc})')
                inst.managers = cls.managers
                return inst
            except Exception as e:
                logger.error(f'Could not instantiate {c.name}:\n{"".join(format_exception(e))}\n (failed after {current_pc}, total of {total_pc})')
                if i < len(order):
                    logger.infop('Trying the next possible choice...')
        raise RuntimeError(f'None of the ServerManagers could be staged (tried for total of {total_pc}, cannot continue')
    @classmethod
    def register(cls, manager_type: typing.Type[BaseServerManager]):
        setattr(cls.managers, manager_type.name.replace('.', '_'), manager_type)
    @classmethod
    def preferred_order(cls) -> list[typing.Type[BaseServerManager]]:
        return sorted(cls.managers.__dict__.values(), key=lambda t: t.real_bias, reverse=True)
# Implementations
class ScreenManager(BaseServerManager):
    __slots__ = ('screen',)
    _type = ('screen',)
    def __init__(self):
        super().__init__()
        if shutil.which(Config('server_manager/screen/binary', 'screen')) is None:
            raise FileNotFoundError('ScreenManager requires the `screen` binary!')
        self.screen = self.Screen(Config('server_manager/screen/name', 'RS_ScreenManager_mcserverprocess'), self.cli_line())
    class Screen:
        __slots__ = ('name', 'cmdline')
        def __init__(self, name: str, cmdline: tuple[str]):
            self.name = shlex.quote(name)
            self.cmdline = ' '.join(cmdline)
        @property
        def _cmd_pfx(self) -> tuple[str]: return (Config('server_manager/screen/binary', 'screen'), '-x', self.name)
        # Commands
        def run_screen_cmd(self, *cmd: tuple[str]) -> str:
            return subprocess.check_output(self._cmd_pfx+cmd).decode(Config('server_manager/screen/encoding', sys.getdefaultencoding()))
        def run_screen_noout(self, *cmd: tuple[str]) -> int:
            return subprocess.call(self._cmd_pfx+cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Status
        @property
        def is_alive(self) -> bool:
            return not self.run_screen_noout('-X', 'info')
        # Logging
        def setup_logfifo(self) -> Path:
            if Config('server_manager/screen/reset_log', True): self.run_screen_cmd('-X', 'log', 'off')
            path = Path(Config('server_manager/screen/log_fifo', f'./_rslog/screen.{self.name}.fifo'))
            if not path.exists(): os.mkfifo(path)
            self.run_screen_cmd('-X', 'log', 'on')
            self.run_screen_cmd('-X', 'logfile', str(path))
            self.run_screen_cmd('-X', 'logfile', 'flush', str(Config('server_manager/screen/log_flush_secs', 1)))
        # Start/stop
        def start(self):
            subprocess.call((shutil.which(Config('server_manager/screen/binary', 'screen')), '-dmS', self.name))
        def stop(self):
            self.run_screen_noout('-X', 'kill')
    def start(self): raise NotImplementedError
    def write(self): raise NotImplementedError

    # Set config defaults
    Config('server_manager/screen/binary', 'screen')
    Config('server_manager/screen/name', 'RS_ScreenManager_mcserverprocess')
    Config('server_manager/screen/encoding', sys.getdefaultencoding())
    
    cap_arbitrary_read = True
    cap_arbitrary_write = True
    cap_detachable = True
    cap_attachable = True
    cap_restartable = True
    
    #bias = -float('inf') if shutil.which(Config('server_manager/screen/binary', 'screen')) is None else 10.0
    bias = -float('inf') # not implemented yet
class RConManager(BaseServerManager):
    __slots__ = ()
    _type = ('remote', 'passwd')
    
    def __init__(self):
        super().__init__()
        if RCONClient is None:
            raise ModuleNotFoundError('RCon module is required for RConManager!')
        if not Config('minecraft/rcon/enabled', False): raise RuntimeError('RCon is not enabled! (set it up in config: minecraft/rcon/enabled)')
        self.remote = f'{Config("minecraft/rcon/host", "127.0.0.1")}:{Config("minecraft/rcon/port", 25575)}'
        self.logger.infop(f'RCon remote: {self.remote} (can be set in config minecraft/rcon/)')
        self.rconpwd = Config('minecraft/rcon/password', None, Config.on_missing.SET_RETURN_DEFAULT)
        if self.rconpwd is None:
            self.rconpwd = getpass('Enter RCon password >')
            self.logger.warning('RCon password can be permanently set in config minecraft/rcon/password')
        raise NotImplementedError
    def start(self): raise NotImplementedError
    def write(self): raise NotImplementedError

    # Set config defaults
    Config('minecraft/rcon/host', '127.0.0.1')
    Config('minecraft/rcon/port', 25575)
    Config('minecraft/rcon/password', None, Config.on_missing.SET_RETURN_DEFAULT)

    cap_arbitrary_read = False
    cap_arbitrary_write = True
    cap_detachable = True
    cap_attachable = True
    cap_restartable = True
    cap_read_from_write = True
    
    @classmethod
    @property
    def bias(cls) -> float:
        if RCONClient is None: return -float('inf')
        if Config('minecraft/rcon/enabled', False):
            return 10.0
        return -255.0 #RConManager should be manually selected
class SelectManager(BasePopenManager):
    __slots__ = ()
    _type = ('select',)
    def start(self):
        super().start()
        outno = self.popen.stdout.fileno()
        inno = sys.stdin.fileno()
        # IO loop
        while self.popen.poll() is None:
            reads,_,_ = select((outno, inno), (), ())
            if inno in reads: self.handle_input(sys.stdin.readline())
            if outno in reads: self.handle_line(self.popen.stdout.readline())
        # Handle remaining lines
        for line in self.popen.stdout.readlines():
            self.handle_line(line)
    def write(self, line: str):
        self.popen.stdin.write(line)

    cap_arbitrary_read = True
    
    bias = 2.0
class DummyServerManager(BaseServerManager):
    __slots__ = ()
    _type = ('manual', 'dummy')
    def __init__(self):
        super().__init__()
        print('-----DUMMY SERVER MODE-----')
    def start(self):
        self.hooks(input('>DUMMY SERVER INPUT >'))
    def write(self, line: str):
        print(f'>DUMMY SERVER WRITE > {line}')

    cap_arbitrary_read = True
    cap_arbitrary_write = True
    cap_restartable = True

    attr_is_dummy = True
    
    bias = -50.0
class PyInterpreterServerManager(DummyServerManager):
    __slots__ = ('interpreter',)
    _type = ('manual', 'debug', 'interpreter',)
    def __init__(self):
        BaseServerManager.__init__(self)
    def start(self):
        import code
        def tc():
            import readline
            import rlcompleter
            _completer = None
            def complete(text: str, state: int):
                nonlocal _completer # first time I've ever actually had a reason to use this!
                if state == 0:
                    _completer = rlcompleter.Completer(self.interpreter.locals)
                return _completer.complete(text, state)
            readline.set_completer(complete)
            readline.parse_and_bind('tab: complete')
        self.interpreter = code.InteractiveConsole({'RS': RS, 'self': self, 'tc': tc})
        self.interpreter.interact(f'''Python Interpreter SM submode
    Some names are passed to this subinterpreter:
    - RS is the RunServer instance
    - self is the {self.__class__} instance
    - self.interpreter is the InteractiveConsole instance
    - tc() is a function that tries to enable tab completion
    Use CTRL+D to exit subinterpreter, as exit() exits both the sub and main interpreters''')
class NullServerManager(BaseServerManager):
    __slots__ = ()
    _type = ('null',)
    def start(self): pass
    def write(self, line: str): pass

    cap_arbitrary_read = True
    cap_arbitrary_write = True
    cap_restartable = True

    attr_is_dummy = True

    bias = -60.0
