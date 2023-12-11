[`_rsruntime/ShaeLib/concurrency/locked_resource.py`](/_rsruntime/ShaeLib/concurrency/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/concurrency/locked_resource/RunServer.ShaeLib.concurrency.locked_resource.func_decors.md](RunServer.ShaeLib.concurrency.locked_resource.func_decors)  
> func_decors(locked, lockd, classlocked, clslockd, iclasslocked, iclslockd, locked_by, lockdby)

## classlocked(...)
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

## classlocked(...)
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

## iclasslocked(...)
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

## iclasslocked(...)
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

## locked(...)
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

## locked(...)
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

## locked_by(...)
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

## locked_by(...)
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