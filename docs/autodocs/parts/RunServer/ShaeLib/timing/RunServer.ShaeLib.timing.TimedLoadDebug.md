[`_rsruntime/ShaeLib/timing/timed_load_debug.py`](/_rsruntime/ShaeLib/timing/timed_load_debug.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/timing/RunServer.ShaeLib.timing.TimedLoadDebug.md](RunServer.ShaeLib.timing.TimedLoadDebug)  
> Helper class for debugging time spent doing things

## final(...)
```python
@staticmethod
def final(self)
```

[`_rsruntime/ShaeLib/timing/timed_load_debug.py@27:29`](/_rsruntime/ShaeLib/timing/timed_load_debug.py#L27)

<details>
<summary>Source Code</summary>

```python
def final(self):
    self.logfn(self.msgfmt[0][1].format(opc=self.ocounter, ipc=self.icounter))
    self.ocounter = None # stop accidental multiple final() calls
```
</details>

> <no doc>

## foreach(...)
```python
@classmethod
def foreach(logfunc: Callable(str), each: tuple[tuple[str, Callable], Ellipsis], tld_args)
```

[`_rsruntime/ShaeLib/timing/timed_load_debug.py@40:45`](/_rsruntime/ShaeLib/timing/timed_load_debug.py#L40)

<details>
<summary>Source Code</summary>

```python
@classmethod
def foreach(cls, logfunc: typing.Callable[[str], None], *each: tuple[tuple[str, typing.Callable[[], None]], ...], **tld_args):
    '''Executes each callable (second element of every "each" tuple) in each and times it with TimedLoadDebug, setting {c} as the first element of every "each" tuple'''
    tld = cls(logfunc, iterable=(n for n,c in each), **tld_args)
    for n,c in each:
        with tld: c()
```
</details>

> Executes each callable (second element of every "each" tuple) in each and times it with TimedLoadDebug, setting {c} as the first element of every "each" tuple

## ienter(...)
```python
@staticmethod
def ienter(self)
```

[`_rsruntime/ShaeLib/timing/timed_load_debug.py@30:32`](/_rsruntime/ShaeLib/timing/timed_load_debug.py#L30)

<details>
<summary>Source Code</summary>

```python
def ienter(self):
    self.icounter = PerfCounter(sec='', secs='')
    self.logfn(self.msgfmt[1][0].format(c=next(self.cur[0]), opc=self.ocounter, ipc=self.icounter))
```
</details>

> <no doc>

## iexit(...)
```python
@staticmethod
def iexit(...)
```
<details>
<summary>Parameters...</summary>

```python
    self, exc_type: type | None, exc_value: typing.Any | None,
    traceback: traceback
```
</details>

[`_rsruntime/ShaeLib/timing/timed_load_debug.py@34:37`](/_rsruntime/ShaeLib/timing/timed_load_debug.py#L34)

<details>
<summary>Source Code</summary>

```python
def iexit(self, exc_type: type | None, exc_value: typing.Any | None, traceback: TracebackType):
    r = self.msgfmt[2](exc_type, exc_value, traceback)
    if r is False: return
    self.logfn(self.msgfmt[1][1].format(c=next(self.cur[1]), opc=self.ocounter, ipc=self.icounter) if r is None else r)
```
</details>

> <no doc>