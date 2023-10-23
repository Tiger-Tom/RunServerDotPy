#!/bin/python

#> Imports
import os
import traceback
from collections.abc import Callable
from dataclasses import dataclass
import copy
import pathlib
import json
import sched
import threading
import time
#</Imports

#> SharedState Class
class SharedState: # Auto-nesting data container
    def __repr__(self):
        return f'{self.__class__.__name__}({", ".join(f"{k}={repr(v)}" for k,v in self.__dict__.items() if (not callable(k)) and (not k.startswith("__")) and (not k.endswith("__")))})'
    def map(self, oneach=lambda x: x):
        mapped = {}
        for k,v in self.__dict__.items():
            if callable(k) or (k.startswith('__') and k.endswith('__')):
                continue
            if isinstance(v, self.__class__):
                mapped[k] = v.map()
                continue
            mapped[k] = oneach(v)
        return mapped
    def __getattribute__(self, attr):
        try: return super().__getattribute__(attr)
        except AttributeError:
            self.__dict__[attr] = self.__class__()
            return super().__getattribute__(attr)
    def __setattribute__(self, attr, newval):
        super().__setattribute__(attr, newval)
    def get(self, key, default=None):
        if '.' in key:
            subname,subkey = key.split('.', 1)
            if subname not in self.__dict__:
                self.__dict__[subname] = self.__class__()
            return self.__dict__[subname].get(subkey, default)
        if key not in self.__dict__: return default
        return self.__dict__[key]
    def set(self, key, val):
        if '.' in key:
            subname,subkey = key.split('.', 1)
            if subname not in self.__dict__:
                self.__dict__[subname] = self.__class__()
            self.__dict__[subname].set(subkey, val)
            return
        self.__dict__[key] = val
    def update(self, kwargs: dict[str, ...]):
        for k,v in kwargs.items():
            self.set(k, v)
        
#</SharedState Class
#> Passedvars Class
@dataclass
class PassedVars:
    console_id: str
    mgr: 'ModuleHandler'
    ChatCommand: Callable[[str, int, str, str], Callable[[Callable[[str, tuple[...]], ...]], Callable[[str, tuple[...]], ...]]]
    TimedFunction: Callable[[bool, int, tuple, dict, int], Callable[[Callable[[], ...]], Callable[[], ...]]]
    RegisterUpdateChecker: Callable[[str, float], None]
    prefix: str
    tellraw: Callable[[str, str], None]
    run: Callable[[str], str]
    commands: dict[str, dict[str, ...]]
    sharedState: SharedState
    logger: 'Logger'
    log: Callable[[str, str], None]
    LineParser: 'MCParser'
    programConfig: dict[str, ...]
    uptime: tuple[float, float]
#</Passedvars Class

#> Module Handler
class ModuleHandler:
    '''Loads modules from the command path, as well as providing a general interface to looping and non-looping delayed/timed functions. Globals passed are anything in passed_globals, as well as Passed[PassedVars] (overwriting anything of the same name in passed_globals), which contains:
        console_id: str
        mgr: 'ModuleHandler'
        ChatCommand: Callable[[str, int, str, str], Callable[[Callable[[str, tuple[...]], ...]], Callable[[str, tuple[...]], ...]]]
        TimedFunction: Callable[[bool, int, tuple, dict, int], Callable[[Callable[[], ...]], Callable[[], ...]]]
        RegisterUpdateChecker: Callable[[str, float], None]
        prefix: str
        tellraw: Callable[[str, str], None]
        run: Callable[[str], str]
        commands: dict[str, dict[str, ...]]
        sharedState: SharedState
        logger: 'Logger'
        log: Callable[[str, str], None]
        LineParser: MCParser
        programConfig: dict[str, ...]
        uptime: tuple[float, float]
    Global variable "__" is also set to Passed, allowing for a more concise text
    __version__ is set to the software version'''
    def __init__(self, commandsPath: str, passed_globals: dict[str, ...], chatcommand_prefix: str, tellraw_command: Callable[[str, str], None], run_command: Callable[[str], None], logger: Callable[[str, str], None], parser: 'MCParser', programConfig: dict[str, ...], uptimeProgram: float, uptimeServer: float, version: tuple[int, int, int]):
        self.superusers = ()
        self.commands = {}
        self.server_identifier = '\0_from_console'
        self.chatcommand_prefix = chatcommand_prefix
        self.tellraw = tellraw_command
        self.run_command = run_command
        self.scheduler = sched.scheduler()
        self.logger = logger
        self.moduleSharedState = SharedState()
        self.passed_globals = copy.deepcopy(passed_globals)
        self.passed_globals['Passed'] = PassedVars(
            console_id = '\0_from_console',
            mgr = self,
            ChatCommand = self.ChatCommand,
            TimedFunction = self.TimedFunction,
            RegisterUpdateChecker = self.RegisterUpdateChecker,
            prefix = self.chatcommand_prefix,
            tellraw = self.tellraw,
            run = self.run_command,
            commands = self.commands,
            sharedState = self.moduleSharedState,
            logger = self.logger,
            log = self.logger.log,
            LineParser = parser,
            programConfig = programConfig,
            uptime = (uptimeProgram, uptimeServer),
        )
        self.passed_globals['__'] = self.passed_globals['Passed']
        self.passed_globals['__version__'] = version
        self._working_module = None
        self.exec_modules(commandsPath)
        self.schedulerKA = True
        self.schedulerThread = threading.Thread(target=self.runScheduler, args=(self.scheduler,), daemon=True)
        self.schedulerThread.start()
    @staticmethod
    def discover_modules(commandsPath: str):
        return pathlib.Path(commandsPath).rglob('*.rspy')
    def exec_modules(self, commandsPath: str):
        print(f'Discovering modules in {commandsPath}')
        mods = sorted(self.discover_modules(commandsPath), key=str)
        print(f'Discovered {len(mods)} module(s)')
        loaded = 0
        for i in mods:
            print(f'Running {i}')
            self.logger.log('module_load', f'Attempting to load module {i}')
            try:
                with open(i) as f:
                    self.exec_module(f.read(), str(i))
                loaded += 1
                print(f'Successfully ran {i}')
                self.logger.log('module_load', f'Successfully loaded module {i}')
            except Exception as e:
                print(f'ERROR: Could not initialize {i}: {e}\nSkipping module')
                self.logger.log('module_load', f'Attempting to load module {i} failed: {e}')
        if len(mods):
            print(f'Successfully loaded {loaded}/{len(mods)} modules ({loaded*1000//len(mods)/10}%)')
            self.logger.log('module_load', f'Loaded {loaded}/{len(mods)} modules ({loaded*1000//len(mods)/10}%)')
    def exec_module(self, module: str, module_name: str):
        self._working_module = module_name
        globs = self.passed_globals
        exec(module, globs)
        self._working_module = None
        return globs
    def run_ccommand(self, user: str, command: str, args=(), overridden_perm=None):
        if command.lower() not in self.commands:
            if user == self.server_identifier:
                print(f'Error: command {command} not recognized. Try "{self.chatcommand_prefix}help"?')
            else:
                self.tellraw(user, f'{{"text":"Error: command {command} not recognized. Try \\"{self.chatcommand_prefix}help\\"?","bold":true,"color":"red","insertion":"{self.chatcommand_prefix}help"}}')
            return
        try:
            self.commands[command.lower()]['callable'](user, overridden_perm=overridden_perm, *args)
        except Exception as e:
            if user == self.server_identifier:  
                print(traceback.format_exc())
                print(f'Error: command {command} failed with "{e}". Try "{self.chatcommand_prefix}help {command}"?')
            else:
                self.tellraw(user, f'{{"text":{json.dumps(traceback.format_exc())},"color":"red"}}')
                self.tellraw(user, f'{{"text":"Error: command {command} failed with \\"{e}\\". Try \\"{self.chatcommand_prefix}help {command}\\"?","bold":true,"color":"red","insertion":"{self.chatcommand_prefix}help {command}"}}')
    def runScheduler(self, scheduler):
        while self.schedulerKA:
            scheduler.run()
            if scheduler.empty(): time.sleep(5)
    def ChatCommand(self, command_name: str, level=0, help_short='Default short help string (CHANGE THIS!)', help_long='Default long help string (CHANGE THIS!)') -> Callable[[Callable[[str, tuple[...]], ...]], Callable[[str, tuple[...]], ...]]:
        '''level: 0 for users, 1 for sudoers, 2+ for root'''
        def inner(function: Callable[[str, tuple[...]], ...]):
            def wrapper(user, *args, overridden_perm: int | None):
                override = ((overridden_perm is not None) and (overridden_perm >= level))
                if user != self.server_identifier:
                    if (level > 0) and not override:
                        if user not in self.superusers:
                            self.logger.log('chat_commands', f'{user} attempting to run {command_name} (level {level} command) failed ({user} is not a superuser)')
                            return f'{user} is not a superuser, cannot run {command_name} (level {level} command)'
                        if level > 1:
                            self.logger.log('chat_commands', f'Superuser {user} attempting to run {command_name} (level {level} command) failed ({user} is not console)')
                            return f'Superuser {user} is not allowed to run {command_name} (level {level} command)'
                    self.logger.log('chat_command', f'{user} running {command_name} (level {level} command)')
                function(user, *args)
            self.commands[command_name.lower()] = {
                'source': self._working_module,
                'level': level,
                'callable': wrapper,
                'help': (help_short, help_long),
            }
            return function
        return inner
    def TimedFunction(self, loop: bool, secs: int, args=(), kwargs={}, priority=0):
        def inner(function: Callable[[], ...]):
            def looped(*args, **kwargs):
                self.logger.log('timer_functions', int(time.time()), f'Looped function {function.__qualname__} at {id(function)} ran after specified {secs} second{"s" if secs != 1 else ""} of delay')
                function(*args, **kwargs)
                self.scheduler.enter(secs, priority, looped, args, kwargs)
            def not_looped(*args, **kwargs):
                self.logger.log('timer_functions', f'Delayed function {function.__qualname__} at {id(function)} ran once after specified {secs} second{"s" if secs != 1 else ""} of delay')
            self.logger.log('timer_functions', f'Function {function.__qualname__} at {id(function)} will be {"looped every" if loop else "ran after"} {secs} second{"s" if secs != 1 else ""}')
            chosen = looped if loop else function
            self.scheduler.enter(secs, priority, looped, args, kwargs)
            return function
        return inner
    def RegisterUpdateChecker(self, url: str, cver: float):
        raise NotImplemented

def testInstance():
    return ModuleHandler('./RSModules/', {}, '!', lambda u,m: print(f'tellraw {u} {m}'), lambda c: print(f'run_command {c}'), lambda c,m: print(f'log ({c}) {m}'))
