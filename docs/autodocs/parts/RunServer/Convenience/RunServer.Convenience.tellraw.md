[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/RunServer.Convenience.tellraw.md](RunServer.Convenience.tellraw)  
> Tells a user something. See RS.TR.text for more advanced usage
>> This function uses RS.TR.itell

## tell(...)
```python
@staticmethod
def tell(self, text: ForwardRef('RS.TellRaw') | tuple[str | dict] | str)
```

[`_rsruntime/lib/rs_usermgr.py@97:102`](/_rsruntime/lib/rs_usermgr.py#L97)

<details>
<summary>Source Code</summary>

```python
def tell(self, text: typing.ForwardRef('RS.TellRaw') | tuple[str | dict] | str):
    if not (hasattr(self, 'name') or self.is_console):
        raise TypeError(f'User {self} has no name; cannot tell')
    if isinstance(text, RS.TellRaw): text = text.render()
    if self.is_console: print(f'CONSOLE.tell: {text if isinstance(text, str) else json.dumps(text, indent=4)}')
    else: RS.SM.write(f'tellraw {self.name} {json.dumps(text)}')
```
</details>

> <no doc>