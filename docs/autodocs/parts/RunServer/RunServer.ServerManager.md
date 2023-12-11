# `ServerManager` (`RunServer.ServerManager` | `RS.SM`)
[`_rsruntime/lib/rs_servmgr.py`](/_rsruntime/lib/rs_servmgr.py "Source")  
[Standalone doc: parts/RunServer/RunServer.ServerManager.md](RunServer.ServerManager)  

## preferred_order()
```python
@classmethod
def preferred_order() -> list[type[BaseServerManager]]
```

[`_rsruntime/lib/rs_servmgr.py@199:201`](/_rsruntime/lib/rs_servmgr.py#L199)

<details>
<summary>Source Code</summary>

```python
@classmethod
def preferred_order(cls) -> list[typing.Type[BaseServerManager]]:
    return sorted(cls.managers.__dict__.values(), key=lambda t: t.real_bias, reverse=True)
```
</details>

> <no doc>

## register(...)
```python
@classmethod
def register(manager_type: type[BaseServerManager])
```

[`_rsruntime/lib/rs_servmgr.py@196:198`](/_rsruntime/lib/rs_servmgr.py#L196)

<details>
<summary>Source Code</summary>

```python
@classmethod
def register(cls, manager_type: typing.Type[BaseServerManager]):
    setattr(cls.managers, manager_type.name.replace('.', '_'), manager_type)
```
</details>

> <no doc>