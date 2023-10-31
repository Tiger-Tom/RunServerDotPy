#!/bin/python3

# The main program, or "entrypoint" #

#> Imports
import types
import sys
import importlib
# RSModules
from .lib.rstypes import fbd, hooks, locked_resource, timer
#</Imports

#> Header >/
class RunServer(types.ModuleType):
    __slots__ = (
        'logger',
        # Load: -1
        'Bootstrapper', 'BS',
        # Load: 0
        'Types', 'T',
        # Load: 1
        'Config', 'C',
        # Load: 2
        'MCLang', 'L',
        'LineParser', 'LP',
        'PluginManager', 'PM',
        # Load: 3
        'ServerManager', 'SM',
        'UserManager', 'UM',
        # Load: 4
        'TellRaw', 'TR',
        # Load: 5
        'ChatCommands', 'CC',
    )
    def __init__(self, bs: 'Bootstrapper'):
        super().__init__('RS')
        self.__file__ = __file__
        self.__package__ = 'RS'
        self.__path__ = []
        # Init self & bootstrapper
        self.Bootstrapper = self.BS = bs
        self.logger = self.BS.root_logger
        self.logger.info('Initializing entrypoint')
        # Add self to sys.modules
        if 'RS' in sys.modules:
            self.logger.fatal('RS already exists in sys.modules, continuing by overwriting but this may have consequences!')
        sys.modules['RS'] = self
        # Load: 0
        self.Types = self.T = types.SimpleNamespace()
        self.Types.FileBackedDict = fbd.FileBackedDict
        self.Types.Hooks = hooks.Hooks
        self.Types.LockedResource = locked_resource.LockedResource
        self.Types.locked = locked_resource.locked
        self.Types.Timer = timer.Timer
        sys.modules['RS.Types'] = self.Types
        # Load: 1
        self.__setup_frommod('rs_config', {
            ('Config', 'C'): 'Config',
        })
        # Load: 2
        self.__setup_frommod('rs_lineparser', {
            ('MCLang', 'L'): 'MCLang',
            ('LineParser', 'LP'): 'LineParser',
        })
        self.__setup_frommod('rs_plugins', {
            ('PluginManager', 'PM'): 'PluginManager',
        })
        print('fixme::rs_plugins.py:Plugins:early_load_plugin()')
        # Load: 3
        self.__setup_frommod('rs_servmgr', {
            ('ServerManager', 'SM'): 'ServerManager',
        }, call=False)
        self.__setup_frommod('rs_userio', {
            ('UserManager', 'UM'): 'UserManager',
        })
        # Load: 4
        self.__setup_frommod('rs_userio', {
            ('TellRaw', 'TR'): 'TellRaw',
        }, call=False)
        # Load: 5
        self.__setup_frommod('rs_userio', {
            ('ChatCommands', 'CC'): 'ChatCommands',
        })
        # Load: 6
        self.Config.sync_all()
        print('fixme::rs_plugins.py:Plugins:load_plugins()')
    def __setup_frommod(self, module: str, keys: dict[tuple[str, str], str], *, call: bool = True):
        self.logger.info(f'Importing module: .lib.{module}')
        m = importlib.import_module(f'.lib.{module}', __package__)
        self.logger.info(f'.lib.{module} imported into {m}')
        for (l,s),n in keys.items():
            setattr(self, l, getattr(m, n)() if call else getattr(m, n))
            setattr(self, s, getattr(self, l))
    def __call__(self):
        self.logger.info('Entrypoint starting')
        self.ServerManager = self.SM = self.ServerManager()
        self.Config.stop_autosync()
        self.Config.sync_all()
