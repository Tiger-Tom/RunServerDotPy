# `Util` (`RunServer.Util` | `RS.U`)
[Standalone doc: parts/RunServer/RunServer.Util.md](RunServer.Util.md)  

## `BetterPPrinter` (`RunServer.Util.BetterPPrinter` | `RS.U.BetterPPrinter`)
[`_rsruntime/util/betterprettyprinter.py`](/_rsruntime/util/betterprettyprinter.py "Source")  
[Standalone doc: parts/RunServer/Util/RunServer.Util.BetterPPrinter.md](RunServer.Util.BetterPPrinter.md)  

### format(...)
```python
@staticmethod
def format(self, obj, _indent_: int = 0) -> Generator[str, None, None]
```

[`_rsruntime/util/betterprettyprinter.py@35:67`](/_rsruntime/util/betterprettyprinter.py#L35)
> <no doc>

### formats(...)
```python
@staticmethod
def formats(self, obj, joiner: str = '') -> str
```

[`_rsruntime/util/betterprettyprinter.py@68:69`](/_rsruntime/util/betterprettyprinter.py#L68)

<details>
<summary>Source Code</summary>

```python
def formats(self, obj, joiner: str = '') -> str:
    return joiner.join(self.format(obj))
```
</details>

> <no doc>

### writes(...)
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

[`_rsruntime/util/betterprettyprinter.py@70:78`](/_rsruntime/util/betterprettyprinter.py#L70)

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

## `Hooks` (`RunServer.Util.Hooks` | `RS.U.Hooks`)
[`_rsruntime/util/hooks.py`](/_rsruntime/util/hooks.py "Source")  
[Standalone doc: parts/RunServer/Util/RunServer.Util.Hooks.md](RunServer.Util.Hooks.md)  
> The most caustic generic hooks class
>> Has no difference in behavior from GenericHooks other than typehinting
>>> basically syntactic sugar for dict[typing.Hashable, typing.Callable]
> Also serves as a container for the other types of hooks

### register(...)
```python
@staticmethod
def register(self, hook: HookType, callback: FuncType)
```

[`_rsruntime/util/hooks.py@22:25`](/_rsruntime/util/hooks.py#L22)

<details>
<summary>Source Code</summary>

```python
def register(self, hook: HookType, callback: FuncType):
    '''Adds a callback to be called by __call__(hook)'''
    if hook not in self.hooks: self.hooks[hook] = set()
    self.hooks[hook].add(callback)
```
</details>

> Adds a callback to be called by __call__(hook)

### unregister(...)
```python
@staticmethod
def unregister(self, hook: HookType, callback: FuncType)
```

[`_rsruntime/util/hooks.py@26:29`](/_rsruntime/util/hooks.py#L26)

<details>
<summary>Source Code</summary>

```python
def unregister(self, hook: HookType, callback: FuncType):
    '''Removes a callback that would be called by __call__(hook) (if it exists)'''
    if hook not in self.hooks: return
    self.hooks[hook].remove(callback)
```
</details>

> Removes a callback that would be called by __call__(hook) (if it exists)

### unregister_hook(...)
```python
@staticmethod
def unregister_hook(self, hook: HookType)
```

[`_rsruntime/util/hooks.py@30:33`](/_rsruntime/util/hooks.py#L30)

<details>
<summary>Source Code</summary>

```python
def unregister_hook(self, hook: HookType):
    '''Deletes all callbacks that would be called by __call__(hook)'''
    if hook not in self.hooks: return
    del self.hooks[hook]
```
</details>

> Deletes all callbacks that would be called by __call__(hook)

## `INIBackedDict` (`RunServer.Util.INIBackedDict` | `RS.U.INIBackedDict`)
[`_rsruntime/util/fbd.py`](/_rsruntime/util/fbd.py "Source")  
[Standalone doc: parts/RunServer/Util/RunServer.Util.INIBackedDict.md](RunServer.Util.INIBackedDict.md)  
> A FileBackedDict implementation that uses ConfigParser as a backend

### bettergetter(...)
```python
@staticmethod
def bettergetter(...) -> Deserialized | Any
```
<details>
<summary>Parameters...</summary>

```python
    self, key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Any = Behavior.RAISE,
    set_default: bool = True
```
</details>

[`_rsruntime/util/fbd.py@137:153`](/_rsruntime/util/fbd.py#L137)

<details>
<summary>Source Code</summary>

```python
def bettergetter(self, key: Key, default: typing.ForwardRef('FileBackedDict.Behavior.RAISE') | typing.Any = Behavior.RAISE, set_default: bool = True) -> Deserialized | typing.Any:
    '''
        Gets the value of key
            If the key is missing, then:
                if default is Behavior.RAISE: raises KeyError
                otherwise: returns default, and if set_default is truthy then sets the key to default
    '''
    key = self.key(key)
    _tree = self._gettree(key, make_if_missing=(default is not self.Behavior.RAISE) and set_default, fetch_if_missing=True, no_raise_keyerror=(default is not self.Behavior.RAISE))
    self._validate_transaction(key, self._transaction_types.PRE_GETITEM, _tree=_tree)
    if _tree is None: return default
    if key[-1] in _tree:
        val = _tree[key[-1]]
        self._validate_transaction(key, self._transaction_types.POST_GETITEM, (val,), _tree=_tree)
        return self._deserialize(val)
    if set_default: self.setitem(key, default, _tree=_tree)
    return default
```
</details>

> Gets the value of key  
> If the key is missing, then:
>> if default is Behavior.RAISE: raises KeyError  
>> otherwise: returns default, and if set_default is truthy then sets the key to default

### contains(...)
```python
@staticmethod
def contains(self, key: Key, _tree: MutableMapping | None = None) -> bool
```

[`_rsruntime/util/fbd.py@188:194`](/_rsruntime/util/fbd.py#L188)

<details>
<summary>Source Code</summary>

```python
@locked
def contains(self, key: Key, *, _tree: MutableMapping | None = None) -> bool:
    '''Returns whether or not the key exists'''
    key = self.key(key) if (_tree is None) else key
    sect = self._gettree(key, make_if_missing=False, fetch_if_missing=True, no_raise_keyerror=True) if (_tree is None) else _tree
    if (sect is None) or (key[-1] not in sect): return False
    return True
```
</details>

> Returns whether or not the key exists

### get(...)
```python
@staticmethod
def get(...) -> Deserialized
```
<details>
<summary>Parameters...</summary>

```python
    self, key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Serializable = Behavior.RAISE,
    _tree: MutableMapping | None = None
```
</details>

[`_rsruntime/util/fbd.py@160:175`](/_rsruntime/util/fbd.py#L160)

<details>
<summary>Source Code</summary>

```python
@locked
def get(self, key: Key, default: typing.ForwardRef('FileBackedDict.Behavior.RAISE') | Serializable = Behavior.RAISE, *, _tree: MutableMapping | None = None) -> Deserialized:
    '''
        Gets the value of key
            If the key is missing, then raises KeyError if default is Behavior.RAISE, otherwise returns default
    '''
    key = self.key(key) if (_tree is None) else key
    sect = _tree if (_tree is not None) else \
           self._gettree(key, make_if_missing=False, fetch_if_missing=True, no_raise_keyerror=(default is not self.Behavior.RAISE))
    self._validate_transaction(key, self._transaction_types.PRE_GETITEM, _tree=sect)
    if sect is None: return default
    if key[-1] not in sect:
        raise KeyError(f'{key}[-1]')
    val = sect[key[-1]]
    self._validate_transaction(key, self._transaction_types.POST_GETITEM, (val,), _tree=_tree)
    return self._deserialize(sect[key[-1]])
```
</details>

> Gets the value of key  
> If the key is missing, then raises KeyError if default is Behavior.RAISE, otherwise returns default

### get(...)
```python
@staticmethod
def get(...) -> Deserialized
```
<details>
<summary>Parameters...</summary>

```python
    self, key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Serializable = Behavior.RAISE,
    _tree: MutableMapping | None = None
```
</details>

[`_rsruntime/util/fbd.py@160:175`](/_rsruntime/util/fbd.py#L160)

<details>
<summary>Source Code</summary>

```python
@locked
def get(self, key: Key, default: typing.ForwardRef('FileBackedDict.Behavior.RAISE') | Serializable = Behavior.RAISE, *, _tree: MutableMapping | None = None) -> Deserialized:
    '''
        Gets the value of key
            If the key is missing, then raises KeyError if default is Behavior.RAISE, otherwise returns default
    '''
    key = self.key(key) if (_tree is None) else key
    sect = _tree if (_tree is not None) else \
           self._gettree(key, make_if_missing=False, fetch_if_missing=True, no_raise_keyerror=(default is not self.Behavior.RAISE))
    self._validate_transaction(key, self._transaction_types.PRE_GETITEM, _tree=sect)
    if sect is None: return default
    if key[-1] not in sect:
        raise KeyError(f'{key}[-1]')
    val = sect[key[-1]]
    self._validate_transaction(key, self._transaction_types.POST_GETITEM, (val,), _tree=_tree)
    return self._deserialize(sect[key[-1]])
```
</details>

> Gets the value of key  
> If the key is missing, then raises KeyError if default is Behavior.RAISE, otherwise returns default

### is_autosyncing(...)
```python
@staticmethod
def is_autosyncing(self) -> bool
```

[`_rsruntime/util/fbd.py@97:100`](/_rsruntime/util/fbd.py#L97)

<details>
<summary>Source Code</summary>

```python
@locked
def is_autosyncing(self) -> bool:
    '''Returns whether or not the internal watchdog timer is ticking'''
    return self.watchdog.is_alive()
```
</details>

> Returns whether or not the internal watchdog timer is ticking

### items_full(...)
```python
@staticmethod
def items_full(self, start_key: Key, key_join: bool = True) -> Generator[tuple[str | tuple[str, ...], Deserialized], None, None]
```

[`_rsruntime/util/fbd.py@197:200`](/_rsruntime/util/fbd.py#L197)

<details>
<summary>Source Code</summary>

```python
@locked
def items_full(self, start_key: Key, key_join: bool = True) -> typing.Generator[tuple[str | tuple[str, ...], Deserialized], None, None]:
    '''Iterates over every (key, value) pair, yielding the entire key'''
    yield from ((k, self[k]) for k in self.keys(start_key, key_join))
```
</details>

> Iterates over every (key, value) pair, yielding the entire key

### items_short(...)
```python
@staticmethod
def items_short(self, start_key: Key)
```

[`_rsruntime/util/fbd.py@201:204`](/_rsruntime/util/fbd.py#L201)

<details>
<summary>Source Code</summary>

```python
@locked
def items_short(self, start_key: Key):
    '''Iterates over every (key, value) pair, yielding the last part of the key'''
    yield from ((k[-1], self[k]) for k in self.keys(start_key, False))
```
</details>

> Iterates over every (key, value) pair, yielding the last part of the key

### key(...)
```python
@classmethod
def key(key: Key, top_level: bool = False) -> tuple[str, Ellipsis]
```

[`_rsruntime/util/fbd.py@65:78`](/_rsruntime/util/fbd.py#L65)

<details>
<summary>Source Code</summary>

```python
@classmethod
def key(cls, key: Key, *, top_level: bool = False) -> tuple[str, ...]: # key key key
    '''Transform a string / tuple of strings into a key'''
    if isinstance(key, str): key = key.split(cls.key_sep)
    if not key: raise ValueError('Empty key')
    if any(cls.key_sep in part for part in key):
        raise ValueError(f'Part of {key} contains a "{cls.key_sep}"')
    elif (not top_level) and (len(key) == 1):
        raise ValueError('Top-level key disallowed')
    elif not cls.key_topp_patt.fullmatch(key[0]):
        raise ValueError(f'Top-level part of key {key} does not match pattern {cls.key_topp_patt.pattern}')
    elif not all(map(cls.key_part_patt.fullmatch, key[1:])):
        raise ValueError(f'Part of sub-key {key[1:]} (full: {key}) not match pattern {cls.key_part_patt.pattern}')
    return tuple(key)
```
</details>

> Transform a string / tuple of strings into a key

### keys(...)
```python
@staticmethod
def keys(self, start_key: Key | None = None, key_join: bool = True) -> Generator[str | tuple[str, ...], None, None]
```

[`_rsruntime/util/fbd.py@205:214`](/_rsruntime/util/fbd.py#L205)

<details>
<summary>Source Code</summary>

```python
@locked
def keys(self, start_key: Key | None = None, key_join: bool = True) -> typing.Generator[str | tuple[str, ...], None, None]:
    '''Iterates over every key'''
    if start_key is None:
        skey = ()
        target = self._data
    else:
        skey = self.key(start_key, top_level=True)
        target = self._gettree(skey+(None,), make_if_missing=False)
    yield from map((lambda k: self.key_sep.join(skey+(k,))) if key_join else (lambda k: skey+(k,)), target.keys())
```
</details>

> Iterates over every key

### path_from_topkey(...)
```python
@staticmethod
def path_from_topkey(self, topkey: str)
```

[`_rsruntime/util/fbd.py@79:81`](/_rsruntime/util/fbd.py#L79)

<details>
<summary>Source Code</summary>

```python
def path_from_topkey(self, topkey: str):
    '''Returns the Path corresponding to the top-key's file'''
    return (self.path / topkey).with_suffix(self.file_suffix)
```
</details>

> Returns the Path corresponding to the top-key's file

### readin(...)
```python
@staticmethod
def readin(self, topkey: str)
```

[`_rsruntime/util/fbd.py@127:132`](/_rsruntime/util/fbd.py#L127)

<details>
<summary>Source Code</summary>

```python
@locked
def readin(self, topkey: str):
    '''Reads in a top-level key'''
    path = self.path_from_topkey(topkey)
    self._from_string(topkey, path.read_text())
    self.mtimes[topkey] = path.stat().st_mtime
```
</details>

> Reads in a top-level key

### readin_modified(...)
```python
@staticmethod
def readin_modified(self)
```

[`_rsruntime/util/fbd.py@116:126`](/_rsruntime/util/fbd.py#L116)

<details>
<summary>Source Code</summary>

```python
@locked
def readin_modified(self):
    '''Reads in top-level keys that have been changed'''
    for tk,tm in self.mtimes.items():
        p = self.path_from_topkey(tk)
        if not p.exists():
            del self.mtimes[tk]
        nt = p.stat().st_mtime
        if nt == tm: continue
        self.mtimes[tk] = tm
        self._from_string(tk, p.read_text())
```
</details>

> Reads in top-level keys that have been changed

### setitem(...)
```python
@staticmethod
def setitem(...)
```
<details>
<summary>Parameters...</summary>

```python
    self, key: Key, val: Serializable,
    _tree: MutableMapping | None = None
```
</details>

[`_rsruntime/util/fbd.py@178:185`](/_rsruntime/util/fbd.py#L178)

<details>
<summary>Source Code</summary>

```python
@locked
def setitem(self, key: Key, val: Serializable, *, _tree: MutableMapping | None = None):
    '''Sets a key to a value'''
    key = self.key(key) if (_tree is None) else key
    sect = (self._gettree(key, make_if_missing=True, fetch_if_missing=True) if (_tree is None) else _tree)
    self._validate_transaction(key, self._transaction_types.SETITEM, (val,), _tree=sect)
    sect[key[-1]] = self._serialize(val)
    self.dirty.add(key[0])
```
</details>

> Sets a key to a value

### sort(...)
```python
@staticmethod
def sort(self, by: Callable(str | tuple[str, ...]) -> Any = <lambda>)
```

[`_rsruntime/util/fbd.py@277:283`](/_rsruntime/util/fbd.py#L277)

<details>
<summary>Source Code</summary>

```python
def sort(self, by: typing.Callable[[str | tuple[str, ...]], typing.Any] = lambda k: k):
    '''Sorts the data of this INIBackedDict in-place, marking all touched sections as dirty'''
    for top,cfg in self._data.items():
        self.dirty.add(top)
        cfg._sections = dict(sorted(cfg._sections.items(), key=lambda it: by((it[0],))))
        for sname,ssect in cfg._sections.items():
            cfg._sections[sname] = dict(sorted(ssect.items(), key=lambda it: by(tuple(it[0].split('.')))))
```
</details>

> Sorts the data of this INIBackedDict in-place, marking all touched sections as dirty

### start_autosync(...)
```python
@staticmethod
def start_autosync(self)
```

[`_rsruntime/util/fbd.py@89:92`](/_rsruntime/util/fbd.py#L89)

<details>
<summary>Source Code</summary>

```python
@locked
def start_autosync(self):
    '''Starts the internal watchdog timer'''
    self.watchdog.start()
```
</details>

> Starts the internal watchdog timer

### stop_autosync(...)
```python
@staticmethod
def stop_autosync(self)
```

[`_rsruntime/util/fbd.py@93:96`](/_rsruntime/util/fbd.py#L93)

<details>
<summary>Source Code</summary>

```python
@locked
def stop_autosync(self):
    '''Stops the internal watchdog timer'''
    self.watchdog.stop()
```
</details>

> Stops the internal watchdog timer

### sync(...)
```python
@staticmethod
def sync(self)
```

[`_rsruntime/util/fbd.py@83:87`](/_rsruntime/util/fbd.py#L83)

<details>
<summary>Source Code</summary>

```python
@locked
def sync(self):
    '''Convenience method for writeback_dirty and readin_modified'''
    self.writeback_dirty()
    self.readin_modified()
```
</details>

> Convenience method for writeback_dirty and readin_modified

### values(...)
```python
@staticmethod
def values(self, start_key: Key) -> Generator[[Deserialized], None, None]
```

[`_rsruntime/util/fbd.py@216:219`](/_rsruntime/util/fbd.py#L216)

<details>
<summary>Source Code</summary>

```python
@locked
def values(self, start_key: Key) -> typing.Generator[[Deserialized], None, None]:
    '''Iterates over every value'''
    yield from map(self.getitem, self.keys(start_key))
```
</details>

> Iterates over every value

### writeback(...)
```python
@staticmethod
def writeback(...)
```
<details>
<summary>Parameters...</summary>

```python
    self, topkey: str, only_if_dirty: bool = True,
    clean: bool = True
```
</details>

[`_rsruntime/util/fbd.py@106:112`](/_rsruntime/util/fbd.py#L106)

<details>
<summary>Source Code</summary>

```python
@locked
def writeback(self, topkey: str, *, only_if_dirty: bool = True, clean: bool = True):
    '''Writes back a top-level key'''
    if topkey in self.dirty:
        if clean: self.dirty.remove(topkey)
    elif only_if_dirty: return
    self.path_from_topkey(topkey).write_text(self._to_string(topkey))
```
</details>

> Writes back a top-level key

### writeback_dirty(...)
```python
@staticmethod
def writeback_dirty(self)
```

[`_rsruntime/util/fbd.py@102:105`](/_rsruntime/util/fbd.py#L102)

<details>
<summary>Source Code</summary>

```python
@locked
def writeback_dirty(self):
    while self.dirty:
        self.writeback(self.dirty.pop(), only_if_dirty=False, clean=False)
```
</details>

> <no doc>

## `JSONBackedDict` (`RunServer.Util.JSONBackedDict` | `RS.U.JSONBackedDict`)
[`_rsruntime/util/fbd.py`](/_rsruntime/util/fbd.py "Source")  
[Standalone doc: parts/RunServer/Util/RunServer.Util.JSONBackedDict.md](RunServer.Util.JSONBackedDict.md)  
> A FileBackedDict implementation that uses JSON as a backend

### bettergetter(...)
```python
@staticmethod
def bettergetter(...) -> Deserialized | Any
```
<details>
<summary>Parameters...</summary>

```python
    self, key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Any = Behavior.RAISE,
    set_default: bool = True
```
</details>

[`_rsruntime/util/fbd.py@137:153`](/_rsruntime/util/fbd.py#L137)

<details>
<summary>Source Code</summary>

```python
def bettergetter(self, key: Key, default: typing.ForwardRef('FileBackedDict.Behavior.RAISE') | typing.Any = Behavior.RAISE, set_default: bool = True) -> Deserialized | typing.Any:
    '''
        Gets the value of key
            If the key is missing, then:
                if default is Behavior.RAISE: raises KeyError
                otherwise: returns default, and if set_default is truthy then sets the key to default
    '''
    key = self.key(key)
    _tree = self._gettree(key, make_if_missing=(default is not self.Behavior.RAISE) and set_default, fetch_if_missing=True, no_raise_keyerror=(default is not self.Behavior.RAISE))
    self._validate_transaction(key, self._transaction_types.PRE_GETITEM, _tree=_tree)
    if _tree is None: return default
    if key[-1] in _tree:
        val = _tree[key[-1]]
        self._validate_transaction(key, self._transaction_types.POST_GETITEM, (val,), _tree=_tree)
        return self._deserialize(val)
    if set_default: self.setitem(key, default, _tree=_tree)
    return default
```
</details>

> Gets the value of key  
> If the key is missing, then:
>> if default is Behavior.RAISE: raises KeyError  
>> otherwise: returns default, and if set_default is truthy then sets the key to default

### contains(...)
```python
@staticmethod
def contains(self, key: Key, _tree: MutableMapping | None = None) -> bool
```

[`_rsruntime/util/fbd.py@188:194`](/_rsruntime/util/fbd.py#L188)

<details>
<summary>Source Code</summary>

```python
@locked
def contains(self, key: Key, *, _tree: MutableMapping | None = None) -> bool:
    '''Returns whether or not the key exists'''
    key = self.key(key) if (_tree is None) else key
    sect = self._gettree(key, make_if_missing=False, fetch_if_missing=True, no_raise_keyerror=True) if (_tree is None) else _tree
    if (sect is None) or (key[-1] not in sect): return False
    return True
```
</details>

> Returns whether or not the key exists

### get(...)
```python
@staticmethod
def get(...) -> Deserialized
```
<details>
<summary>Parameters...</summary>

```python
    self, key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Serializable = Behavior.RAISE,
    _tree: MutableMapping | None = None
```
</details>

[`_rsruntime/util/fbd.py@160:175`](/_rsruntime/util/fbd.py#L160)

<details>
<summary>Source Code</summary>

```python
@locked
def get(self, key: Key, default: typing.ForwardRef('FileBackedDict.Behavior.RAISE') | Serializable = Behavior.RAISE, *, _tree: MutableMapping | None = None) -> Deserialized:
    '''
        Gets the value of key
            If the key is missing, then raises KeyError if default is Behavior.RAISE, otherwise returns default
    '''
    key = self.key(key) if (_tree is None) else key
    sect = _tree if (_tree is not None) else \
           self._gettree(key, make_if_missing=False, fetch_if_missing=True, no_raise_keyerror=(default is not self.Behavior.RAISE))
    self._validate_transaction(key, self._transaction_types.PRE_GETITEM, _tree=sect)
    if sect is None: return default
    if key[-1] not in sect:
        raise KeyError(f'{key}[-1]')
    val = sect[key[-1]]
    self._validate_transaction(key, self._transaction_types.POST_GETITEM, (val,), _tree=_tree)
    return self._deserialize(sect[key[-1]])
```
</details>

> Gets the value of key  
> If the key is missing, then raises KeyError if default is Behavior.RAISE, otherwise returns default

### get(...)
```python
@staticmethod
def get(...) -> Deserialized
```
<details>
<summary>Parameters...</summary>

```python
    self, key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Serializable = Behavior.RAISE,
    _tree: MutableMapping | None = None
```
</details>

[`_rsruntime/util/fbd.py@160:175`](/_rsruntime/util/fbd.py#L160)

<details>
<summary>Source Code</summary>

```python
@locked
def get(self, key: Key, default: typing.ForwardRef('FileBackedDict.Behavior.RAISE') | Serializable = Behavior.RAISE, *, _tree: MutableMapping | None = None) -> Deserialized:
    '''
        Gets the value of key
            If the key is missing, then raises KeyError if default is Behavior.RAISE, otherwise returns default
    '''
    key = self.key(key) if (_tree is None) else key
    sect = _tree if (_tree is not None) else \
           self._gettree(key, make_if_missing=False, fetch_if_missing=True, no_raise_keyerror=(default is not self.Behavior.RAISE))
    self._validate_transaction(key, self._transaction_types.PRE_GETITEM, _tree=sect)
    if sect is None: return default
    if key[-1] not in sect:
        raise KeyError(f'{key}[-1]')
    val = sect[key[-1]]
    self._validate_transaction(key, self._transaction_types.POST_GETITEM, (val,), _tree=_tree)
    return self._deserialize(sect[key[-1]])
```
</details>

> Gets the value of key  
> If the key is missing, then raises KeyError if default is Behavior.RAISE, otherwise returns default

### is_autosyncing(...)
```python
@staticmethod
def is_autosyncing(self) -> bool
```

[`_rsruntime/util/fbd.py@97:100`](/_rsruntime/util/fbd.py#L97)

<details>
<summary>Source Code</summary>

```python
@locked
def is_autosyncing(self) -> bool:
    '''Returns whether or not the internal watchdog timer is ticking'''
    return self.watchdog.is_alive()
```
</details>

> Returns whether or not the internal watchdog timer is ticking

### items_full(...)
```python
@staticmethod
def items_full(self, start_key: Key, key_join: bool = True) -> Generator[tuple[str | tuple[str, ...], Deserialized], None, None]
```

[`_rsruntime/util/fbd.py@197:200`](/_rsruntime/util/fbd.py#L197)

<details>
<summary>Source Code</summary>

```python
@locked
def items_full(self, start_key: Key, key_join: bool = True) -> typing.Generator[tuple[str | tuple[str, ...], Deserialized], None, None]:
    '''Iterates over every (key, value) pair, yielding the entire key'''
    yield from ((k, self[k]) for k in self.keys(start_key, key_join))
```
</details>

> Iterates over every (key, value) pair, yielding the entire key

### items_short(...)
```python
@staticmethod
def items_short(self, start_key: Key)
```

[`_rsruntime/util/fbd.py@201:204`](/_rsruntime/util/fbd.py#L201)

<details>
<summary>Source Code</summary>

```python
@locked
def items_short(self, start_key: Key):
    '''Iterates over every (key, value) pair, yielding the last part of the key'''
    yield from ((k[-1], self[k]) for k in self.keys(start_key, False))
```
</details>

> Iterates over every (key, value) pair, yielding the last part of the key

### key(...)
```python
@classmethod
def key(key: Key, top_level: bool = False) -> tuple[str, Ellipsis]
```

[`_rsruntime/util/fbd.py@65:78`](/_rsruntime/util/fbd.py#L65)

<details>
<summary>Source Code</summary>

```python
@classmethod
def key(cls, key: Key, *, top_level: bool = False) -> tuple[str, ...]: # key key key
    '''Transform a string / tuple of strings into a key'''
    if isinstance(key, str): key = key.split(cls.key_sep)
    if not key: raise ValueError('Empty key')
    if any(cls.key_sep in part for part in key):
        raise ValueError(f'Part of {key} contains a "{cls.key_sep}"')
    elif (not top_level) and (len(key) == 1):
        raise ValueError('Top-level key disallowed')
    elif not cls.key_topp_patt.fullmatch(key[0]):
        raise ValueError(f'Top-level part of key {key} does not match pattern {cls.key_topp_patt.pattern}')
    elif not all(map(cls.key_part_patt.fullmatch, key[1:])):
        raise ValueError(f'Part of sub-key {key[1:]} (full: {key}) not match pattern {cls.key_part_patt.pattern}')
    return tuple(key)
```
</details>

> Transform a string / tuple of strings into a key

### keys(...)
```python
@staticmethod
def keys(self, start_key: Key | None = None, key_join: bool = True) -> Generator[str | tuple[str, ...], None, None]
```

[`_rsruntime/util/fbd.py@205:214`](/_rsruntime/util/fbd.py#L205)

<details>
<summary>Source Code</summary>

```python
@locked
def keys(self, start_key: Key | None = None, key_join: bool = True) -> typing.Generator[str | tuple[str, ...], None, None]:
    '''Iterates over every key'''
    if start_key is None:
        skey = ()
        target = self._data
    else:
        skey = self.key(start_key, top_level=True)
        target = self._gettree(skey+(None,), make_if_missing=False)
    yield from map((lambda k: self.key_sep.join(skey+(k,))) if key_join else (lambda k: skey+(k,)), target.keys())
```
</details>

> Iterates over every key

### path_from_topkey(...)
```python
@staticmethod
def path_from_topkey(self, topkey: str)
```

[`_rsruntime/util/fbd.py@79:81`](/_rsruntime/util/fbd.py#L79)

<details>
<summary>Source Code</summary>

```python
def path_from_topkey(self, topkey: str):
    '''Returns the Path corresponding to the top-key's file'''
    return (self.path / topkey).with_suffix(self.file_suffix)
```
</details>

> Returns the Path corresponding to the top-key's file

### readin(...)
```python
@staticmethod
def readin(self, topkey: str)
```

[`_rsruntime/util/fbd.py@127:132`](/_rsruntime/util/fbd.py#L127)

<details>
<summary>Source Code</summary>

```python
@locked
def readin(self, topkey: str):
    '''Reads in a top-level key'''
    path = self.path_from_topkey(topkey)
    self._from_string(topkey, path.read_text())
    self.mtimes[topkey] = path.stat().st_mtime
```
</details>

> Reads in a top-level key

### readin_modified(...)
```python
@staticmethod
def readin_modified(self)
```

[`_rsruntime/util/fbd.py@116:126`](/_rsruntime/util/fbd.py#L116)

<details>
<summary>Source Code</summary>

```python
@locked
def readin_modified(self):
    '''Reads in top-level keys that have been changed'''
    for tk,tm in self.mtimes.items():
        p = self.path_from_topkey(tk)
        if not p.exists():
            del self.mtimes[tk]
        nt = p.stat().st_mtime
        if nt == tm: continue
        self.mtimes[tk] = tm
        self._from_string(tk, p.read_text())
```
</details>

> Reads in top-level keys that have been changed

### setitem(...)
```python
@staticmethod
def setitem(...)
```
<details>
<summary>Parameters...</summary>

```python
    self, key: Key, val: Serializable,
    _tree: MutableMapping | None = None
```
</details>

[`_rsruntime/util/fbd.py@178:185`](/_rsruntime/util/fbd.py#L178)

<details>
<summary>Source Code</summary>

```python
@locked
def setitem(self, key: Key, val: Serializable, *, _tree: MutableMapping | None = None):
    '''Sets a key to a value'''
    key = self.key(key) if (_tree is None) else key
    sect = (self._gettree(key, make_if_missing=True, fetch_if_missing=True) if (_tree is None) else _tree)
    self._validate_transaction(key, self._transaction_types.SETITEM, (val,), _tree=sect)
    sect[key[-1]] = self._serialize(val)
    self.dirty.add(key[0])
```
</details>

> Sets a key to a value

### sort(...)
```python
@staticmethod
def sort(self, by: Callable(tuple[str, Ellipsis]) -> Any = <lambda>)
```

[`_rsruntime/util/fbd.py@374:378`](/_rsruntime/util/fbd.py#L374)

<details>
<summary>Source Code</summary>

```python
def sort(self, by: typing.Callable[[tuple[str, ...]], typing.Any] = lambda k: k):
    '''Sorts the data of this JSONBackedDict (semi-)in-place, marking all touched sections as dirty'''
    for top,dat in self._data.items():
        self.dirty.add(top)
        self._data[top] = self._sorteddict(dat, (top,), by)
```
</details>

> Sorts the data of this JSONBackedDict (semi-)in-place, marking all touched sections as dirty

### start_autosync(...)
```python
@staticmethod
def start_autosync(self)
```

[`_rsruntime/util/fbd.py@89:92`](/_rsruntime/util/fbd.py#L89)

<details>
<summary>Source Code</summary>

```python
@locked
def start_autosync(self):
    '''Starts the internal watchdog timer'''
    self.watchdog.start()
```
</details>

> Starts the internal watchdog timer

### stop_autosync(...)
```python
@staticmethod
def stop_autosync(self)
```

[`_rsruntime/util/fbd.py@93:96`](/_rsruntime/util/fbd.py#L93)

<details>
<summary>Source Code</summary>

```python
@locked
def stop_autosync(self):
    '''Stops the internal watchdog timer'''
    self.watchdog.stop()
```
</details>

> Stops the internal watchdog timer

### sync(...)
```python
@staticmethod
def sync(self)
```

[`_rsruntime/util/fbd.py@83:87`](/_rsruntime/util/fbd.py#L83)

<details>
<summary>Source Code</summary>

```python
@locked
def sync(self):
    '''Convenience method for writeback_dirty and readin_modified'''
    self.writeback_dirty()
    self.readin_modified()
```
</details>

> Convenience method for writeback_dirty and readin_modified

### values(...)
```python
@staticmethod
def values(self, start_key: Key) -> Generator[[Deserialized], None, None]
```

[`_rsruntime/util/fbd.py@216:219`](/_rsruntime/util/fbd.py#L216)

<details>
<summary>Source Code</summary>

```python
@locked
def values(self, start_key: Key) -> typing.Generator[[Deserialized], None, None]:
    '''Iterates over every value'''
    yield from map(self.getitem, self.keys(start_key))
```
</details>

> Iterates over every value

### writeback(...)
```python
@staticmethod
def writeback(...)
```
<details>
<summary>Parameters...</summary>

```python
    self, topkey: str, only_if_dirty: bool = True,
    clean: bool = True
```
</details>

[`_rsruntime/util/fbd.py@106:112`](/_rsruntime/util/fbd.py#L106)

<details>
<summary>Source Code</summary>

```python
@locked
def writeback(self, topkey: str, *, only_if_dirty: bool = True, clean: bool = True):
    '''Writes back a top-level key'''
    if topkey in self.dirty:
        if clean: self.dirty.remove(topkey)
    elif only_if_dirty: return
    self.path_from_topkey(topkey).write_text(self._to_string(topkey))
```
</details>

> Writes back a top-level key

### writeback_dirty(...)
```python
@staticmethod
def writeback_dirty(self)
```

[`_rsruntime/util/fbd.py@102:105`](/_rsruntime/util/fbd.py#L102)

<details>
<summary>Source Code</summary>

```python
@locked
def writeback_dirty(self):
    while self.dirty:
        self.writeback(self.dirty.pop(), only_if_dirty=False, clean=False)
```
</details>

> <no doc>

## `Locker` (`RunServer.Util.Locker` | `RS.U.Locker`)
###  OR `locked_resource` (`RunServer.Util.locked_resource` | `RS.U.locked_resource`)
[Standalone doc: parts/RunServer/Util/RunServer.Util.Locker.md](RunServer.Util.Locker.md)  

### `LockedResource` (`RunServer.Util.Locker.LockedResource` | `RS.U.Locker.LockedResource`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.LockedResource.md](RunServer.Util.Locker.LockedResource.md)  
> Adds a "lock" parameter to class instances (and slots!)  
> This should be used in tandem with the @locked decorator:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock  
>>>> print("initialized!")
>>> @locked # note decorator  
>>> def test_lock(self):
>>>> print("lock acquired!")

### `basic` (`RunServer.Util.Locker.basic` | `RS.U.Locker.basic`)
####  OR `b` (`RunServer.Util.Locker.b` | `RS.U.Locker.b`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.basic.md](RunServer.Util.Locker.basic.md)  
> basic(LockedResource, LR, locked, lockd)

#### locked(...)
```python
@staticmethod
def locked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@76:92`](/_rsruntime/util/locked_resource.py#L76)

<details>
<summary>Source Code</summary>

```python
def locked(func: typing.Callable):
    '''
        Waits to acquire the method's self's .lock attribute (uses "with")
        This should be used in tandem with the LockedResource superclass:
            class DemoLocked(LockedResource): # note subclass
                def __init__(self):
                    super().__init__() # note super init, needed to setup .lock
                    print("initialized!")
                @locked # note decorator
                def test_lock(self):
                    print("lock acquired!")
    '''
    @wraps(func)
    def locked_func(self: LockedResource, *args, **kwargs):
        with self.lock:
            return func(self, *args, **kwargs)
    return locked_func
```
</details>

> Waits to acquire the method's self's .lock attribute (uses "with")  
> This should be used in tandem with the LockedResource superclass:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock  
>>>> print("initialized!")
>>> @locked # note decorator  
>>> def test_lock(self):
>>>> print("lock acquired!")

#### locked(...)
```python
@staticmethod
def locked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@76:92`](/_rsruntime/util/locked_resource.py#L76)

<details>
<summary>Source Code</summary>

```python
def locked(func: typing.Callable):
    '''
        Waits to acquire the method's self's .lock attribute (uses "with")
        This should be used in tandem with the LockedResource superclass:
            class DemoLocked(LockedResource): # note subclass
                def __init__(self):
                    super().__init__() # note super init, needed to setup .lock
                    print("initialized!")
                @locked # note decorator
                def test_lock(self):
                    print("lock acquired!")
    '''
    @wraps(func)
    def locked_func(self: LockedResource, *args, **kwargs):
        with self.lock:
            return func(self, *args, **kwargs)
    return locked_func
```
</details>

> Waits to acquire the method's self's .lock attribute (uses "with")  
> This should be used in tandem with the LockedResource superclass:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock  
>>>> print("initialized!")
>>> @locked # note decorator  
>>> def test_lock(self):
>>>> print("lock acquired!")

### `cls` (`RunServer.Util.Locker.cls` | `RS.U.Locker.cls`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.cls.md](RunServer.Util.Locker.cls.md)  
> cls(LockedClass, LC, classlocked, clslockd, iclasslocked, iclslockd)

#### LockedClass(...)
```python
@staticmethod
def LockedClass(lock_class: AbstractContextManager = RLock, I_KNOW_WHAT_IM_DOING: bool = False)
```

[`_rsruntime/util/locked_resource.py@52:74`](/_rsruntime/util/locked_resource.py#L52)
> Adds a "classlock" class variable  
> This should be used in tandem with either the @classlocked or @iclasslocked decorators
>> see help(classlockd) or help(iclasslocked) for real demo code
> Note that, unless you pass I_KNOW_WHAT_IM_DOING=True, lock_class is instantiated immediately in order to check if it is an instance of AbstractContextManager
>> This is to try to help emit a warning if LockedClass is used on a user class without being called (@LockedClass instead of @LockedClass())  
>> The lock_class must be instantiated to check, as threading.RLock and threading.Lock are actually functions  
>> I_KNOW_WHAT_IM_DOING=True disables both the immediate instantiation of lock_class, the isinstance check, and the warning
> lock_class is the type of lock (or really any context manager will do) to use (defaults to RLock)  
> Short demo code:
>> @LockedClass()  
>> class Locked: ...
> or, to use a custom lock:
>> @LockedClass(threading.Semaphore)  
>> class CustomLocked: ...

#### LockedClass(...)
```python
@staticmethod
def LockedClass(lock_class: AbstractContextManager = RLock, I_KNOW_WHAT_IM_DOING: bool = False)
```

[`_rsruntime/util/locked_resource.py@52:74`](/_rsruntime/util/locked_resource.py#L52)
> Adds a "classlock" class variable  
> This should be used in tandem with either the @classlocked or @iclasslocked decorators
>> see help(classlockd) or help(iclasslocked) for real demo code
> Note that, unless you pass I_KNOW_WHAT_IM_DOING=True, lock_class is instantiated immediately in order to check if it is an instance of AbstractContextManager
>> This is to try to help emit a warning if LockedClass is used on a user class without being called (@LockedClass instead of @LockedClass())  
>> The lock_class must be instantiated to check, as threading.RLock and threading.Lock are actually functions  
>> I_KNOW_WHAT_IM_DOING=True disables both the immediate instantiation of lock_class, the isinstance check, and the warning
> lock_class is the type of lock (or really any context manager will do) to use (defaults to RLock)  
> Short demo code:
>> @LockedClass()  
>> class Locked: ...
> or, to use a custom lock:
>> @LockedClass(threading.Semaphore)  
>> class CustomLocked: ...

#### classlocked(...)
```python
@staticmethod
def classlocked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@93:112`](/_rsruntime/util/locked_resource.py#L93)
> Similar to @locked, but uses cls's .classlock attribute  
> Does NOT imply classmethod (use @iclasslocked if you want to do that)  
> Meant to be used with the @LockedClass class decorator:
>> @LockedClass  
>> class DemoLockedClass:
>>> @classmethod # note: @classmethod BEFORE @classlocked  
>>> @classlocked # could both be replaced by a single @iclasslocked  
>>> def test_lock(cls):
>>>> print("class lock acquired!")
>>> @classlocked  
>>> def test_lock_2(self):
>>>> print("class lock acquired on non-classmethod!")

#### classlocked(...)
```python
@staticmethod
def classlocked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@93:112`](/_rsruntime/util/locked_resource.py#L93)
> Similar to @locked, but uses cls's .classlock attribute  
> Does NOT imply classmethod (use @iclasslocked if you want to do that)  
> Meant to be used with the @LockedClass class decorator:
>> @LockedClass  
>> class DemoLockedClass:
>>> @classmethod # note: @classmethod BEFORE @classlocked  
>>> @classlocked # could both be replaced by a single @iclasslocked  
>>> def test_lock(cls):
>>>> print("class lock acquired!")
>>> @classlocked  
>>> def test_lock_2(self):
>>>> print("class lock acquired on non-classmethod!")

#### iclasslocked(...)
```python
@staticmethod
def iclasslocked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@113:123`](/_rsruntime/util/locked_resource.py#L113)

<details>
<summary>Source Code</summary>

```python
def iclasslocked(func: typing.Callable):
    '''
        Is the same as @classlocked (it even calls it), but also wraps the method in classmethod
        Meant to be used with @LockedClass:
            @LockedClass()
            class Locked:
                @iclasslocked
                def classlocked_classmethod(cls):
                    print("class lock acquired!")
    '''
    return classmethod(classlocked(func))
```
</details>

> Is the same as @classlocked (it even calls it), but also wraps the method in classmethod  
> Meant to be used with @LockedClass:
>> @LockedClass()  
>> class Locked:
>>> @iclasslocked  
>>> def classlocked_classmethod(cls):
>>>> print("class lock acquired!")

#### iclasslocked(...)
```python
@staticmethod
def iclasslocked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@113:123`](/_rsruntime/util/locked_resource.py#L113)

<details>
<summary>Source Code</summary>

```python
def iclasslocked(func: typing.Callable):
    '''
        Is the same as @classlocked (it even calls it), but also wraps the method in classmethod
        Meant to be used with @LockedClass:
            @LockedClass()
            class Locked:
                @iclasslocked
                def classlocked_classmethod(cls):
                    print("class lock acquired!")
    '''
    return classmethod(classlocked(func))
```
</details>

> Is the same as @classlocked (it even calls it), but also wraps the method in classmethod  
> Meant to be used with @LockedClass:
>> @LockedClass()  
>> class Locked:
>>> @iclasslocked  
>>> def classlocked_classmethod(cls):
>>>> print("class lock acquired!")

### `cls_decors` (`RunServer.Util.Locker.cls_decors` | `RS.U.Locker.cls_decors`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.cls_decors.md](RunServer.Util.Locker.cls_decors.md)  
> cls_decors(LockedClass, LC)

#### LockedClass(...)
```python
@staticmethod
def LockedClass(lock_class: AbstractContextManager = RLock, I_KNOW_WHAT_IM_DOING: bool = False)
```

[`_rsruntime/util/locked_resource.py@52:74`](/_rsruntime/util/locked_resource.py#L52)
> Adds a "classlock" class variable  
> This should be used in tandem with either the @classlocked or @iclasslocked decorators
>> see help(classlockd) or help(iclasslocked) for real demo code
> Note that, unless you pass I_KNOW_WHAT_IM_DOING=True, lock_class is instantiated immediately in order to check if it is an instance of AbstractContextManager
>> This is to try to help emit a warning if LockedClass is used on a user class without being called (@LockedClass instead of @LockedClass())  
>> The lock_class must be instantiated to check, as threading.RLock and threading.Lock are actually functions  
>> I_KNOW_WHAT_IM_DOING=True disables both the immediate instantiation of lock_class, the isinstance check, and the warning
> lock_class is the type of lock (or really any context manager will do) to use (defaults to RLock)  
> Short demo code:
>> @LockedClass()  
>> class Locked: ...
> or, to use a custom lock:
>> @LockedClass(threading.Semaphore)  
>> class CustomLocked: ...

#### LockedClass(...)
```python
@staticmethod
def LockedClass(lock_class: AbstractContextManager = RLock, I_KNOW_WHAT_IM_DOING: bool = False)
```

[`_rsruntime/util/locked_resource.py@52:74`](/_rsruntime/util/locked_resource.py#L52)
> Adds a "classlock" class variable  
> This should be used in tandem with either the @classlocked or @iclasslocked decorators
>> see help(classlockd) or help(iclasslocked) for real demo code
> Note that, unless you pass I_KNOW_WHAT_IM_DOING=True, lock_class is instantiated immediately in order to check if it is an instance of AbstractContextManager
>> This is to try to help emit a warning if LockedClass is used on a user class without being called (@LockedClass instead of @LockedClass())  
>> The lock_class must be instantiated to check, as threading.RLock and threading.Lock are actually functions  
>> I_KNOW_WHAT_IM_DOING=True disables both the immediate instantiation of lock_class, the isinstance check, and the warning
> lock_class is the type of lock (or really any context manager will do) to use (defaults to RLock)  
> Short demo code:
>> @LockedClass()  
>> class Locked: ...
> or, to use a custom lock:
>> @LockedClass(threading.Semaphore)  
>> class CustomLocked: ...

### `etc` (`RunServer.Util.Locker.etc` | `RS.U.Locker.etc`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.etc.md](RunServer.Util.Locker.etc.md)  
> etc(locked_by, lockdby)

#### locked_by(...)
```python
@staticmethod
def locked_by(lock: AbstractContextManager)
```

[`_rsruntime/util/locked_resource.py@125:132`](/_rsruntime/util/locked_resource.py#L125)

<details>
<summary>Source Code</summary>

```python
def locked_by(lock: AbstractContextManager):
    def func_locker(func: typing.Callable):
        @wraps(func)
        def locked_func(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return locked_func
    return func_locker
```
</details>

> <no doc>

#### locked_by(...)
```python
@staticmethod
def locked_by(lock: AbstractContextManager)
```

[`_rsruntime/util/locked_resource.py@125:132`](/_rsruntime/util/locked_resource.py#L125)

<details>
<summary>Source Code</summary>

```python
def locked_by(lock: AbstractContextManager):
    def func_locker(func: typing.Callable):
        @wraps(func)
        def locked_func(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return locked_func
    return func_locker
```
</details>

> <no doc>

### `func_decors` (`RunServer.Util.Locker.func_decors` | `RS.U.Locker.func_decors`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.func_decors.md](RunServer.Util.Locker.func_decors.md)  
> func_decors(locked, lockd, classlocked, clslockd, iclasslocked, iclslockd, locked_by, lockdby)

#### classlocked(...)
```python
@staticmethod
def classlocked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@93:112`](/_rsruntime/util/locked_resource.py#L93)
> Similar to @locked, but uses cls's .classlock attribute  
> Does NOT imply classmethod (use @iclasslocked if you want to do that)  
> Meant to be used with the @LockedClass class decorator:
>> @LockedClass  
>> class DemoLockedClass:
>>> @classmethod # note: @classmethod BEFORE @classlocked  
>>> @classlocked # could both be replaced by a single @iclasslocked  
>>> def test_lock(cls):
>>>> print("class lock acquired!")
>>> @classlocked  
>>> def test_lock_2(self):
>>>> print("class lock acquired on non-classmethod!")

#### classlocked(...)
```python
@staticmethod
def classlocked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@93:112`](/_rsruntime/util/locked_resource.py#L93)
> Similar to @locked, but uses cls's .classlock attribute  
> Does NOT imply classmethod (use @iclasslocked if you want to do that)  
> Meant to be used with the @LockedClass class decorator:
>> @LockedClass  
>> class DemoLockedClass:
>>> @classmethod # note: @classmethod BEFORE @classlocked  
>>> @classlocked # could both be replaced by a single @iclasslocked  
>>> def test_lock(cls):
>>>> print("class lock acquired!")
>>> @classlocked  
>>> def test_lock_2(self):
>>>> print("class lock acquired on non-classmethod!")

#### iclasslocked(...)
```python
@staticmethod
def iclasslocked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@113:123`](/_rsruntime/util/locked_resource.py#L113)

<details>
<summary>Source Code</summary>

```python
def iclasslocked(func: typing.Callable):
    '''
        Is the same as @classlocked (it even calls it), but also wraps the method in classmethod
        Meant to be used with @LockedClass:
            @LockedClass()
            class Locked:
                @iclasslocked
                def classlocked_classmethod(cls):
                    print("class lock acquired!")
    '''
    return classmethod(classlocked(func))
```
</details>

> Is the same as @classlocked (it even calls it), but also wraps the method in classmethod  
> Meant to be used with @LockedClass:
>> @LockedClass()  
>> class Locked:
>>> @iclasslocked  
>>> def classlocked_classmethod(cls):
>>>> print("class lock acquired!")

#### iclasslocked(...)
```python
@staticmethod
def iclasslocked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@113:123`](/_rsruntime/util/locked_resource.py#L113)

<details>
<summary>Source Code</summary>

```python
def iclasslocked(func: typing.Callable):
    '''
        Is the same as @classlocked (it even calls it), but also wraps the method in classmethod
        Meant to be used with @LockedClass:
            @LockedClass()
            class Locked:
                @iclasslocked
                def classlocked_classmethod(cls):
                    print("class lock acquired!")
    '''
    return classmethod(classlocked(func))
```
</details>

> Is the same as @classlocked (it even calls it), but also wraps the method in classmethod  
> Meant to be used with @LockedClass:
>> @LockedClass()  
>> class Locked:
>>> @iclasslocked  
>>> def classlocked_classmethod(cls):
>>>> print("class lock acquired!")

#### locked(...)
```python
@staticmethod
def locked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@76:92`](/_rsruntime/util/locked_resource.py#L76)

<details>
<summary>Source Code</summary>

```python
def locked(func: typing.Callable):
    '''
        Waits to acquire the method's self's .lock attribute (uses "with")
        This should be used in tandem with the LockedResource superclass:
            class DemoLocked(LockedResource): # note subclass
                def __init__(self):
                    super().__init__() # note super init, needed to setup .lock
                    print("initialized!")
                @locked # note decorator
                def test_lock(self):
                    print("lock acquired!")
    '''
    @wraps(func)
    def locked_func(self: LockedResource, *args, **kwargs):
        with self.lock:
            return func(self, *args, **kwargs)
    return locked_func
```
</details>

> Waits to acquire the method's self's .lock attribute (uses "with")  
> This should be used in tandem with the LockedResource superclass:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock  
>>>> print("initialized!")
>>> @locked # note decorator  
>>> def test_lock(self):
>>>> print("lock acquired!")

#### locked(...)
```python
@staticmethod
def locked(func: Callable)
```

[`_rsruntime/util/locked_resource.py@76:92`](/_rsruntime/util/locked_resource.py#L76)

<details>
<summary>Source Code</summary>

```python
def locked(func: typing.Callable):
    '''
        Waits to acquire the method's self's .lock attribute (uses "with")
        This should be used in tandem with the LockedResource superclass:
            class DemoLocked(LockedResource): # note subclass
                def __init__(self):
                    super().__init__() # note super init, needed to setup .lock
                    print("initialized!")
                @locked # note decorator
                def test_lock(self):
                    print("lock acquired!")
    '''
    @wraps(func)
    def locked_func(self: LockedResource, *args, **kwargs):
        with self.lock:
            return func(self, *args, **kwargs)
    return locked_func
```
</details>

> Waits to acquire the method's self's .lock attribute (uses "with")  
> This should be used in tandem with the LockedResource superclass:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock  
>>>> print("initialized!")
>>> @locked # note decorator  
>>> def test_lock(self):
>>>> print("lock acquired!")

#### locked_by(...)
```python
@staticmethod
def locked_by(lock: AbstractContextManager)
```

[`_rsruntime/util/locked_resource.py@125:132`](/_rsruntime/util/locked_resource.py#L125)

<details>
<summary>Source Code</summary>

```python
def locked_by(lock: AbstractContextManager):
    def func_locker(func: typing.Callable):
        @wraps(func)
        def locked_func(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return locked_func
    return func_locker
```
</details>

> <no doc>

#### locked_by(...)
```python
@staticmethod
def locked_by(lock: AbstractContextManager)
```

[`_rsruntime/util/locked_resource.py@125:132`](/_rsruntime/util/locked_resource.py#L125)

<details>
<summary>Source Code</summary>

```python
def locked_by(lock: AbstractContextManager):
    def func_locker(func: typing.Callable):
        @wraps(func)
        def locked_func(*args, **kwargs):
            with lock:
                return func(*args, **kwargs)
        return locked_func
    return func_locker
```
</details>

> <no doc>

### `locked` (`RunServer.Util.Locker.locked` | `RS.U.Locker.locked`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.locked.md](RunServer.Util.Locker.locked.md)  
> Waits to acquire the method's self's .lock attribute (uses "with")  
> This should be used in tandem with the LockedResource superclass:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock  
>>>> print("initialized!")
>>> @locked # note decorator  
>>> def test_lock(self):
>>>> print("lock acquired!")

### `superclasses` (`RunServer.Util.Locker.superclasses` | `RS.U.Locker.superclasses`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.superclasses.md](RunServer.Util.Locker.superclasses.md)  
> superclasses(LockedResource, LR)

## `PerfCounter` (`RunServer.Util.PerfCounter` | `RS.U.PerfCounter`)
[`_rsruntime/util/perfcounter.py`](/_rsruntime/util/perfcounter.py "Source")  
[Standalone doc: parts/RunServer/Util/RunServer.Util.PerfCounter.md](RunServer.Util.PerfCounter.md)  
> Provides an object-oriented (because why not) way to use (and format) time.perf_counter

### fromhex(...)
```python
@classmethod
def fromhex(string)
```
> Create a floating-point number from a hexadecimal string.  
>   
> >>> float.fromhex('0x1.ffffp10')  
> 2047.984375  
> >>> float.fromhex('-0x1p-1074')  
> -5e-324

## `TimedLoadDebug` (`RunServer.Util.TimedLoadDebug` | `RS.U.TimedLoadDebug`)
[`_rsruntime/util/timed_load_debug.py`](/_rsruntime/util/timed_load_debug.py "Source")  
[Standalone doc: parts/RunServer/Util/RunServer.Util.TimedLoadDebug.md](RunServer.Util.TimedLoadDebug.md)  
> Helper class for debugging time spent doing things

### final(...)
```python
@staticmethod
def final(self)
```

[`_rsruntime/util/timed_load_debug.py@27:29`](/_rsruntime/util/timed_load_debug.py#L27)

<details>
<summary>Source Code</summary>

```python
def final(self):
    self.logfn(self.msgfmt[0][1].format(opc=self.ocounter, ipc=self.icounter))
    self.ocounter = None # stop accidental multiple final() calls
```
</details>

> <no doc>

### foreach(...)
```python
@classmethod
def foreach(logfunc: Callable(str), each: tuple[tuple[str, Callable], Ellipsis], tld_args)
```

[`_rsruntime/util/timed_load_debug.py@40:45`](/_rsruntime/util/timed_load_debug.py#L40)

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

### ienter(...)
```python
@staticmethod
def ienter(self)
```

[`_rsruntime/util/timed_load_debug.py@30:32`](/_rsruntime/util/timed_load_debug.py#L30)

<details>
<summary>Source Code</summary>

```python
def ienter(self):
    self.icounter = PerfCounter(sec='', secs='')
    self.logfn(self.msgfmt[1][0].format(c=next(self.cur[0]), opc=self.ocounter, ipc=self.icounter))
```
</details>

> <no doc>

### iexit(...)
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

[`_rsruntime/util/timed_load_debug.py@34:37`](/_rsruntime/util/timed_load_debug.py#L34)

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

## `Timer` (`RunServer.Util.Timer` | `RS.U.Timer`)
[`_rsruntime/util/timer.py`](/_rsruntime/util/timer.py "Source")  
[Standalone doc: parts/RunServer/Util/RunServer.Util.Timer.md](RunServer.Util.Timer.md)  

### clear(...)
```python
@staticmethod
def clear(timer: BaseTimer) -> BaseTimer
```

[`_rsruntime/util/timer.py@84:86`](/_rsruntime/util/timer.py#L84)

<details>
<summary>Source Code</summary>

```python
@staticmethod
def clear(timer: BaseTimer) -> BaseTimer:
    return timer.stop()
```
</details>

> <no doc>

### set_timer(...)
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

[`_rsruntime/util/timer.py@80:83`](/_rsruntime/util/timer.py#L80)

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

## `fetch` (`RunServer.Util.fetch` | `RS.U.fetch`)
[Standalone doc: parts/RunServer/Util/RunServer.Util.fetch.md](RunServer.Util.fetch.md)  

### `CHUNK_FETCH_ABORT` (`RunServer.Util.fetch.CHUNK_FETCH_ABORT` | `RS.U.fetch.CHUNK_FETCH_ABORT`)
[Standalone doc: parts/RunServer/Util/fetch/RunServer.Util.fetch.CHUNK_FETCH_ABORT.md](RunServer.Util.fetch.CHUNK_FETCH_ABORT.md)  
> The base class of the class hierarchy.  
>   
> When called, it accepts no arguments and returns a new featureless  
> instance that has no instance attributes and cannot be given any.

### `chunk_fetch` (`RunServer.Util.fetch.chunk_fetch` | `RS.U.fetch.chunk_fetch`)
[`_rsruntime/util/fetch.py`](/_rsruntime/util/fetch.py "Source")  
[Standalone doc: parts/RunServer/Util/fetch/RunServer.Util.fetch.chunk_fetch.md](RunServer.Util.fetch.chunk_fetch.md)  
> Fetch and yield bytes from the URL in chunks of chunksize  
> Yields a Chunk object  
> If the URL is cached, and ignore_cache is false, then yields the data (as Chunk, with from_cache=True) and returns it  
> Once all data has been read and yielded, it is returned as bytes, and added to the cache if add_to_cache is true
>> Cache is not written to if CHUNK_FETCH_ABORT is used to interrupt the download

### `fetch` (`RunServer.Util.fetch.fetch` | `RS.U.fetch.fetch`)
[`_rsruntime/util/fetch.py`](/_rsruntime/util/fetch.py "Source")  
[Standalone doc: parts/RunServer/Util/fetch/RunServer.Util.fetch.fetch.md](RunServer.Util.fetch.fetch.md)  
> Fetch bytes from the URL  
> If the URL is cached, and ignore_cache is false, then returns the cached value  
> Otherwise, fetch the data and return it, as well as add it to the cache if add_to_cache is true

### `fetch_nocache` (`RunServer.Util.fetch.fetch_nocache` | `RS.U.fetch.fetch_nocache`)
[Standalone doc: parts/RunServer/Util/fetch/RunServer.Util.fetch.fetch_nocache.md](RunServer.Util.fetch.fetch_nocache.md)  
> partial(func, *args, **keywords) - new function with partial application  
> of the given arguments and keywords.

#### fetch(...)
```python
@staticmethod
def fetch(...) -> bytes
```
<details>
<summary>Parameters...</summary>

```python
    url: str, add_to_cache: bool = True, ignore_cache: bool = False,
    add_headers
```
</details>

[`_rsruntime/util/fetch.py@24:34`](/_rsruntime/util/fetch.py#L24)

<details>
<summary>Source Code</summary>

```python
def fetch(url: str, *, add_to_cache: bool = True, ignore_cache: bool = False, **add_headers) -> bytes:
    '''
        Fetch bytes from the URL
        If the URL is cached, and ignore_cache is false, then returns the cached value
        Otherwise, fetch the data and return it, as well as add it to the cache if add_to_cache is true
    '''
    h = hash(url)
    if (not ignore_cache) and (h in cache): return cache[h]
    d = request('GET', url, headers={'User-Agent': user_agent} | add_headers).data
    if add_to_cache: cache[h] = d
    return d
```
</details>

> Fetch bytes from the URL  
> If the URL is cached, and ignore_cache is false, then returns the cached value  
> Otherwise, fetch the data and return it, as well as add it to the cache if add_to_cache is true

### `flush_cache` (`RunServer.Util.fetch.flush_cache` | `RS.U.fetch.flush_cache`)
[`_rsruntime/util/fetch.py`](/_rsruntime/util/fetch.py "Source")  
[Standalone doc: parts/RunServer/Util/fetch/RunServer.Util.fetch.flush_cache.md](RunServer.Util.fetch.flush_cache.md)  
> Removes a URL entry from the cache, or everything if url is None

### `foreach_chunk_fetch` (`RunServer.Util.fetch.foreach_chunk_fetch` | `RS.U.fetch.foreach_chunk_fetch`)
[`_rsruntime/util/fetch.py`](/_rsruntime/util/fetch.py "Source")  
[Standalone doc: parts/RunServer/Util/fetch/RunServer.Util.fetch.foreach_chunk_fetch.md](RunServer.Util.fetch.foreach_chunk_fetch.md)  
> Calls callback for each Chunk yielded by chunk_fetch, then returns the bytes