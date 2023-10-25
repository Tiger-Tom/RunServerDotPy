#!/bin/python3

# The main program, or "entrypoint" #

#> Imports
import types
# RSModules
from .lib.rstypes import fbd, hooks, timer
from .lib import rs_config, rs_lineparser, rs_servmgr, rs_userio, rs_plugins
#</Imports

#> Header >/
class RunServer:
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
        # Load: 3
        'ServerManager', 'SM',
        'UserManager', 'UM',
        # Load: 4
        'TellRaw', 'TR',
        # Load: 5
        'ChatCommands', 'CC',
    )
    def __init__(self, bs: 'Bootstrapper'):
        # Init self & bootstrapper
        self.Bootstrapper = self.BS = bs
        self.logger = self.BS.root_logger
        self.logger.info('Initializing entrypoint')
        # Load: 0
        self.Types = self.T = types.SimpleNamespace()
        self.Types.FileBackedDict = fbd.FileBackedDict
        self.Types.Hooks = hooks.Hooks
        self.Types.Timer = timer.Timer
        # Load: 1
        self.__set_frommod(rs_config, {
            ('Config', 'C'): 'Config',
        })
        # Load: 2
        self.__set_frommod(rs_lineparser, {
            ('MCLang', 'L'): 'MCLang',
            ('LineParser', 'LP'): 'LineParser',
        })
        print('fixme::rs_plugins.py:Plugins:early_load_plugin()')
        # Load: 3
        self.__set_frommod(rs_servmgr, {
            ('ServerManager', 'SM'): 'ServerManager',
        })
        self.__set_frommod(rs_userio, {
            ('UserManager', 'UM'): 'UserManager',
        })
        # Load: 4
        self.__set_frommod(rs_userio, {
            ('TellRaw', 'TR'): 'TellRaw',
        })
        # Load: 5
        self.__set_frommod(rs_userio, {
            ('ChatCommands', 'CC'): 'ChatCommands',
        })
        # Load: 6
        print('fixme::rs_plugins.py:Plugins:early_load_plugin()')
    def __setup_frommod(self, module: types.ModuleType, keys: dict[tuple[str, str], str]):
        module.RunServer = module.RS = self
        for n,(l,s) in keys.items():
            setattr(self, l, getattr(module, n))
            setattr(self, s, getattr(self, l))
    def __call__(self):
        self.logger.info('Entrypoint starting')
