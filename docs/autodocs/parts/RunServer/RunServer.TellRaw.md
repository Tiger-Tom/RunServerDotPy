# `TellRaw` (`RunServer.TellRaw` | `RS.TR`)
[`_rsruntime/lib/rs_userio.py`](/_rsruntime/lib/rs_userio.py "Source")  
[Standalone doc: parts/RunServer/RunServer.TellRaw.md](RunServer.TellRaw)  
> Generates a TellRaw JSON
>> Praise be to https://www.minecraftjson.com !
> Who doesn't want object-oriented TellRaws???

## ijoin(...)
```python
@staticmethod
def ijoin(self, tellraws: tuple[Self | str | dict]) -> Generator[[typing.Self], None, None]
```

[`_rsruntime/lib/rs_userio.py@105:109`](/_rsruntime/lib/rs_userio.py#L105)

<details>
<summary>Source Code</summary>

```python
def ijoin(self, tellraws: tuple[typing.Self | str | dict]) -> typing.Generator[[typing.Self], None, None]:
    for i,tr in enumerate(tellraws):
        yield tr
        if i < len(tellraws)-1:
            yield self
```
</details>

> <no doc>

## itell(...)
```python
@classmethod
def itell(user: User, args, kwargs)
```

[`_rsruntime/lib/rs_userio.py@114:117`](/_rsruntime/lib/rs_userio.py#L114)

<details>
<summary>Source Code</summary>

```python
@classmethod
def itell(cls, user: UserManager.User, *args, **kwargs):
    '''Convenience method for `user.tell(RS.TR().text(*args, **kwargs))`'''
    user.tell(cls().text(*args, **kwargs))
```
</details>

> Convenience method for `user.tell(RS.TR().text(*args, **kwargs))`

## join(...)
```python
@staticmethod
def join(self, tellraws: tuple[Self | str | dict]) -> Self
```

[`_rsruntime/lib/rs_userio.py@110:111`](/_rsruntime/lib/rs_userio.py#L110)

<details>
<summary>Source Code</summary>

```python
def join(self, tellraws: tuple[typing.Self | str | dict]) -> typing.Self:
    return self.__class__(self.ijoin(tellraws))
```
</details>

> <no doc>

## line_break(...)
```python
@staticmethod
def line_break(self, count: int = 1)
```

[`_rsruntime/lib/rs_userio.py@99:103`](/_rsruntime/lib/rs_userio.py#L99)

<details>
<summary>Source Code</summary>

```python
def line_break(self, count: int = 1):
    '''Append n newlines to self (where n >= 0)'''
    if count < 0: raise ValueError('Cannot append a negative amount of newlines')
    for _ in range(count): self.append(r'\n')
    return self
```
</details>

> Append n newlines to self (where n >= 0)

## render(...)
```python
@staticmethod
def render(self)
```

[`_rsruntime/lib/rs_userio.py@37:38`](/_rsruntime/lib/rs_userio.py#L37)

<details>
<summary>Source Code</summary>

```python
def render(self):
    return json.dumps(self)
```
</details>

> <no doc>

## text(...)
```python
@staticmethod
def text(...)
```
<details>
<summary>Parameters...</summary>

```python
    self, text: str, color: str | None = None,
    fmt: TextFormat | dict = 0, insertion: str | None = None, type: TextType = TextType.TEXT,
    objective: None | str = None, click_event: ClickEvent | None = None, click_contents: None | str = None,
    hover_event: HoverEvent | None = None, hover_contents: None | ForwardRef('TellRaw') | tuple | dict = None
```
</details>

[`_rsruntime/lib/rs_userio.py@43:98`](/_rsruntime/lib/rs_userio.py#L43)
> Appends a tellraw text to self  
> text is the text to show unless type is:
>> SELECTOR, in which case text is the selector type  
>> SCORE, in which case text is the name of the player  
>> KEYBIND, in which case text is the ID of the keybind
> fmt is the formatting to apply to the text  
> insertion is text that is entered into the user's chat-box when the text is shift-clicked  
> type should be self-explanatory  
> objective is None unless type is SCORE, in which case objective is the scoreboard objective  
> click_event is either a ClickEvent or None for nothing
>> click_contents is the text to use for the click_event (the URL to open, text to copy, etc.)
> hover_event is either a HoverEvent or None for nothing
>> hover_contents is the data to use for the hover_event (the entity to display, the TellRaw to show [as text])