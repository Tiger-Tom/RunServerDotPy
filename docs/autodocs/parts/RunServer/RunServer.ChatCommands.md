# `ChatCommands` (`RunServer.ChatCommands` | `RS.CC`)
[`_rsruntime/lib/rs_userio.py`](/_rsruntime/lib/rs_userio.py "Source")  
[Standalone doc: parts/RunServer/RunServer.ChatCommands.md](RunServer.ChatCommands)  

## compose_command(...)
```python
def compose_command(cmd: str, args: str | None = None) -> str
```

[`_rsruntime/lib/rs_userio.py@329:334`](/_rsruntime/lib/rs_userio.py#L329)

<details>
<summary>Source Code</summary>

```python
def compose_command(self, cmd: str, args: str | None = None) -> str:
    '''Compiles cmd and args together using various configuration to compose a command string'''
    return Config['chat_commands/patterns/line'].format(
        char=Config['chat_commands/patterns/char'], command=cmd,
        argsep=('' if args is None else ' '),
        args=('' if args is None else (args if isinstance(args, str) else ' '.join(args))))
```
</details>

> Compiles cmd and args together using various configuration to compose a command string

## help(...)
```python
def help(...)
```
<details>
<summary>Parameters...</summary>

```python
    user: User, on: str | Literal[section] | None = None, section: None | str = None,
    force_console: bool | None = None
```
</details>

[`_rsruntime/lib/rs_userio.py@397:463`](/_rsruntime/lib/rs_userio.py#L397)
> Shows help on commands or sections.  
> If on is "section", then shows help on the section specified by "section"  
> If on is a command, then shows help on that command  
> If on is not supplied, then shows a list of top-level sections

## helpcmd_for(...)
```python
def helpcmd_for(item: str | None = None, for_section: bool = False)
```

[`_rsruntime/lib/rs_userio.py@470:477`](/_rsruntime/lib/rs_userio.py#L470)

<details>
<summary>Source Code</summary>

```python
def helpcmd_for(self, item: str | None = None, for_section: bool = False):
    '''Composes a help command for the item'''
    if item is None:
        assert not for_section, 'item should be None only if for_section is False'
        return self.compose_command('help')
    elif for_section:
        return self.compose_command('help', ('section', item))
    return self.compose_command('help', item)
```
</details>

> Composes a help command for the item

## init2()
```python
def init2()
```

[`_rsruntime/lib/rs_userio.py@298:302`](/_rsruntime/lib/rs_userio.py#L298)

<details>
<summary>Source Code</summary>

```python
def init2(self):
    # Register hooks
    LineParser.register_chat_callback(self.run_command)
    # Register help command
    self.register_func(self.help, {'?',})
```
</details>

> <no doc>

## parse_command(...)
```python
def parse_command(line: str) -> tuple[bool, _rsruntime.lib.rs_userio.ChatCommands.ChatCommand | str, str]
```

[`_rsruntime/lib/rs_userio.py@335:345`](/_rsruntime/lib/rs_userio.py#L335)

<details>
<summary>Source Code</summary>

```python
def parse_command(self, line: str) -> tuple[bool, ChatCommand | str, str]:
    '''
        Returns:
          - a (True, ChatCommand, args) tuple if the line is a ChatCommand
          - a (False, command, args) tuple if the line matches as a ChatCommand, but the command in question hasn't been registered
          - None if the line doesn't match as a ChatCommand
    '''
    if m := self.command_patt.fullmatch(line):
        is_cmd = m.group('cmd') in self
        return (is_cmd, self[m.group('cmd')] if is_cmd else m.group('cmd'), m.group('args'))
    return None
```
</details>

> Returns:  
> - a (True, ChatCommand, args) tuple if the line is a ChatCommand  
> - a (False, command, args) tuple if the line matches as a ChatCommand, but the command in question hasn't been registered  
> - None if the line doesn't match as a ChatCommand

## register(...)
```python
def register(cmd: ChatCommands.ChatCommand, aliases: set = set()) -> ChatCommands.ChatCommand
```

[`_rsruntime/lib/rs_userio.py@369:387`](/_rsruntime/lib/rs_userio.py#L369)
> <no doc>

## register_func(...)
```python
def register_func(...) -> ChatCommands.ChatCommand
```
<details>
<summary>Parameters...</summary>

```python
    func: Callable(User, Ellipsis), aliases: set = set(), permission: Perm = 80,
    help_section: str | tuple[str, ...] = ()
```
</details>

[`_rsruntime/lib/rs_userio.py@365:368`](/_rsruntime/lib/rs_userio.py#L365)

<details>
<summary>Source Code</summary>

```python
def register_func(self, func: typing.Callable[[UserManager.User, ...], None], aliases: set = set(), *, permission: UserManager.Perm = UserManager.Perm.USER, help_section: str | tuple[str, ...] = ()) -> 'ChatCommands.ChatCommand':
    cc = self.ChatCommand(func, permission=permission, help_section=help_section)
    self.register(cc, aliases)
    return cc
```
</details>

> <no doc>

## run_command(...)
```python
def run_command(user: User, line: str, not_secure: bool = False)
```

[`_rsruntime/lib/rs_userio.py@346:363`](/_rsruntime/lib/rs_userio.py#L346)
> <no doc>