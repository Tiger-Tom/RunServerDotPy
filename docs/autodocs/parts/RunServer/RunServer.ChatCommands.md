# `ChatCommands` (`RunServer.ChatCommands` | `RS.CC`)
[`_rsruntime/lib/rs_userio.py`](/_rsruntime/lib/rs_userio.py "Source")  
[Standalone doc: parts/RunServer/RunServer.ChatCommands.md](RunServer.ChatCommands.md)  

## compose_command(...)
```python
def compose_command(cmd: str, args: str | None) -> str
```

[`_rsruntime/lib/rs_userio.py@328:333`](/_rsruntime/lib/rs_userio.py#L328)

<details>
<summary>Source Code</summary>

```python
def compose_command(self, cmd: str, args: str | None) -> str:
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

[`_rsruntime/lib/rs_userio.py@395:461`](/_rsruntime/lib/rs_userio.py#L395)
> Shows help on commands or sections.  
> If on is "section", then shows help on the section specified by "section"  
> If on is a command, then shows help on that command  
> If on is not supplied, then shows a list of top-level sections

## helpcmd_for(...)
```python
def helpcmd_for(item: str | None = None, for_section: bool = False)
```

[`_rsruntime/lib/rs_userio.py@468:475`](/_rsruntime/lib/rs_userio.py#L468)

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

[`_rsruntime/lib/rs_userio.py@297:301`](/_rsruntime/lib/rs_userio.py#L297)

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

[`_rsruntime/lib/rs_userio.py@334:344`](/_rsruntime/lib/rs_userio.py#L334)

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

[`_rsruntime/lib/rs_userio.py@367:385`](/_rsruntime/lib/rs_userio.py#L367)
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

[`_rsruntime/lib/rs_userio.py@363:366`](/_rsruntime/lib/rs_userio.py#L363)

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

[`_rsruntime/lib/rs_userio.py@345:361`](/_rsruntime/lib/rs_userio.py#L345)

<details>
<summary>Source Code</summary>

```python
def run_command(self, user: UserManager.User, line: str, not_secure: bool = False):
    mat = self.parse_command(line)
    if mat is None: return # not a ChatCommand
    try:
        if not mat[0]:
            raise KeyError(f'ChatCommand {mat[1]} was not found, perhaps try {self.helpcmd_for()}?')
        mat[1](user, *mat[1].params.parse_args(*mat[1].split_args(mat[2])))
    except Exception as e:
        if user is user.CONSOLE:
            print(f'Failure whilst running command {line!r}:\n{"".join(traceback.format_exception(e))}')
            return
        exc = ''.join(traceback.format_exception(e))
        user.tell(TellRaw.text(f'A failure occured whilst running command {line!r}:', TellRaw.TextFormat(color='#FF0000')).line_break() \
                         .text(repr(e), '#FF0000').line_break() \
                         .text('Click to copy full error message', '#FF0000',
                               click_event=TellRaw.ClickEvent.COPY, click_contents=exc,
                               hover_event=TellRaw.HoverEvent.TEXT, hover_contents=TellRaw().text(exc, '#FF0000', TellRaw.TF.UNDERLINED)))
```
</details>

> <no doc>