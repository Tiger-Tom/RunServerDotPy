[`_rsruntime/ShaeLib/concurrency/locked_resource.py`](/_rsruntime/ShaeLib/concurrency/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/concurrency/locked_resource/RunServer.ShaeLib.concurrency.locked_resource.cls_decors.md](RunServer.ShaeLib.concurrency.locked_resource.cls_decors)  
> cls_decors(LockedClass, LC)

## LockedClass(...)
```python
@staticmethod
def LockedClass(lock_class: AbstractContextManager = RLock, I_KNOW_WHAT_IM_DOING: bool = False)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@52:74`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L52)
> Adds a "classlock" class variable  
> This should be used in tandem with either the @classlocked or @iclasslocked decorators
>> see help(classlockd) or help(iclasslocked) for real demo code
> Note that, unless you pass I_KNOW_WHAT_IM_DOING=True, lock_class is instantiated immediately in order to check if it is an instance of AbstractContextManager
>> This is to try to help emit a warning if LockedClass is used on a user class without being called (@LockedClass instead of @LockedClass())  
>> The lock_class must be instantiated to check, as threading.RLock and threading.Lock are actually functions  
>> I_KNOW_WHAT_IM_DOING=True disables both the immediate instantiation of lock_class, the isinstance check, and the warning
> lock_class is the type of lock (or really any context manager will do) to use (defaults to RLock)  
> Short demo code:
>> @LockedClass()  
>> class Locked: ...
> or, to use a custom lock:
>> @LockedClass(threading.Semaphore)  
>> class CustomLocked: ...

## LockedClass(...)
```python
@staticmethod
def LockedClass(lock_class: AbstractContextManager = RLock, I_KNOW_WHAT_IM_DOING: bool = False)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@52:74`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L52)
> Adds a "classlock" class variable  
> This should be used in tandem with either the @classlocked or @iclasslocked decorators
>> see help(classlockd) or help(iclasslocked) for real demo code
> Note that, unless you pass I_KNOW_WHAT_IM_DOING=True, lock_class is instantiated immediately in order to check if it is an instance of AbstractContextManager
>> This is to try to help emit a warning if LockedClass is used on a user class without being called (@LockedClass instead of @LockedClass())  
>> The lock_class must be instantiated to check, as threading.RLock and threading.Lock are actually functions  
>> I_KNOW_WHAT_IM_DOING=True disables both the immediate instantiation of lock_class, the isinstance check, and the warning
> lock_class is the type of lock (or really any context manager will do) to use (defaults to RLock)  
> Short demo code:
>> @LockedClass()  
>> class Locked: ...
> or, to use a custom lock:
>> @LockedClass(threading.Semaphore)  
>> class CustomLocked: ...