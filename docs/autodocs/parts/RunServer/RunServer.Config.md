# `Config` (`RunServer.Config` | `RS.C`)
[`_rsruntime/lib/rs_config.py`](/_rsruntime/lib/rs_config.py "Source")  
[Standalone doc: parts/RunServer/RunServer.Config.md](RunServer.Config.md)  
> A thin wrapper around INIBackedDict

## bettergetter(...)
```python
def bettergetter(key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Any = Behavior.RAISE, set_default: bool = True) -> Deserialized | Any
```

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

## close()
```python
def close()
```

[`_rsruntime/lib/rs_config.py@65:68`](/_rsruntime/lib/rs_config.py#L65)

<details>
<summary>Source Code</summary>

```python
def close(self):
    self.stop_autosync()
    self.sort()
    self.sync()
```
</details>

> <no doc>

## contains(...)
```python
def contains(key: Key, _tree: MutableMapping | None = None) -> bool
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

## get(...)
```python
def get(key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Serializable = Behavior.RAISE, _tree: MutableMapping | None = None) -> Deserialized
```

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

## get(...)
```python
def get(key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Serializable = Behavior.RAISE, _tree: MutableMapping | None = None) -> Deserialized
```

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

## is_autosyncing()
```python
def is_autosyncing() -> bool
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

## items_full(...)
```python
def items_full(start_key: Key, key_join: bool = True) -> Generator[tuple[str | tuple[str, ...], Deserialized], None, None]
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

## items_short(...)
```python
def items_short(start_key: Key)
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

## key(...)
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

## keys(...)
```python
def keys(start_key: Key | None = None, key_join: bool = True) -> Generator[str | tuple[str, ...], None, None]
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

## mass_set_default(...)
```python
def mass_set_default(pfx: str | None = None, dict_vals: dict[str, Serializable] | None = None, values: Serializable)
```

[`_rsruntime/lib/rs_config.py@28:64`](/_rsruntime/lib/rs_config.py#L28)
> Sets a large amount of default values
>> When pfx is not None, it is prepended (with a / if it doesn't already have one) to each key
> Values are either given through dict_vals or **values (keyword args)
>> Using both is probably bad but not prohibited
>>> A SyntaxWarning shall be issued upon you to remind you of your choices.
>> If a value is in both and is not the same, a ValueError is raised
>>> Once this has been checked, they are merged together
> If a total of 0 values are given, an error is logged  
> Otherwise, an info is logged decribing how many keys will be set

## path_from_topkey(...)
```python
def path_from_topkey(topkey: str)
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

## readin(...)
```python
def readin(topkey: str)
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

## readin_modified()
```python
def readin_modified()
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

## set_default(...)
```python
def set_default(option: str | tuple[str], value: Serializable)
```

[`_rsruntime/lib/rs_config.py@24:27`](/_rsruntime/lib/rs_config.py#L24)

<details>
<summary>Source Code</summary>

```python
def set_default(self, option: str | tuple[str], value: INIBackedDict.__bases__[0].__parameters__[0]):
    '''Sets an option if it does not exist'''
    if option not in self:
        self[option] = value
```
</details>

> Sets an option if it does not exist

## setitem(...)
```python
def setitem(key: Key, val: Serializable, _tree: MutableMapping | None = None)
```

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

## sort(...)
```python
def sort(by: Callable(str | tuple[str, ...]) -> Any = <lambda>)
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

## start_autosync()
```python
def start_autosync()
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

## stop_autosync()
```python
def stop_autosync()
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

## sync()
```python
def sync()
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

## values(...)
```python
def values(start_key: Key) -> Generator[[Deserialized], None, None]
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

## writeback(...)
```python
def writeback(topkey: str, only_if_dirty: bool = True, clean: bool = True)
```

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

## writeback_dirty()
```python
def writeback_dirty()
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