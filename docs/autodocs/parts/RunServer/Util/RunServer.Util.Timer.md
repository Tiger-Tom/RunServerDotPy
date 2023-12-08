[`_rsruntime/util/timer.py`](/_rsruntime/util/timer.py "Source")  
[Standalone doc: parts/RunServer/Util/RunServer.Util.Timer.md](RunServer.Util.Timer.md)  

## clear(...)
```python
@staticmethod
def clear(timer: BaseTimer) -> BaseTimer
```

[`_rsruntime/util/timer.py@84:86`](/_rsruntime/util/timer.py#L84)

<details>
<summary>Source Code</summary>

```python
@staticmethod
def clear(timer: BaseTimer) -> BaseTimer:
    return timer.stop()
```
</details>

> <no doc>

## set_timer(...)
```python
@staticmethod
def set_timer(...) -> Timer.BaseTimer
```
<details>
<summary>Parameters...</summary>

```python
    timer_type: type[Timer.BaseTimer], func: Callable, secs: float,
    activate_now: bool = True
```
</details>

[`_rsruntime/util/timer.py@80:83`](/_rsruntime/util/timer.py#L80)

<details>
<summary>Source Code</summary>

```python
@staticmethod
def set_timer(timer_type: type['Timer.BaseTimer'], func: typing.Callable, secs: float, activate_now: bool = True) -> 'Timer.BaseTimer':
    if activate_now: return timer_type(func, secs).start()
    return timer_type(func, secs)
```
</details>

> <no doc>