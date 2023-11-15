#!/bin/python3

#> Imports
from threading import RLock
# Types
import typing
from functools import wraps
#</Imports

#> Header >/
__all__ = ('LockedResource', 'locked')

class LockedResource:
    __slots__ = ('lock',)
    def __init__(self, *, lock_class=RLock):
        self.lock = lock_class()
def locked(func: typing.Callable):
    @wraps(func)
    def locked_func(self: LockedResource, *args, **kwargs):
        with self.lock:
            return func(self, *args, **kwargs)
    return locked_func
