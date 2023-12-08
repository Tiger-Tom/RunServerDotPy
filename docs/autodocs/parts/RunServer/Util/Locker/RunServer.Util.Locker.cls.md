[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.cls.md](RunServer.Util.Locker.cls.md)  
> cls(LockedClass, LC, classlocked, clslockd, iclasslocked, iclslockd)

## LockedClass(...)
```python
@staticmethod
def LockedClass(lock_class: AbstractContextManager = RLock, I_KNOW_WHAT_IM_DOING: bool = False)
```

[`_rsruntime/util/locked_resource.py@52:74`](/_rsruntime/util/locked_resource.py#L52)
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

[`_rsruntime/util/locked_resource.py@52:74`](/_rsruntime/util/locked_resource.py#L52)
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

## classlocked(...)
```python
@staticmethod
def classlocked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@93:112`](/_rsruntime/util/locked_resource.py#L93)
> Similar to @locked, but uses cls's .classlock attribute  
> Does NOT imply classmethod (use @iclasslocked if you want to do that)  
> Meant to be used with the @LockedClass class decorator:
>> @LockedClass  
>> class DemoLockedClass:
>>> @classmethod # note: @classmethod BEFORE @classlocked  
>>> @classlocked # could both be replaced by a single @iclasslocked  
>>> def test_lock(cls):
>>>> print("class lock acquired!")
>>> @classlocked  
>>> def test_lock_2(self):
>>>> print("class lock acquired on non-classmethod!")

## classlocked(...)
```python
@staticmethod
def classlocked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@93:112`](/_rsruntime/util/locked_resource.py#L93)
> Similar to @locked, but uses cls's .classlock attribute  
> Does NOT imply classmethod (use @iclasslocked if you want to do that)  
> Meant to be used with the @LockedClass class decorator:
>> @LockedClass  
>> class DemoLockedClass:
>>> @classmethod # note: @classmethod BEFORE @classlocked  
>>> @classlocked # could both be replaced by a single @iclasslocked  
>>> def test_lock(cls):
>>>> print("class lock acquired!")
>>> @classlocked  
>>> def test_lock_2(self):
>>>> print("class lock acquired on non-classmethod!")

## iclasslocked(...)
```python
@staticmethod
def iclasslocked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@113:123`](/_rsruntime/util/locked_resource.py#L113)

<details>
<summary>Source Code</summary>

```python
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
```
</details>

> Is the same as @classlocked (it even calls it), but also wraps the method in classmethod  
> Meant to be used with @LockedClass:
>> @LockedClass()  
>> class Locked:
>>> @iclasslocked  
>>> def classlocked_classmethod(cls):
>>>> print("class lock acquired!")

## iclasslocked(...)
```python
@staticmethod
def iclasslocked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@113:123`](/_rsruntime/util/locked_resource.py#L113)

<details>
<summary>Source Code</summary>

```python
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
```
</details>

> Is the same as @classlocked (it even calls it), but also wraps the method in classmethod  
> Meant to be used with @LockedClass:
>> @LockedClass()  
>> class Locked:
>>> @iclasslocked  
>>> def classlocked_classmethod(cls):
>>>> print("class lock acquired!")