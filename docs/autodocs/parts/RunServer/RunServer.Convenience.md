# `Convenience` (`RunServer.Convenience` | `RS._`)
[Standalone doc: parts/RunServer/RunServer.Convenience.md](RunServer.Convenience)  

## `command` (`RunServer.Convenience.command` | `RS._.command`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/RunServer.Convenience.command.md](RunServer.Convenience.command)  
> Writes a command to the server
>> Equivelant to RS.SM.command(*commands)

## `inject_line` (`RunServer.Convenience.inject_line` | `RS._.inject_line`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/RunServer.Convenience.inject_line.md](RunServer.Convenience.inject_line)  
> Injects a line into LineParser, as if it was read from the ServerManager
>> Equivelant to RS.LP.handle_line(line)

## `listen_chat` (`RunServer.Convenience.listen_chat` | `RS._.listen_chat`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/RunServer.Convenience.listen_chat.md](RunServer.Convenience.listen_chat)  
> Registers a callback for when LineParser reads a chat message
>> The callback should have three arguments:  
>> - the user (RS.UM.User object)  
>> - the line (str)  
>> - if the message was "not secure" (bool)

## `say` (`RunServer.Convenience.say` | `RS._.say`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/RunServer.Convenience.say.md](RunServer.Convenience.say)  

## `tell` (`RunServer.Convenience.tell` | `RS._.tell`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/RunServer.Convenience.tell.md](RunServer.Convenience.tell)  

## `tellraw` (`RunServer.Convenience.tellraw` | `RS._.tellraw`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/RunServer.Convenience.tellraw.md](RunServer.Convenience.tellraw)  
> Tells a user something. See RS.TR.text for more advanced usage
>> This function uses RS.TR.itell

### tell(...)
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
    else: RS.SM.command(f'tellraw {self.name} {json.dumps(text)}')
```
</details>

> <no doc>