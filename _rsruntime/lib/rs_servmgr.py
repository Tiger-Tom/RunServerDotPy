#!/bin/python3

#> Imports
from pathlib import Path
import shlex
from getpass import getpass
# Types
import typing
from abc import ABC, abstractmethod, abstractproperty
# Manager-specific modules
try: from rcon.source import Client as RCONClient
except ModuleNotFoundError: RCONClient = None
try: import screenutils
except ModuleNotFoundError: screenutils = None
#</Imports

# RunServer Module
import RS
from RS import Config, LineParser
from RS.Types import Hooks

#> Header >/
# Base classes
class BaseServerManager(ABC):
    __slots__ = ('logger', 'hooks')
    def __init__(self):
        self.logger = RS.logger.getChild(self.__class__.__qualname__)
        self.hooks = Hooks.SingleHook()
        self.hooks.register(print)
        self.hooks.register(LineParser.handle_line)

    # Non-abstract methods
    @classmethod
    def _bias_config(cls) -> float:
        return Config(f'override/server_manager/bias_mod/{cls.__qualname__}', 0.0) + \
               (-float('inf') if Config(f'server_manager/blacklist/{cls.__qualname__}', False) else 0.0) + \
               (100.0 if Config(f'server_manager/prefer/{cls.__qualname__}', False) else 0.0)
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
    is_dummy: bool = False
    
        
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

            
        
# Implementations
class ScreenManager(BaseServerManager):
    __slots__ = ()
    _type = ('screen',)
    def __init__(self):
        super().__init__()
        if screenutils is None:
            raise ModuleNotFoundError('Screenutils module is required for ScreenManager!')
        raise NotImplementedError
    
    cap_arbitrary_read = True
    cap_arbitrary_write = True
    cap_detachable = True
    cap_attachable = True
    cap_restartable = True
    
    bias = -float('inf') if screenutils is None else 10.0
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

    is_dummy = True
    
    bias = -50.0

# Manager
class ServerManager:
    server_manager_types = {ScreenManager, RConManager, SelectManager, DummyServerManager}
    def __new__(cls):
        RS.logger.getChild('ServerManager').debug(f'Instantiating server manager; preferred order: {tuple(f"{c.__qualname__}:<{c.type}>,[{c.bias}+{c._bias_config()}]" for c in cls.preferred_order())}')
        return cls.preferred_order()[0]()
    @classmethod
    def register(cls, manager_type: typing.Type[BaseServerManager]):
        cls.server_manager_types.add(manager_type)
    @classmethod
    def preferred_order(cls) -> list[typing.Type[BaseServerManager]]:
        return sorted(cls.server_manager_types, key=lambda t: t.bias+t._bias_config(), reverse=True)
ServerManager.BaseServerManager = BaseServerManager
ServerManager.BasePopenManager = BasePopenManager
ServerManager.ScreenManager = ScreenManager
ServerManager.RConManager = RConManager
ServerManager.SelectManager = SelectManager