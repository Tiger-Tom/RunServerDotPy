#!/bin/python

#> Imports
# Formatting
import traceback
import time
# System
import sys
from pathlib import Path
# Types
import typing
from types import TracebackType
#</Imports

# RunServer Module
import RS
from RS.Types import Hooks

#> Header >/
class ExceptionHandlers:
    __slots__ = ('logger', 'exceptionhooks', 'unraisablehooks')

    exception_dump_path = Path('_exception.dump')
    unraisable_dump_path = Path('_unraisable.dump')
    hookfail_dump_path = Path('_failed_hooks.dump')
    
    def __init__(self):
        import logging
        self.logger = RS.logger.getChild('ExceptionHandlers')
        self.exceptionhooks = Hooks.SingleHook()
        self.unraisablehooks = Hooks.SingleHook()
        sys.excepthook = self._exception_caught
        sys.unraisablehook = self._unraisable_caught
    def register_exception_hook(self, callback: typing.Callable[[typing.Type[BaseException], typing.Any | None, TracebackType], None]):
        self.exceptionhooks.register(callback)
    def register_unraisable_hook(self, callback: typing.Callable[['UnraisableHookArgs'], None]):
        self.unraisablehook.register(callback)
    def _exception_caught(self, type, value, tback):
        msg = f'--UNCAUGHT EXCEPTION AT {time.ctime()}--\n{"".join(traceback.format_exception(type, value=value, tb=tback))}'
        with self.exception_dump_path.open('a') as f: f.write(msg)
        self.logger.fatal(msg)
        try: self.exceptionhooks(type, value, tback)
        except Exception as e:
            msg = f'--EXCEPTION WHILST RUNNING EXCEPTIONHOOKS AT {time.ctime()}--\n{"".join(traceback.format_exception(e))}'
            with self.hookfail_dump_path.open('a') as f: f.write(msg)
            self.logger.fatal(msg)
    def _unraisable_caught(self, unraisable):
        msg = f'--UNRAISABLE EXCEPTION ENCOUNTERED--\n {unraisable.err_msg or "Exception ignored in"}: {unraisable.object!r}\n{"".join(traceback.format_exception(unraisable.exc_type, value=unraisable.exc_value, tb=unraisable.exc_traceback))}'
        with self.unraisable_dump_path.open('a') as f: f.write(msg)
        self.logger.fatal(msg)
        try: self.unraisablehooks(unraisable)
        except Exception as e:
            msg = f'--EXCEPTION WHILST RUNNING UNRAISABLEHOOKS AT {time.ctime()}--\n{"".join(traceback.format_exception(e))}'
            with self.hookfail_dump_path.open('a') as f: f.write(msg)
            self.logger.fatal(msg)
