[`_rsruntime/ShaeLib/timing/timer.py`](/_rsruntime/ShaeLib/timing/timer.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/timing/RunServer.ShaeLib.timing.Timer.md](RunServer.ShaeLib.timing.Timer)  

## clear(...)
```python
@staticmethod
def clear(timer: BaseTimer) -> BaseTimer
```

[`_rsruntime/ShaeLib/timing/timer.py@84:86`](/_rsruntime/ShaeLib/timing/timer.py#L84)

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

[`_rsruntime/ShaeLib/timing/timer.py@80:83`](/_rsruntime/ShaeLib/timing/timer.py#L80)

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