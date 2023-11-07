#!/bin/python3

#> Imports
from inspect import isabstract
from traceback import format_exception
# Shell
import shlex
from getpass import getpass
# Files
from pathlib import Path
import shutil
# Types
import typing
from types import SimpleNamespace
from abc import ABC, abstractmethod, abstractproperty
# Manager-specific modules
try: from rcon.source import Client as RCONClient
except ModuleNotFoundError: RCONClient = None
#</Imports

# RunServer Module
import RS
from RS import Config, LineParser
from RS.Types import Hooks, PerfCounter

#> Header >/
# Base classes
class BaseServerManager(ABC):
    __slots__ = ('logger', 'hooks')
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
            cls.register()
            return
        logger.debug(f'registering {cls.name} in ServerManager')
        ServerManager.register(cls)
        
    # Non-abstract methods
    @classmethod
    def _bias_config(cls) -> float:
        return (-float('inf') if Config(f'server_manager/blacklist/{cls.name}', False) else 0.0) + \
               (100.0 if Config(f'server_manager/prefer/{cls.name}', False) else 0.0)
    @classmethod
    def _bias_override(cls) -> float | None:
        return Config(f'override/server_manager/bias_mod/{cls.name}', None)
    @classmethod
    @property
    def real_bias(cls) -> float:
        if (b := cls._bias_override()) is not None: return b
        return cls.bias + cls._bias_config()
    @classmethod
    def register(cls):
        setattr(cls.basemanagers, cls.name, cls)
    @classmethod
    @property
    def name(cls) -> str:
        return f'{"[builtin]" if cls.__module__ == BaseServerManager.__module__ else cls.__module__}.{cls.__qualname__}'.replace('/', '.')
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

    # Misc. attributes
    attr_is_dummy: bool = False
        
class BasePopenManager(BaseServerManager):
    __slots__ = ('popen',)
    _type = ('popen_writer',)
    def __init__(self):
        super().__init__()
        import subprocess

    cap_arbitrary_write = True
    cap_restartable = True
    
    def start(self):
        #Config('minecraft/path/base', './minecraft')
        ...
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
            logger.info(f'Staging ServerManager {c.name} (type {c.type}) (bias {c.real_bias}, index {i}) (T+{total_pc})...')
            ## Print out typing
            logger.debug(f'{c.name} typing:')
            logger.debug(f' _type: {c._type}')
            logger.debug(f' Chain (MRO):')
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
                return inst
            except Exception as e:
                logger.error(f'Could not instantiate {c.name}:\n{"".join(format_exception(e))}\n (failed after {current_pc}, total of {total_pc})')
                if i < len(order):
                    logger.warning('Trying the next possible choice...')
        raise RuntimeError('None of the ServerManagers could be staged (tried for total of {total_pc}, cannot continue')
    @classmethod
    def register(cls, manager_type: typing.Type[BaseServerManager]):
        setattr(cls.managers, manager_type.name, manager_type)
    @classmethod
    def preferred_order(cls) -> list[typing.Type[BaseServerManager]]:
        print(cls.managers.__dict__)
        return sorted(cls.managers.__dict__.values(), key=lambda t: t.real_bias, reverse=True)
# Implementations
class ScreenManager(BaseServerManager):
    __slots__ = ()
    _type = ('screen',)
    def __init__(self):
        super().__init__()
        if shutil.which(Config('server_manager/screen/binary', 'screen')) is None:
            raise FileNotFoundError('ScreenManager requires the `screen` binary!')
        Config('server_manager/screen/name', 'RS_ScreenManager_mcserverprocess')
    class Screen:
        __slots__ = ('name',)
        def __init__(self, name: str):
            self.name = shlex.quote(name)
        @property
        def _cmd_pfx(self) -> tuple[str]: return ('screen', '-x', self.name)
        # Commands
        def run_screen_cmd(self, cmd: tuple[str]) -> str:
            return subprocess.check_output(self._cmd_pfx+cmd).decode(Config('encoding', sys.getdefaultencoding()))
        # Status
        @property
        def is_alive(self) -> bool:
            return not not subprocess.call(('screen', '-x', 'rssm', '-X', 'info'), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Logging
        def setup_logfifo(self) -> Path:
            if Config('server_manager/screen/reset_log', True): self.run_screen_cmd('log', 'off')
            path = Path(Config('server_manager/screen/log_fifo', f'./screen.{Config["server_manager/screen/name"]}.fifo'))
            os.mkfifo(path)
            self.run_screen_cmd('logfile', path)
            self.run_screen_cmd('logfile', 'flush', str(Config('server_manager/screen/log_flush_secs', 1)))
    
    cap_arbitrary_read = True
    cap_arbitrary_write = True
    cap_detachable = True
    cap_attachable = True
    cap_restartable = True
    
    bias = -float('inf') if shutil.which(Config('server_manager/screen/binary', 'screen')) is None else 10.0
class RConManager(BaseServerManager):
    __slots__ = ()
    _type = ('remote', 'passwd')
    def __init__(self):
        super().__init__()
        if RCONClient is None:
            raise ModuleNotFoundError('RCon module is required for RConManager!')
        if not Config('minecraft/rcon/enabled', False): raise RuntimeError('RCon is not enabled! (set it up in config: minecraft/rcon/enabled)')
        self.remote = f'{Config("minecraft/rcon/host", "127.0.0.1")}:{Config("minecraft/rcon/port", 25575)}'
        self.logger.warning(f'RCon remote: {self.remote} (can be set in config minecraft/rcon/)')
        self.rconpwd = Config('minecraft/rcon/password', None)
        if self.rconpwd is None:
            self.rconpwd = getpass('Enter RCon password >')
            self.logger.warning('RCon password can be permanently set in config minecraft/rcon/password')
        raise NotImplementedError

    cap_arbitrary_read = False
    cap_arbitrary_write = True
    cap_detachable = True
    cap_attachable = True
    cap_restartable = True
    
    @classmethod
    @property
    def bias(cls) -> float:
        if RCONClient is None: return -float('inf')
        if Config('minecraft/rcon/enabled', False):
            return 10
        return -255.0 #RConManager should be manually selected
class SelectManager(BasePopenManager):
    __slots__ = ()
    _type = ('select',)
    def __init__(self):
        super().__init__()
        raise NotImplementedError

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
    __slots__ = ()
    _type = ('manual', 'debug', 'interpreter',)
    def __init__(self):
        BaseServerManager.__init__(self)
    def start(self):
        import code
        code.interact('''Python Interpreter SM submode
    All locals and globals have been passed, A.E.:
    - RS is the RunServer instance
    - self is the {self.__class__} instance
    Use CTRL+D to exit subinterpreter, as exit() exits both the sub and main interpreters''', local=globals()+locals())
