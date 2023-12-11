[Standalone doc: parts/RunServer/ShaeLib/RunServer.ShaeLib.types.md](RunServer.ShaeLib.types)  

## `Hooks` (`RunServer.ShaeLib.types.Hooks` | `RS.SL.types.Hooks`)
[`_rsruntime/ShaeLib/types/hooks.py`](/_rsruntime/ShaeLib/types/hooks.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/types/RunServer.ShaeLib.types.Hooks.md](RunServer.ShaeLib.types.Hooks)  
> The most caustic generic hooks class
>> Has no difference in behavior from GenericHooks other than typehinting
>>> basically syntactic sugar for dict[typing.Hashable, typing.Callable]
> Also serves as a container for the other types of hooks

### register(...)
```python
@staticmethod
def register(self, hook: HookType, callback: FuncType)
```

[`_rsruntime/ShaeLib/types/hooks.py@22:25`](/_rsruntime/ShaeLib/types/hooks.py#L22)

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

[`_rsruntime/ShaeLib/types/hooks.py@26:29`](/_rsruntime/ShaeLib/types/hooks.py#L26)

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

[`_rsruntime/ShaeLib/types/hooks.py@30:33`](/_rsruntime/ShaeLib/types/hooks.py#L30)

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

## `fbd` (`RunServer.ShaeLib.types.fbd` | `RS.SL.types.fbd`)
[Standalone doc: parts/RunServer/ShaeLib/types/RunServer.ShaeLib.types.fbd.md](RunServer.ShaeLib.types.fbd)  

### `INIBackedDict` (`RunServer.ShaeLib.types.fbd.INIBackedDict` | `RS.SL.types.fbd.INIBackedDict`)
[`_rsruntime/ShaeLib/types/fbd.py`](/_rsruntime/ShaeLib/types/fbd.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/types/fbd/RunServer.ShaeLib.types.fbd.INIBackedDict.md](RunServer.ShaeLib.types.fbd.INIBackedDict)  
> A FileBackedDict implementation that uses ConfigParser as a backend

#### bettergetter(...)
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

[`_rsruntime/ShaeLib/types/fbd.py@137:153`](/_rsruntime/ShaeLib/types/fbd.py#L137)

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

#### contains(...)
```python
@staticmethod
def contains(self, key: Key, _tree: MutableMapping | None = None) -> bool
```

[`_rsruntime/ShaeLib/types/fbd.py@188:194`](/_rsruntime/ShaeLib/types/fbd.py#L188)

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

#### get(...)
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

[`_rsruntime/ShaeLib/types/fbd.py@160:175`](/_rsruntime/ShaeLib/types/fbd.py#L160)

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

#### get(...)
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

[`_rsruntime/ShaeLib/types/fbd.py@160:175`](/_rsruntime/ShaeLib/types/fbd.py#L160)

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

#### is_autosyncing(...)
```python
@staticmethod
def is_autosyncing(self) -> bool
```

[`_rsruntime/ShaeLib/types/fbd.py@97:100`](/_rsruntime/ShaeLib/types/fbd.py#L97)

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

#### items_full(...)
```python
@staticmethod
def items_full(self, start_key: Key, key_join: bool = True) -> Generator[tuple[str | tuple[str, ...], Deserialized], None, None]
```

[`_rsruntime/ShaeLib/types/fbd.py@197:200`](/_rsruntime/ShaeLib/types/fbd.py#L197)

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

#### items_short(...)
```python
@staticmethod
def items_short(self, start_key: Key)
```

[`_rsruntime/ShaeLib/types/fbd.py@201:204`](/_rsruntime/ShaeLib/types/fbd.py#L201)

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

#### key(...)
```python
@classmethod
def key(key: Key, top_level: bool = False) -> tuple[str, Ellipsis]
```

[`_rsruntime/ShaeLib/types/fbd.py@65:78`](/_rsruntime/ShaeLib/types/fbd.py#L65)

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

#### keys(...)
```python
@staticmethod
def keys(self, start_key: Key | None = None, key_join: bool = True) -> Generator[str | tuple[str, ...], None, None]
```

[`_rsruntime/ShaeLib/types/fbd.py@205:214`](/_rsruntime/ShaeLib/types/fbd.py#L205)

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

#### path_from_topkey(...)
```python
@staticmethod
def path_from_topkey(self, topkey: str)
```

[`_rsruntime/ShaeLib/types/fbd.py@79:81`](/_rsruntime/ShaeLib/types/fbd.py#L79)

<details>
<summary>Source Code</summary>

```python
def path_from_topkey(self, topkey: str):
    '''Returns the Path corresponding to the top-key's file'''
    return (self.path / topkey).with_suffix(self.file_suffix)
```
</details>

> Returns the Path corresponding to the top-key's file

#### readin(...)
```python
@staticmethod
def readin(self, topkey: str)
```

[`_rsruntime/ShaeLib/types/fbd.py@127:132`](/_rsruntime/ShaeLib/types/fbd.py#L127)

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

#### readin_modified(...)
```python
@staticmethod
def readin_modified(self)
```

[`_rsruntime/ShaeLib/types/fbd.py@116:126`](/_rsruntime/ShaeLib/types/fbd.py#L116)

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

#### setitem(...)
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

[`_rsruntime/ShaeLib/types/fbd.py@178:185`](/_rsruntime/ShaeLib/types/fbd.py#L178)

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

#### sort(...)
```python
@staticmethod
def sort(self, by: Callable(str | tuple[str, ...]) -> Any = <lambda>)
```

[`_rsruntime/ShaeLib/types/fbd.py@277:283`](/_rsruntime/ShaeLib/types/fbd.py#L277)

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

#### start_autosync(...)
```python
@staticmethod
def start_autosync(self)
```

[`_rsruntime/ShaeLib/types/fbd.py@89:92`](/_rsruntime/ShaeLib/types/fbd.py#L89)

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

#### stop_autosync(...)
```python
@staticmethod
def stop_autosync(self)
```

[`_rsruntime/ShaeLib/types/fbd.py@93:96`](/_rsruntime/ShaeLib/types/fbd.py#L93)

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

#### sync(...)
```python
@staticmethod
def sync(self)
```

[`_rsruntime/ShaeLib/types/fbd.py@83:87`](/_rsruntime/ShaeLib/types/fbd.py#L83)

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

#### values(...)
```python
@staticmethod
def values(self, start_key: Key) -> Generator[[Deserialized], None, None]
```

[`_rsruntime/ShaeLib/types/fbd.py@216:219`](/_rsruntime/ShaeLib/types/fbd.py#L216)

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

#### writeback(...)
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

[`_rsruntime/ShaeLib/types/fbd.py@106:112`](/_rsruntime/ShaeLib/types/fbd.py#L106)

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

#### writeback_dirty(...)
```python
@staticmethod
def writeback_dirty(self)
```

[`_rsruntime/ShaeLib/types/fbd.py@102:105`](/_rsruntime/ShaeLib/types/fbd.py#L102)

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

### `JSONBackedDict` (`RunServer.ShaeLib.types.fbd.JSONBackedDict` | `RS.SL.types.fbd.JSONBackedDict`)
[`_rsruntime/ShaeLib/types/fbd.py`](/_rsruntime/ShaeLib/types/fbd.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/types/fbd/RunServer.ShaeLib.types.fbd.JSONBackedDict.md](RunServer.ShaeLib.types.fbd.JSONBackedDict)  
> A FileBackedDict implementation that uses JSON as a backend

#### bettergetter(...)
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

[`_rsruntime/ShaeLib/types/fbd.py@137:153`](/_rsruntime/ShaeLib/types/fbd.py#L137)

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

#### contains(...)
```python
@staticmethod
def contains(self, key: Key, _tree: MutableMapping | None = None) -> bool
```

[`_rsruntime/ShaeLib/types/fbd.py@188:194`](/_rsruntime/ShaeLib/types/fbd.py#L188)

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

#### get(...)
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

[`_rsruntime/ShaeLib/types/fbd.py@160:175`](/_rsruntime/ShaeLib/types/fbd.py#L160)

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

#### get(...)
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

[`_rsruntime/ShaeLib/types/fbd.py@160:175`](/_rsruntime/ShaeLib/types/fbd.py#L160)

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

#### is_autosyncing(...)
```python
@staticmethod
def is_autosyncing(self) -> bool
```

[`_rsruntime/ShaeLib/types/fbd.py@97:100`](/_rsruntime/ShaeLib/types/fbd.py#L97)

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

#### items_full(...)
```python
@staticmethod
def items_full(self, start_key: Key, key_join: bool = True) -> Generator[tuple[str | tuple[str, ...], Deserialized], None, None]
```

[`_rsruntime/ShaeLib/types/fbd.py@197:200`](/_rsruntime/ShaeLib/types/fbd.py#L197)

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

#### items_short(...)
```python
@staticmethod
def items_short(self, start_key: Key)
```

[`_rsruntime/ShaeLib/types/fbd.py@201:204`](/_rsruntime/ShaeLib/types/fbd.py#L201)

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

#### key(...)
```python
@classmethod
def key(key: Key, top_level: bool = False) -> tuple[str, Ellipsis]
```

[`_rsruntime/ShaeLib/types/fbd.py@65:78`](/_rsruntime/ShaeLib/types/fbd.py#L65)

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

#### keys(...)
```python
@staticmethod
def keys(self, start_key: Key | None = None, key_join: bool = True) -> Generator[str | tuple[str, ...], None, None]
```

[`_rsruntime/ShaeLib/types/fbd.py@205:214`](/_rsruntime/ShaeLib/types/fbd.py#L205)

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

#### path_from_topkey(...)
```python
@staticmethod
def path_from_topkey(self, topkey: str)
```

[`_rsruntime/ShaeLib/types/fbd.py@79:81`](/_rsruntime/ShaeLib/types/fbd.py#L79)

<details>
<summary>Source Code</summary>

```python
def path_from_topkey(self, topkey: str):
    '''Returns the Path corresponding to the top-key's file'''
    return (self.path / topkey).with_suffix(self.file_suffix)
```
</details>

> Returns the Path corresponding to the top-key's file

#### readin(...)
```python
@staticmethod
def readin(self, topkey: str)
```

[`_rsruntime/ShaeLib/types/fbd.py@127:132`](/_rsruntime/ShaeLib/types/fbd.py#L127)

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

#### readin_modified(...)
```python
@staticmethod
def readin_modified(self)
```

[`_rsruntime/ShaeLib/types/fbd.py@116:126`](/_rsruntime/ShaeLib/types/fbd.py#L116)

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

#### setitem(...)
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

[`_rsruntime/ShaeLib/types/fbd.py@178:185`](/_rsruntime/ShaeLib/types/fbd.py#L178)

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

#### sort(...)
```python
@staticmethod
def sort(self, by: Callable(tuple[str, Ellipsis]) -> Any = <lambda>)
```

[`_rsruntime/ShaeLib/types/fbd.py@374:378`](/_rsruntime/ShaeLib/types/fbd.py#L374)

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

#### start_autosync(...)
```python
@staticmethod
def start_autosync(self)
```

[`_rsruntime/ShaeLib/types/fbd.py@89:92`](/_rsruntime/ShaeLib/types/fbd.py#L89)

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

#### stop_autosync(...)
```python
@staticmethod
def stop_autosync(self)
```

[`_rsruntime/ShaeLib/types/fbd.py@93:96`](/_rsruntime/ShaeLib/types/fbd.py#L93)

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

#### sync(...)
```python
@staticmethod
def sync(self)
```

[`_rsruntime/ShaeLib/types/fbd.py@83:87`](/_rsruntime/ShaeLib/types/fbd.py#L83)

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

#### values(...)
```python
@staticmethod
def values(self, start_key: Key) -> Generator[[Deserialized], None, None]
```

[`_rsruntime/ShaeLib/types/fbd.py@216:219`](/_rsruntime/ShaeLib/types/fbd.py#L216)

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

#### writeback(...)
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

[`_rsruntime/ShaeLib/types/fbd.py@106:112`](/_rsruntime/ShaeLib/types/fbd.py#L106)

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

#### writeback_dirty(...)
```python
@staticmethod
def writeback_dirty(self)
```

[`_rsruntime/ShaeLib/types/fbd.py@102:105`](/_rsruntime/ShaeLib/types/fbd.py#L102)

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

## `shaespace` (`RunServer.ShaeLib.types.shaespace` | `RS.SL.types.shaespace`)
[Standalone doc: parts/RunServer/ShaeLib/types/RunServer.ShaeLib.types.shaespace.md](RunServer.ShaeLib.types.shaespace)  

### `ShaeSpace` (`RunServer.ShaeLib.types.shaespace.ShaeSpace` | `RS.SL.types.shaespace.ShaeSpace`)
[`_rsruntime/ShaeLib/types/shaespace.py`](/_rsruntime/ShaeLib/types/shaespace.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/types/shaespace/RunServer.ShaeLib.types.shaespace.ShaeSpace.md](RunServer.ShaeLib.types.shaespace.ShaeSpace)  
> A decorator to turn a class('s __dict__) into a SimpleNamespace

### `SlottedSpace` (`RunServer.ShaeLib.types.shaespace.SlottedSpace` | `RS.SL.types.shaespace.SlottedSpace`)
[`_rsruntime/ShaeLib/types/shaespace.py`](/_rsruntime/ShaeLib/types/shaespace.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/types/shaespace/RunServer.ShaeLib.types.shaespace.SlottedSpace.md](RunServer.ShaeLib.types.shaespace.SlottedSpace)  
> Creates and instantiates a namespace with a preset __slots__ attribute

### `SlottedSpaceType` (`RunServer.ShaeLib.types.shaespace.SlottedSpaceType` | `RS.SL.types.shaespace.SlottedSpaceType`)
[`_rsruntime/ShaeLib/types/shaespace.py`](/_rsruntime/ShaeLib/types/shaespace.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/types/shaespace/RunServer.ShaeLib.types.shaespace.SlottedSpaceType.md](RunServer.ShaeLib.types.shaespace.SlottedSpaceType)  
> Creates a namespace with a preset __slots__ attribute

### `slotted_ShaeSpace` (`RunServer.ShaeLib.types.shaespace.slotted_ShaeSpace` | `RS.SL.types.shaespace.slotted_ShaeSpace`)
[`_rsruntime/ShaeLib/types/shaespace.py`](/_rsruntime/ShaeLib/types/shaespace.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/types/shaespace/RunServer.ShaeLib.types.shaespace.slotted_ShaeSpace.md](RunServer.ShaeLib.types.shaespace.slotted_ShaeSpace)  
> A decorator to turn a class('s __dict__) into a SlottedSpace