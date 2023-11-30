#!/bin/python3

#> Imports
from threading import RLock
import warnings
# Types
import typing
from types import SimpleNamespace
from collections import namedtuple
from functools import wraps
from contextlib import AbstractContextManager
#</Imports

#> Header >/
__all__ = (
    'LockedResource', 'locked',
    'basic', 'b',
    'cls',
    'etc',
    'func_decors',
    'superclasses',
    'cls_decors',
)
#naming convention:
#long = thing.__qualname__
#short = \
#      long.replace('_', '').replace('class', 'cls').replace('locked', 'lockd') if long.is_lower() \
#      else ''.join(c for c in long if c.isupper())
_basic        = namedtuple('basic',        ('LockedResource','LR', 'locked','lockd'))
_cls          = namedtuple('cls',          ('LockedClass','LC', 'classlocked','clslockd', 'iclasslocked','iclslockd'))
_etc          = namedtuple('etc',          ('locked_by','lockdby'))
_func_decors  = namedtuple('func_decors',  ('locked','lockd', 'classlocked','clslockd', 'iclasslocked','iclslockd', 'locked_by','lockdby'))
_superclasses = namedtuple('superclasses', ('LockedResource','LR'))
_cls_decors   = namedtuple('cls_decors',   ('LockedClass','LC'))
# Classes
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
    def __init__(self, *, lock_class: AbstractContextManager | typing.Callable[[None], AbstractContextManager] = RLock):
        self.lock = lock_class()
## Class decorators
def LockedClass(lock_class: AbstractContextManager = RLock, *, I_KNOW_WHAT_IM_DOING: bool = False):
    '''
        Adds a "classlock" class variable
        This should be used in tandem with either the @classlocked or @iclasslocked decorators
            see help(classlockd) or help(iclasslocked) for real demo code
        Note that, unless you pass I_KNOW_WHAT_IM_DOING=True, lock_class is instantiated immediately in order to check if it is an instance of AbstractContextManager
            This is to try to help emit a warning if LockedClass is used on a user class without being called (@LockedClass instead of @LockedClass())
            The lock_class must be instantiated to check, as threading.RLock and threading.Lock are actually functions
            I_KNOW_WHAT_IM_DOING=True disables both the immediate instantiation of lock_class, the isinstance check, and the warning
        lock_class is the type of lock (or really any context manager will do) to use (defaults to RLock)
        Short demo code:
            @LockedClass()
            class Locked: ...
        or, to use a custom lock:
            @LockedClass(threading.Semaphore)
            class CustomLocked: ...
    '''
    if (not I_KNOW_WHAT_IM_DOING) and (not isinstance(lock_class(), AbstractContextManager)):
        warnings.warn(f'LockedClass was used with lock_class {lock_class}, which (when instantiated) is not an instance of AbstractContextManager. Perhaps you meant to use `@LockedClass()`?', SyntaxWarning)
    def ClassLocker(cls: typing.Type):
        cls.classlock = lock_class()
        return cls
    return ClassLocker
# Function decorators
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
def classlocked(func: typing.Callable):
    '''
        Similar to @locked, but uses cls's .classlock attribute
        Does NOT imply classmethod (use @iclasslocked if you want to do that)
        Meant to be used with the @LockedClass class decorator:
            @LockedClass
            class DemoLockedClass:
                @classmethod # note: @classmethod BEFORE @classlocked
                @classlocked # could both be replaced by a single @iclasslocked
                def test_lock(cls):
                    print("class lock acquired!")
                @classlocked
                def test_lock_2(self):
                    print("class lock acquired on non-classmethod!")
    '''
    @wraps(func)
    def locked_func(self_or_cls: LockedClass | typing.Type[LockedClass], *args, **kwargs):
        with self_or_cls.classlock:
            return func(self_or_cls, *args, **kwargs)
    return locked_func
def iclasslocked(func: typing.Callable):
    '''
        Is the same as @classlocked (it even calls it), but also wraps the method in classmethod
        Meant to be used with @LockedClass:
            @LockedClass()
            class Locked:
                @iclasslocked
                def classlocked_classmethod(cls):
                    print("class lock acquired!")
    '''
    return classmethod(classlocked(func))
## Function decorator... decorator?
def locked_by(lock: AbstractContextManager):
    def func_locker(func: typing.Callable):
        @wraps(func)
        def locked_func(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return locked_func
    return func_locker

# Assign to namespaces
for c in (_basic, _cls, _etc, _func_decors, _superclasses, _cls_decors):
    globals()[c.__qualname__] = c._make((o for ol in ((globals()[f], globals()[f]) for f in c._fields[::2]) for o in ol))
b = basic
