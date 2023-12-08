[Standalone doc: parts/RunServer/Util/RunServer.Util.Locker.md](RunServer.Util.Locker.md)  

## `LockedResource` (`RunServer.Util.Locker.LockedResource` | `RS.U.Locker.LockedResource`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.LockedResource.md](RunServer.Util.Locker.LockedResource.md)  
> Adds a "lock" parameter to class instances (and slots!)  
> This should be used in tandem with the @locked decorator:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock  
>>>> print("initialized!")
>>> @locked # note decorator  
>>> def test_lock(self):
>>>> print("lock acquired!")

## `basic` (`RunServer.Util.Locker.basic` | `RS.U.Locker.basic`)
###  OR `b` (`RunServer.Util.Locker.b` | `RS.U.Locker.b`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.basic.md](RunServer.Util.Locker.basic.md)  
> basic(LockedResource, LR, locked, lockd)

### locked(...)
```python
@staticmethod
def locked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@76:92`](/_rsruntime/util/locked_resource.py#L76)

<details>
<summary>Source Code</summary>

```python
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
```
</details>

> Waits to acquire the method's self's .lock attribute (uses "with")  
> This should be used in tandem with the LockedResource superclass:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock  
>>>> print("initialized!")
>>> @locked # note decorator  
>>> def test_lock(self):
>>>> print("lock acquired!")

### locked(...)
```python
@staticmethod
def locked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@76:92`](/_rsruntime/util/locked_resource.py#L76)

<details>
<summary>Source Code</summary>

```python
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
```
</details>

> Waits to acquire the method's self's .lock attribute (uses "with")  
> This should be used in tandem with the LockedResource superclass:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock  
>>>> print("initialized!")
>>> @locked # note decorator  
>>> def test_lock(self):
>>>> print("lock acquired!")

## `cls` (`RunServer.Util.Locker.cls` | `RS.U.Locker.cls`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.cls.md](RunServer.Util.Locker.cls.md)  
> cls(LockedClass, LC, classlocked, clslockd, iclasslocked, iclslockd)

### LockedClass(...)
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

### LockedClass(...)
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

### classlocked(...)
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

### classlocked(...)
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

### iclasslocked(...)
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

### iclasslocked(...)
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

## `cls_decors` (`RunServer.Util.Locker.cls_decors` | `RS.U.Locker.cls_decors`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.cls_decors.md](RunServer.Util.Locker.cls_decors.md)  
> cls_decors(LockedClass, LC)

### LockedClass(...)
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

### LockedClass(...)
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

## `etc` (`RunServer.Util.Locker.etc` | `RS.U.Locker.etc`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.etc.md](RunServer.Util.Locker.etc.md)  
> etc(locked_by, lockdby)

### locked_by(...)
```python
@staticmethod
def locked_by(lock: AbstractContextManager)
```

[`_rsruntime/util/locked_resource.py@125:132`](/_rsruntime/util/locked_resource.py#L125)

<details>
<summary>Source Code</summary>

```python
def locked_by(lock: AbstractContextManager):
    def func_locker(func: typing.Callable):
        @wraps(func)
        def locked_func(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return locked_func
    return func_locker
```
</details>

> <no doc>

### locked_by(...)
```python
@staticmethod
def locked_by(lock: AbstractContextManager)
```

[`_rsruntime/util/locked_resource.py@125:132`](/_rsruntime/util/locked_resource.py#L125)

<details>
<summary>Source Code</summary>

```python
def locked_by(lock: AbstractContextManager):
    def func_locker(func: typing.Callable):
        @wraps(func)
        def locked_func(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return locked_func
    return func_locker
```
</details>

> <no doc>

## `func_decors` (`RunServer.Util.Locker.func_decors` | `RS.U.Locker.func_decors`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.func_decors.md](RunServer.Util.Locker.func_decors.md)  
> func_decors(locked, lockd, classlocked, clslockd, iclasslocked, iclslockd, locked_by, lockdby)

### classlocked(...)
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

### classlocked(...)
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

### iclasslocked(...)
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

### iclasslocked(...)
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

### locked(...)
```python
@staticmethod
def locked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@76:92`](/_rsruntime/util/locked_resource.py#L76)

<details>
<summary>Source Code</summary>

```python
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
```
</details>

> Waits to acquire the method's self's .lock attribute (uses "with")  
> This should be used in tandem with the LockedResource superclass:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock  
>>>> print("initialized!")
>>> @locked # note decorator  
>>> def test_lock(self):
>>>> print("lock acquired!")

### locked(...)
```python
@staticmethod
def locked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@76:92`](/_rsruntime/util/locked_resource.py#L76)

<details>
<summary>Source Code</summary>

```python
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
```
</details>

> Waits to acquire the method's self's .lock attribute (uses "with")  
> This should be used in tandem with the LockedResource superclass:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock  
>>>> print("initialized!")
>>> @locked # note decorator  
>>> def test_lock(self):
>>>> print("lock acquired!")

### locked_by(...)
```python
@staticmethod
def locked_by(lock: AbstractContextManager)
```

[`_rsruntime/util/locked_resource.py@125:132`](/_rsruntime/util/locked_resource.py#L125)

<details>
<summary>Source Code</summary>

```python
def locked_by(lock: AbstractContextManager):
    def func_locker(func: typing.Callable):
        @wraps(func)
        def locked_func(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return locked_func
    return func_locker
```
</details>

> <no doc>

### locked_by(...)
```python
@staticmethod
def locked_by(lock: AbstractContextManager)
```

[`_rsruntime/util/locked_resource.py@125:132`](/_rsruntime/util/locked_resource.py#L125)

<details>
<summary>Source Code</summary>

```python
def locked_by(lock: AbstractContextManager):
    def func_locker(func: typing.Callable):
        @wraps(func)
        def locked_func(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return locked_func
    return func_locker
```
</details>

> <no doc>

## `locked` (`RunServer.Util.Locker.locked` | `RS.U.Locker.locked`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.locked.md](RunServer.Util.Locker.locked.md)  
> Waits to acquire the method's self's .lock attribute (uses "with")  
> This should be used in tandem with the LockedResource superclass:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock  
>>>> print("initialized!")
>>> @locked # note decorator  
>>> def test_lock(self):
>>>> print("lock acquired!")

## `superclasses` (`RunServer.Util.Locker.superclasses` | `RS.U.Locker.superclasses`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.superclasses.md](RunServer.Util.Locker.superclasses.md)  
> superclasses(LockedResource, LR)