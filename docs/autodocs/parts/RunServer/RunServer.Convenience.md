# `Convenience` (`RunServer.Convenience` | `RS._`)
[Standalone doc: parts/RunServer/RunServer.Convenience.md](RunServer.Convenience.md)  

## `command` (`RunServer.Convenience.command` | `RS._.command`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/RunServer.Convenience.command.md](RunServer.Convenience.command.md)  
> Writes a command to the server
>> Equivelant to RS.SM.write(line)

## `inject_line` (`RunServer.Convenience.inject_line` | `RS._.inject_line`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/RunServer.Convenience.inject_line.md](RunServer.Convenience.inject_line.md)  
> Injects a line into LineParser, as if it was read from the ServerManager
>> Equivelant to RS.LP.handle_line(line)

## `listen_chat` (`RunServer.Convenience.listen_chat` | `RS._.listen_chat`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/RunServer.Convenience.listen_chat.md](RunServer.Convenience.listen_chat.md)  
> Registers a callback for when LineParser reads a chat message
>> The callback should have three arguments:  
>> - the user (RS.UM.User object)  
>> - the line (str)  
>> - if the message was "not secure" (bool)

## `say` (`RunServer.Convenience.say` | `RS._.say`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/RunServer.Convenience.say.md](RunServer.Convenience.say.md)  

## `tell` (`RunServer.Convenience.tell` | `RS._.tell`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/RunServer.Convenience.tell.md](RunServer.Convenience.tell.md)  

## `tellraw` (`RunServer.Convenience.tellraw` | `RS._.tellraw`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/RunServer.Convenience.tellraw.md](RunServer.Convenience.tellraw.md)  
> Tells a user something. See RS.TR.text for more advanced usage
>> This function uses RS.TR.itell

### tell(...)
```python
@staticmethod
def tell(self, text: ForwardRef('TellRaw') | tuple[str | dict] | str)
```

[`_rsruntime/lib/rs_usermgr.py@96:101`](/_rsruntime/lib/rs_usermgr.py#L96)

<details>
<summary>Source Code</summary>

```python
def tell(self, text: typing.ForwardRef('TellRaw') | tuple[str | dict] | str):
    if not (hasattr(self, 'name') or self.is_console):
        raise TypeError(f'User {self} has no name; cannot tell')
    if isinstance(text, TellRaw): text = text.render()
    if self.is_console: print(f'CONSOLE.tell: {text if isinstance(text, str) else json.dumps(text, indent=4)}')
    else: RS.SM.write(f'tellraw {self.name} {json.dumps(text)}')
```
</details>

> <no doc>