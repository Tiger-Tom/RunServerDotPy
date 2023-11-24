#!/bin/python3

# The main program, or "entrypoint" #

#> Imports
import types
import sys
import importlib
import time
from types import SimpleNamespace
# RSModules
from . import util
#</Imports

#> Header >/
class RunServer(types.ModuleType):
    __slots__ = (
        'logger',
        # Load: -1
        'Bootstrapper', 'BS',
        # Load: 0
        'Util', 'U',
        'Flags', 'F',
        # Load: 1
        'Config', 'C',
        'ExceptionHandlers', 'EH',
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
        self.logger.infop('Initializing entrypoint')
        # Add self to sys.modules
        if 'RS' in sys.modules:
            self.logger.fatal('RS already exists in sys.modules, continuing by overwriting but this may have consequences!')
        sys.modules['RS'] = self
        # Setup perf counter
        pc = util.PerfCounter(sec='', secs='')
        self.logger.debug(f'start@T+{pc}')
        # Load: 0
        self.logger.debug(f'start:load_0@T+{pc}')
        sys.modules['RS.Util'] = self.Util = self.U = util
        self.Flags = self.F = SimpleNamespace()
        self.F.force_restart = False
        self.F.force_no_restart = False
        self.logger.debug(f'finish:load_0@T+{pc}')
        # Load: 1
        self.logger.debug(f'start:load_1@T+{pc}')
        self.__setup_frommod('rs_config', {
            ('Config', 'C'): 'Config',
        })
        self.__setup_frommod('rs_exceptionhandlers', {
            ('ExceptionHandlers', 'EH'): 'ExceptionHandlers',
        })
        self.logger.debug(f'finish:load_1@T+{pc}')
        # Load: 2
        self.logger.debug(f'start:load_2@T+{pc}')
        self.__setup_frommod('rs_lineparser', {
            ('MCLang', 'L'): 'MCLang',
            ('LineParser', 'LP'): 'LineParser',
        })
        self.__setup_frommod('rs_plugins', {
            ('PluginManager', 'PM'): 'PluginManager',
        })
        self.PM.early_load_plugins()
        self.logger.debug(f'finish:load_2@T+{pc}')
        # Load: 3
        self.logger.debug(f'start:load_3@T+{pc}')
        self.__setup_frommod('rs_servmgr', {
            ('ServerManager', 'SM'): 'ServerManager',
        }, call=False)
        self.__setup_frommod('rs_userio', {
            ('UserManager', 'UM'): 'UserManager',
        })
        self.logger.debug(f'finish:load_3@T+{pc}')
        # Load: 4
        self.logger.debug(f'start:load_4@T+{pc}')
        self.__setup_frommod('rs_userio', {
            ('TellRaw', 'TR'): 'TellRaw',
        }, call=False)
        self.logger.debug(f'finish:load_4@T+{pc}')
        # Load: 5
        self.logger.debug(f'start:load_5@T+{pc}')
        self.__setup_frommod('rs_userio', {
            ('ChatCommands', 'CC'): 'ChatCommands',
        })
        self.logger.debug(f'finish:load_5@T+{pc}')
        # Load: 6
        self.logger.debug(f'start:load_6@T+{pc}')
        self.Config.sync()
        self.PM.load_plugins()
        self.logger.debug(f'finish:load_6@T+{pc}')
        # Final log
        self.logger.debug(f'finish@T+{pc}')
    def __setup_frommod(self, module: str, keys: dict[tuple[str, str], str], *, call: bool = True):
        pc = util.PerfCounter(sec='', secs='')
        self.logger.info(f'Importing module: .lib.{module} [T+{pc}]')
        m = importlib.import_module(f'.lib.{module}', __package__)
        self.logger.info(f'.lib.{module} imported into {m} [T+{pc}]')
        for (l,s),n in keys.items():
            setattr(self, l, getattr(m, n)() if call else getattr(m, n))
            setattr(self, s, getattr(self, l))
            self.logger.debug(f'{l} = {s} = {module}.{n} [T+{pc}]')
    def __call__(self):
        self.logger.infop('Entrypoint starting')
        # Instantiate ServerManager
        self.ServerManager = self.SM = self.ServerManager()
        # Start plugins
        self.PM.start()
        # Start server
        while True:
            self.SM.start()
            if self.F.force_no_restart or ((not self.F.force_restart) and (not self.C('server_manager/autorestart/restart', True))): break
            if not self.SM.cap_restartable:
                self.logger.fatal(f'A restart was requested, but the ServerManager (type {self.SM.type}) does not support restarting')
                break
            try:
                for s in range(self.C('server_manager/autorestart/delay', 5), 0, -1):
                    print(f'Restarting in {s} second{"" if s == 1 else "s"}, issue KeyboardInterrupt (usually CTRL+C) to cancel')
                    time.sleep(1)
            except KeyboardInterrupt:
                print('Restart aborted')
                break
