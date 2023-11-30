#!/bin/python3

#> Imports
import threading
import functools
# Types
import typing
from abc import ABC, abstractmethod
from .locked_resource import LockedResource, locked
#</Imports

#> Header >/
__all__ = ('Timer',)

class Timer:
    __slots__ = ()

    class BaseTimer(ABC, LockedResource):
        __slots__ = ('callable', 'length')

        def __init__(self, func: typing.Callable, length: float, *, lock_class=threading.RLock):
            super().__init__(lock_class=lock_class)
            self.callable = func
            self.length = length

        @abstractmethod
        @locked
        def start(self) -> typing.Self: pass
        @abstractmethod
        @locked
        def stop(self) -> typing.Self: pass
        cancel = stop
        @abstractmethod
        @locked
        def reset(self) -> typing.Self: pass

    class After(BaseTimer):
        __slots__ = ('thread', 'callable', 'length')

        def __init__(self, func: typing.Callable, time: float):
            super().__init__(func, time)
            self.thread = None

        @locked
        def _trigger(self):
            self.callable()
            self.thread = None
        @locked
        def start(self):
            if self.thread is not None:
                raise RuntimeError(f'Timer {self} tried to start twice or did not clear properly')
            self.thread = threading.Timer(self.length, self._trigger)
            self.thread.daemon = True
            self.thread.start()
            return self
        @locked
        def stop(self):
            if self.thread is None: return
            self.thread.cancel()
            self.thread = None
            return self
        cancel = stop
        @locked
        def reset(self, start = False):
            self.stop()
            if start: self.start()
            return self
        @locked
        def is_alive(self) -> bool:
            if self.thread is None: return False
            return self.thread.is_alive()
    class Interval(After):
        __slots__ = ()

        @locked
        def _trigger(self):
            super()._trigger()
            self.reset(True)

    @staticmethod
    def set_timer(timer_type: type['Timer.BaseTimer'], func: typing.Callable, secs: float, activate_now: bool = True) -> 'Timer.BaseTimer':
        if activate_now: return timer_type(func, secs).start()
        return timer_type(func, secs)
    @staticmethod
    def clear(timer: BaseTimer) -> BaseTimer:
        return timer.stop()

    set_timeout = functools.partial(set_timer, After)
    set_interval = functools.partial(set_timer, Interval)
