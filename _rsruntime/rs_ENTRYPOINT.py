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
        'MinecraftManager', 'MC',
        # Load: 3
        'MCLang', 'L',
        'LineParser', 'LP',
        'PluginManager', 'PM',
        # Load: 4
        'ServerManager', 'SM',
        'UserManager', 'UM',
        # Load: 5
        'TellRaw', 'TR',
        # Load: 6
        'ChatCommands', 'CC',
        # Load: 8
        'Convenience', '_',
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
        tld = util.TimedLoadDebug(self.logger.info)
        # Load: 0
        with tld:
            sys.modules['RS.Util'] = self.Util = self.U = util
            self.Flags = self.F = SimpleNamespace()
            self.F.force_restart = False
            self.F.force_no_restart = False
        # Load: 1
        with tld:
            from .lib import rs_config
            self.__setup_frommod(rs_config, {
                ('Config', 'C'): 'Config',
            })
            from .lib import rs_exceptionhandlers
            self.__setup_frommod(rs_exceptionhandlers, {
                ('ExceptionHandlers', 'EH'): 'ExceptionHandlers',
            })
        # Load: 2
        with tld:
            from .lib import rs_mcmgr
            self.__setup_frommod(rs_mcmgr, {
                ('MinecraftManager', 'MC'): 'MinecraftManager',
            })
        # Load: 3
        with tld:
            from .lib import rs_lineparser
            self.__setup_frommod(rs_lineparser, {
                ('MCLang', 'L'): 'MCLang',
                ('LineParser', 'LP'): 'LineParser',
            })
            from .lib import rs_plugins
            self.__setup_frommod(rs_plugins, {
                ('PluginManager', 'PM'): 'PluginManager',
            })
            self.PM.early_load_plugins()
        # Load: 4
        with tld:
            from .lib import rs_servmgr
            self.__setup_frommod(rs_servmgr, {
                ('ServerManager', 'SM'): 'ServerManager',
            }, call=False)
            from .lib import rs_usermgr
            self.__setup_frommod(rs_usermgr, {
                ('UserManager', 'UM'): 'UserManager',
            })
        # Load: 5
        with tld:
            from .lib import rs_userio
            self.__setup_frommod(rs_userio, {
                ('TellRaw', 'TR'): 'TellRaw',
            }, call=False)
        # Load: 6
        with tld:
            self.__setup_frommod(rs_userio, {
                ('ChatCommands', 'CC'): 'ChatCommands',
            })
        # Load: 7
        with tld:
            from .lib import rs_convenience
            self.Convenience = self._ = rs_convenience
        # Final log
        tld.final()

    def __setup_frommod(self, module: str, keys: dict[tuple[str, str], str], *, call: bool = True):
        pc = util.PerfCounter(sec='', secs='')
        self.logger.info(f'Setting up from module: {module} [T+{pc}]')
        for (l,s),n in keys.items():
            setattr(self, l, getattr(module, n)() if call else getattr(module, n))
            setattr(self, s, getattr(self, l))
            self.logger.debug(f'{l} = {s} = {module}.{n} [T+{pc}]')

    def __call__(self):
        self.logger.infop('Entrypoint starting')
        if self.BS.is_dry_run:
            self.logger.fatal('Is a dry run')
            return
        # Second stage init
        self.logger.warning('Running second-stage initialization')
        util.TimedLoadDebug.foreach(self.logger.info,
            ('MinecraftManager', self.MinecraftManager.init2),
            ('MCLang', self.MCLang.init2),
            ('LineParser', self.LineParser.init2),
            ('UserManager', self.UserManager.init2),
            ('ChatCommands', self.ChatCommands.init2),
        )
        # Instantiate ServerManager
        self.ServerManager = self.SM = self.ServerManager()
        # Initialize plugins
        self.PM.load_plugins()
        # Start plugins
        self.PM.start()
        # Main server loop
        while True:
            # Start server
            self.SM.start()
            # Handle forced no-restarts
            if self.F.force_no_restart or ((not self.F.force_restart) and (not self.C('server_manager/autorestart/restart', True))): break
            # Handle impossible restarts
            if not self.SM.cap_restartable:
                self.logger.fatal(f'A restart was requested, but the ServerManager (type {self.SM.type}) does not support restarting')
                break
            # Prompt user to cancel restart (if needed)
            try:
                for s in range(self.C('server_manager/autorestart/delay', 5), 0, -1):
                    print(f'Restarting in {s} second{"" if s == 1 else "s"}, issue KeyboardInterrupt (usually CTRL+C) to cancel')
                    time.sleep(1)
            except KeyboardInterrupt:
                print('Restart aborted')
                break
            # Restart plugins
            self.PM.restart()
