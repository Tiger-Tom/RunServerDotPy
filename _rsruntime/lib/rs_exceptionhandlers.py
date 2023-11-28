#!/bin/python

#> Imports
# Formatting
import traceback
import time
# System
import sys
from pathlib import Path
import threading
# Types
import typing
import types
#</Imports

# RunServer Module
import RS
from RS.Util import Hooks

#> Header >/
class ExceptionHandlers:
    __slots__ = ('logger', 'exceptionhooks', 'unraisablehooks', 'threadexceptionhooks')

    exception_dump_path = Path('_exception.dump')
    unraisable_dump_path = Path('_unraisable.dump')
    threadexception_dump_path = Path('_thread_exception.dump')
    hookfail_dump_path = Path('_failed_hooks.dump')
    conffail_dump_path = Path('_failed_config_save.dump')

    def __init__(self):
        import logging
        self.logger = RS.logger.getChild('EH')
        self.exceptionhooks = Hooks.SingleHook()
        self.unraisablehooks = Hooks.SingleHook()
        self.threadexceptionhooks = Hooks.SingleHook()
        RS.BS.register_onclose(self.hookout)
        self.hookin()
    def hookin(self):
        self._hookin_hooktype(sys, 'excepthook')
        self._hookin_hooktype(sys, 'unraisablehook')
        self._hookin_hooktype(threading, 'excepthook')
    def _hookin_hooktype(self, module: types.ModuleType, name: str):
        self.logger.warning(f'Hooking in at {module.__name__}.{name}')
        setattr(module, name, getattr(self, f'_{module.__name__}__{name}'))
        self.logger.infop(f'{module.__name__}.{name}=._{module.__name__}__{name}')
    def hookout(self):
        self._hookout_hooktype(sys, 'excepthook')
        self._hookout_hooktype(sys, 'unraisablehook')
        self._hookout_hooktype(threading, 'excepthook')
    def _hookout_hooktype(self, module: types.ModuleType, name: str):
        self.logger.warning(f'Hooking out from {module.__name__}.{name}')
        setattr(module, name, getattr(module, f'__{name}__'))
        self.logger.infop(f'{module.__name__}.{name}={module.__name__}.__{name}__')
    def register_exception_hook(self, callback: typing.Callable[[typing.Type[BaseException], typing.Any | None, types.TracebackType], None]):
        self.exceptionhooks.register(callback)
    def register_unraisable_hook(self, callback: typing.Callable[['UnraisableHookArgs'], None]):
        self.unraisablehook.register(callback)
    def register_thread_exception_hook(self, callback: typing.Callable[[threading.ExceptHookArgs], None]):
        self.threadexceptionhooks.register(callback)
    def _try_hooks(self, hooks: Hooks.SingleHook, *args):
        try: hooks(*args)
        except Exception as e:
            msg = f'--EXCEPTION WHILST RUNNING HOOKS AT {time.ctime()}--\n{"".join(traceback.format_exception(e))}'
            with self.hookfail_dump_path.open('a') as f: f.write(msg)
            self.logger.fatal(msg)
    def _try_saveconfig(self):
        self.logger.warning('TRYING TO WRITEBACK CONFIG BEFORE FAIL...')
        try:
            RS.Config.writeback_dirty()
        except Exception as e:
            msg = f'--EXCEPTION WHILST SAVING CONFIG AT {time.ctime()}--\n{"".join(traceback.format_exception(e))}'
            with self.conffail_dump_path.open('a') as f: f.write(msg)
            self.logger.fatal(msg)
    def _sys__excepthook(self, type: typing.Type[BaseException], value: typing.Any | None, tback: types.TracebackType):
        msg = f'--UNCAUGHT EXCEPTION AT {time.ctime()}--\n{"".join(traceback.format_exception(type, value=value, tb=tback))}'
        with self.exception_dump_path.open('a') as f: f.write(msg)
        self.logger.fatal(msg)
        self._try_hooks(self.exceptionhooks, type, value, tback)
        self._try_saveconfig()
    def _sys__unraisablehook(self, unraisable: 'UnraisableHookArgs'):
        msg = f'--UNRAISABLE EXCEPTION ENCOUNTERED--\n {unraisable.err_msg or "Exception ignored in"}: {unraisable.object!r}\n{"".join(traceback.format_exception(unraisable.exc_type, value=unraisable.exc_value, tb=unraisable.exc_traceback))}'
        with self.unraisable_dump_path.open('a') as f: f.write(msg)
        self.logger.fatal(msg)
        self._try_hooks(self.unraisablehooks, unraisable)
        self._try_saveconfig()
    def _threading__excepthook(self, args: threading.ExceptHookArgs):
        msg = f'--UNCAUGHT EXCEPTION ENCOUNTERED IN THREAD {args.thread!r} AT {time.ctime()}--\n{"".join(traceback.format_exception(args.exc_type, value=args.exc_value, tb=args.exc_traceback))}'
        with self.threadexception_dump_path.open('a') as f: f.write(msg)
        self.logger.fatal(msg)
        self._try_hooks(threadexceptionhooks, args)
        self._try_saveconfig()
