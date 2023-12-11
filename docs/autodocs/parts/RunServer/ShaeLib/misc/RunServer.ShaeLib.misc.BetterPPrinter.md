[`_rsruntime/ShaeLib/misc/betterprettyprinter.py`](/_rsruntime/ShaeLib/misc/betterprettyprinter.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/misc/RunServer.ShaeLib.misc.BetterPPrinter.md](RunServer.ShaeLib.misc.BetterPPrinter)  

## format(...)
```python
@staticmethod
def format(self, obj, _indent_: int = 0) -> Generator[str, None, None]
```

[`_rsruntime/ShaeLib/misc/betterprettyprinter.py@35:67`](/_rsruntime/ShaeLib/misc/betterprettyprinter.py#L35)
> <no doc>

## formats(...)
```python
@staticmethod
def formats(self, obj, joiner: str = '') -> str
```

[`_rsruntime/ShaeLib/misc/betterprettyprinter.py@68:69`](/_rsruntime/ShaeLib/misc/betterprettyprinter.py#L68)

<details>
<summary>Source Code</summary>

```python
def formats(self, obj, joiner: str = '') -> str:
    return joiner.join(self.format(obj))
```
</details>

> <no doc>

## writes(...)
```python
@staticmethod
def writes(...)
```
<details>
<summary>Parameters...</summary>

```python
    self, obj, fp=<_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>,
    end: str = '\n', delay: float | None = None, collect: list | Callable(str) | None = None
```
</details>

[`_rsruntime/ShaeLib/misc/betterprettyprinter.py@70:78`](/_rsruntime/ShaeLib/misc/betterprettyprinter.py#L70)

<details>
<summary>Source Code</summary>

```python
def writes(self, obj, fp=sys.stdout, end: str = '\n', delay: float | None = None, collect: list | typing.Callable[[str], None] | None = None):
    for tok in self.format(obj):
        fp.write(tok)
        if delay: time.sleep(delay) # for aesthetic or testing purposes
        if collect is not None:
            if callable(collect): collect(tok)
            else: collect.append(fp)
    fp.write(end)
    return collect
```
</details>

> <no doc>