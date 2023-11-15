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
    '''
        Adds a "lock" parameter to class instances (and slots!)
        This should be used in tandem with the @locked decorator:
            class DemoLocked(LockedResource): # note subclass
                def __init__(self):
                    super().__init__() # note super init, needed to setup .lock
                    print("initialized!")
                @locked # note decorator
                def test_lock(self):
                    print("lock acquired!")
    '''
    __slots__ = ('lock',)
    def __init__(self, *, lock_class=RLock):
        self.lock = lock_class()
def locked(func: typing.Callable):
    '''
        Waits to acquire the method's self's .lock attribute (uses "with")
        This should be used in tandem with the LockedResource superclass:
            class DemoLocked(LockedResource): # note subclass
                def __init__(self):
                    super().__init__() # note super init, needed to setup .lock
                    print("initialized!")
                @locked # note decorator
                def test_lock(self):
                    print("lock acquired!")
    '''
    @wraps(func)
    def locked_func(self: LockedResource, *args, **kwargs):
        with self.lock:
            return func(self, *args, **kwargs)
    return locked_func
