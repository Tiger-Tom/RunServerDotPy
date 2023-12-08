[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.basic.md](RunServer.Util.Locker.basic.md)  
> basic(LockedResource, LR, locked, lockd)

## locked(...)
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

## locked(...)
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