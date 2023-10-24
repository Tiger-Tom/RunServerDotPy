#!/bin/python3

#> Imports
import threading
import functools
# Types
import typing
from abc import ABC, abstractmethod
#</Imports

#> Header >/
class Timer:
    __slots__ = ()

    class BaseTimer(ABC):
        __slots__ = ('callable', 'length')

        def __init__(self, func: typing.Callable, length: float):
            self.callable = func
            self.length = length

        @abstractmethod
        def start(self) -> typing.Self: pass
        @abstractmethod
        def stop(self) -> typing.Self: pass
        cancel = stop
        @abstractmethod
        def reset(self) -> typing.Self: pass
    
    class After(BaseTimer):
        __slots__ = ('thread', 'lock', 'callable', 'length')
        
        def __init__(self, func: typing.Callable, time: float):
            super().__init__(func, time)
            self.thread = None
            self.lock = threading.RLock()
            
        @staticmethod
        def _locked(func: typing.Callable):
            @functools.wraps(func)
            def locked_func(self, *a, **kw):
                with self.lock:
                    return func(self, *a, **kw)
            return locked_func

        @_locked
        def _trigger(self):
            self.callable()
            self.thread = None
        @_locked
        def start(self):
            if self.thread is not None:
                raise RuntimeError(f'Timer {self} tried to start twice or did not clear properly')
            self.thread = threading.Timer(self.length, self._trigger)
            self.thread.start()
            return self
        @_locked
        def stop(self):
            if self.thread is None: return
            self.thread.cancel()
            self.thread = None
            return self
        cancel = stop
        @_locked
        def reset(self, start = False):
            self.cancel()
            self.thread = None
            if start: self.start()
            return self
    class Interval(After):
        __slots__ = ()

        def _trigger(self):
            with self.lock:
                super()._trigger()
                self.reset(True)

    @staticmethod
    def set_timer(timer_type: BaseTimer, func: typing.Callable, secs: float, activate_now: bool = True) -> BaseTimer:
        if activate_now: return timer_type(func, secs).start()
        return timer_type(func, secs)
    @staticmethod
    def clear(timer: BaseTimer) -> BaseTimer:
        return timer.stop()

    set_timeout = functools.partial(set_timer, After)
    set_interval = functools.partial(set_timer, Interval)
