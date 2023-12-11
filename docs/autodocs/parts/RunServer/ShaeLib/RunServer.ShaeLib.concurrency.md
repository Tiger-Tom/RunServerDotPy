[Standalone doc: parts/RunServer/ShaeLib/RunServer.ShaeLib.concurrency.md](RunServer.ShaeLib.concurrency)  

## `locked_resource` (`RunServer.ShaeLib.concurrency.locked_resource` | `RS.SL.concurrency.locked_resource`)
[Standalone doc: parts/RunServer/ShaeLib/concurrency/RunServer.ShaeLib.concurrency.locked_resource.md](RunServer.ShaeLib.concurrency.locked_resource)  

### `LockedResource` (`RunServer.ShaeLib.concurrency.locked_resource.LockedResource` | `RS.SL.concurrency.locked_resource.LockedResource`)
[`_rsruntime/ShaeLib/concurrency/locked_resource.py`](/_rsruntime/ShaeLib/concurrency/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/concurrency/locked_resource/RunServer.ShaeLib.concurrency.locked_resource.LockedResource.md](RunServer.ShaeLib.concurrency.locked_resource.LockedResource)  
> Adds a "lock" parameter to class instances (and slots!)  
> This should be used in tandem with the @locked decorator:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock  
>>>> print("initialized!")
>>> @locked # note decorator  
>>> def test_lock(self):
>>>> print("lock acquired!")

### `basic` (`RunServer.ShaeLib.concurrency.locked_resource.basic` | `RS.SL.concurrency.locked_resource.basic`)
####  OR `b` (`RunServer.ShaeLib.concurrency.locked_resource.b` | `RS.SL.concurrency.locked_resource.b`)
[`_rsruntime/ShaeLib/concurrency/locked_resource.py`](/_rsruntime/ShaeLib/concurrency/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/concurrency/locked_resource/RunServer.ShaeLib.concurrency.locked_resource.basic.md](RunServer.ShaeLib.concurrency.locked_resource.basic)  
> basic(LockedResource, LR, locked, lockd)

#### locked(...)
```python
@staticmethod
def locked(func: Callable)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@76:92`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L76)

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

#### locked(...)
```python
@staticmethod
def locked(func: Callable)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@76:92`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L76)

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

### `cls` (`RunServer.ShaeLib.concurrency.locked_resource.cls` | `RS.SL.concurrency.locked_resource.cls`)
[`_rsruntime/ShaeLib/concurrency/locked_resource.py`](/_rsruntime/ShaeLib/concurrency/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/concurrency/locked_resource/RunServer.ShaeLib.concurrency.locked_resource.cls.md](RunServer.ShaeLib.concurrency.locked_resource.cls)  
> cls(LockedClass, LC, classlocked, clslockd, iclasslocked, iclslockd)

#### LockedClass(...)
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

#### LockedClass(...)
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

#### classlocked(...)
```python
@staticmethod
def classlocked(func: Callable)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@93:112`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L93)
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

#### classlocked(...)
```python
@staticmethod
def classlocked(func: Callable)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@93:112`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L93)
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

#### iclasslocked(...)
```python
@staticmethod
def iclasslocked(func: Callable)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@113:123`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L113)

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

#### iclasslocked(...)
```python
@staticmethod
def iclasslocked(func: Callable)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@113:123`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L113)

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

### `cls_decors` (`RunServer.ShaeLib.concurrency.locked_resource.cls_decors` | `RS.SL.concurrency.locked_resource.cls_decors`)
[`_rsruntime/ShaeLib/concurrency/locked_resource.py`](/_rsruntime/ShaeLib/concurrency/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/concurrency/locked_resource/RunServer.ShaeLib.concurrency.locked_resource.cls_decors.md](RunServer.ShaeLib.concurrency.locked_resource.cls_decors)  
> cls_decors(LockedClass, LC)

#### LockedClass(...)
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

#### LockedClass(...)
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

### `etc` (`RunServer.ShaeLib.concurrency.locked_resource.etc` | `RS.SL.concurrency.locked_resource.etc`)
[`_rsruntime/ShaeLib/concurrency/locked_resource.py`](/_rsruntime/ShaeLib/concurrency/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/concurrency/locked_resource/RunServer.ShaeLib.concurrency.locked_resource.etc.md](RunServer.ShaeLib.concurrency.locked_resource.etc)  
> etc(locked_by, lockdby)

#### locked_by(...)
```python
@staticmethod
def locked_by(lock: AbstractContextManager)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@125:132`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L125)

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

#### locked_by(...)
```python
@staticmethod
def locked_by(lock: AbstractContextManager)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@125:132`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L125)

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

### `func_decors` (`RunServer.ShaeLib.concurrency.locked_resource.func_decors` | `RS.SL.concurrency.locked_resource.func_decors`)
[`_rsruntime/ShaeLib/concurrency/locked_resource.py`](/_rsruntime/ShaeLib/concurrency/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/concurrency/locked_resource/RunServer.ShaeLib.concurrency.locked_resource.func_decors.md](RunServer.ShaeLib.concurrency.locked_resource.func_decors)  
> func_decors(locked, lockd, classlocked, clslockd, iclasslocked, iclslockd, locked_by, lockdby)

#### classlocked(...)
```python
@staticmethod
def classlocked(func: Callable)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@93:112`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L93)
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

#### classlocked(...)
```python
@staticmethod
def classlocked(func: Callable)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@93:112`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L93)
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

#### iclasslocked(...)
```python
@staticmethod
def iclasslocked(func: Callable)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@113:123`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L113)

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

#### iclasslocked(...)
```python
@staticmethod
def iclasslocked(func: Callable)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@113:123`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L113)

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

#### locked(...)
```python
@staticmethod
def locked(func: Callable)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@76:92`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L76)

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

#### locked(...)
```python
@staticmethod
def locked(func: Callable)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@76:92`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L76)

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

#### locked_by(...)
```python
@staticmethod
def locked_by(lock: AbstractContextManager)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@125:132`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L125)

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

#### locked_by(...)
```python
@staticmethod
def locked_by(lock: AbstractContextManager)
```

[`_rsruntime/ShaeLib/concurrency/locked_resource.py@125:132`](/_rsruntime/ShaeLib/concurrency/locked_resource.py#L125)

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

### `locked` (`RunServer.ShaeLib.concurrency.locked_resource.locked` | `RS.SL.concurrency.locked_resource.locked`)
[`_rsruntime/ShaeLib/concurrency/locked_resource.py`](/_rsruntime/ShaeLib/concurrency/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/concurrency/locked_resource/RunServer.ShaeLib.concurrency.locked_resource.locked.md](RunServer.ShaeLib.concurrency.locked_resource.locked)  
> Waits to acquire the method's self's .lock attribute (uses "with")  
> This should be used in tandem with the LockedResource superclass:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock  
>>>> print("initialized!")
>>> @locked # note decorator  
>>> def test_lock(self):
>>>> print("lock acquired!")

### `superclasses` (`RunServer.ShaeLib.concurrency.locked_resource.superclasses` | `RS.SL.concurrency.locked_resource.superclasses`)
[`_rsruntime/ShaeLib/concurrency/locked_resource.py`](/_rsruntime/ShaeLib/concurrency/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/concurrency/locked_resource/RunServer.ShaeLib.concurrency.locked_resource.superclasses.md](RunServer.ShaeLib.concurrency.locked_resource.superclasses)  
> superclasses(LockedResource, LR)