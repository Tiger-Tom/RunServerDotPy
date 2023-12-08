[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.etc.md](RunServer.Util.Locker.etc.md)  
> etc(locked_by, lockdby)

## locked_by(...)
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

## locked_by(...)
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