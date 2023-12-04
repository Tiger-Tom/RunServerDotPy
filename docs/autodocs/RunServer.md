*This documentation was generated with `devel/makedoc.py`*
> Documentation is generated from the source code.
> Documentation is quite probably incomplete or inaccurate, just look at this script!

# `RunServer` (imported as `RS`)
> <no doc>

# `Bootstrapper` (`RunServer.Bootstrapper` | `RS.BS`)
[`_rsruntime/rs_BOOTSTRAP.py`](/_rsruntime/rs_BOOTSTRAP.py "Source")  
[Standalone doc: parts/RunServer/Bootstrapper.md](./parts/RunServer/Bootstrapper.md)  
> Does the necessary startup and take-down for RunServer

## access_entrypoint(...)
```python
def access_entrypoint(ep: str) -> types.ModuleType
```
[`_rsruntime/rs_BOOTSTRAP.py@210:214`](/_rsruntime/rs_BOOTSTRAP.py#L210)

<details>
<summary>Source Code</summary>

```python
def access_entrypoint(self, ep: str) -> types.ModuleType:
    '''Loads the entrypoint's surrounding module'''
    fl = SourceFileLoader(f'{__package__}.RS', ep)
    self.logger.warning(f'ACCESSING ENTRYPOINT: {fl}')
    return fl.load_module()
```
</details>

> Loads the entrypoint's surrounding module

## bootstrap(...)
```python
def bootstrap(close_after: bool = True)
```
[`_rsruntime/rs_BOOTSTRAP.py@182:196`](/_rsruntime/rs_BOOTSTRAP.py#L182)

<details>
<summary>Source Code</summary>

```python
def bootstrap(self, close_after: bool = True):
    '''Executes the base manifest, then accesses, assigns, and chainloads the entrypoint'''
    self.run_base_manifest()
    if self.args.update_only:
        self.logger.fatal('--update-only argument supplied, exiting')
        return
    self.__contained_RS_module = self.access_entrypoint('_rsruntime/rs_ENTRYPOINT.py')
    self.__contained_RS = self.stage_entrypoint(self.__contained_RS_module)
    global RS
    if RS != NotImplemented:
        self.logger.warning(f'Tried to set {__file__}-level RS, but it appears to have already been set?')
    else: RS = self.__contained_RS
    self.init_entrypoint(RS)
    self.chainload_entrypoint(RS)
    if close_after: self.close()
```
</details>

> Executes the base manifest, then accesses, assigns, and chainloads the entrypoint

## chainload_entrypoint(...)
```python
def chainload_entrypoint(rs: RS)
```
[`_rsruntime/rs_BOOTSTRAP.py@223:227`](/_rsruntime/rs_BOOTSTRAP.py#L223)

<details>
<summary>Source Code</summary>

```python
def chainload_entrypoint(self, rs: 'RS'):
    '''Runs the entrypoint's __call__ method'''
    self.logger.warning(f'ENTERING ENTRYPOINT: {rs.__call__}')
    rs()
    self.logger.fatal('EXITED ENTRYPOINT')
```
</details>

> Runs the entrypoint's __call__ method

## close(...)
```python
def close(do_exit: bool | int = False)
```
[`_rsruntime/rs_BOOTSTRAP.py@231:239`](/_rsruntime/rs_BOOTSTRAP.py#L231)

<details>
<summary>Source Code</summary>

```python
def close(self, do_exit: bool | int = False):
    '''Executes all shutdown callbacks and closes logging (logging.shutdown()), and exits with exit code do_exit if it isn't False'''
    if self.is_closed: return
    self.logger.irrec('Instructed to perform orderly shutdown, executing shutdown callbacks...')
    for h in self.shutdown_callbacks: h()
    self.logger.irrec(f'Closing logger{f" and exiting with code {do_exit}" if do_exit is not False else ""}, goodbye!')
    logging.shutdown()
    if do_exit is False: self.is_closed = True
    else: exit(do_exit)
```
</details>

> Executes all shutdown callbacks and closes logging (logging.shutdown()), and exits with exit code do_exit if it isn't False

## ensure_python_version()
```python
@classmethod
def ensure_python_version()
```
[`_rsruntime/rs_BOOTSTRAP.py@69:73`](/_rsruntime/rs_BOOTSTRAP.py#L69)

<details>
<summary>Source Code</summary>

```python
@classmethod
def ensure_python_version(cls):
    '''Ensure that the Python version meets the minimum requirements'''
    if sys.version_info < cls.minimum_vers:
        raise NotImplementedError(f'Python version {".".join(map(str, sys.version_info[:3]))} doesn\'t meet the minimum requirements, needs {".".join(map(str, cls.minimum_vers))}')
```
</details>

> Ensure that the Python version meets the minimum requirements

## init_entrypoint(...)
```python
def init_entrypoint(rs: RS)
```
[`_rsruntime/rs_BOOTSTRAP.py@219:222`](/_rsruntime/rs_BOOTSTRAP.py#L219)

<details>
<summary>Source Code</summary>

```python
def init_entrypoint(self, rs: 'RS'):
    '''Initializes the entrypoint's class (with self as an argument)'''
    self.logger.warning(f'INITIALIZING ENTRYPOINT: {rs.__init__}')
    rs.__init__(self)
```
</details>

> Initializes the entrypoint's class (with self as an argument)

## parse_arguments(...)
```python
def parse_arguments(args=None)
```
[`_rsruntime/rs_BOOTSTRAP.py@75:93`](/_rsruntime/rs_BOOTSTRAP.py#L75)
> Generate and ArgumentParser and parse (known) arguments

## register_onclose(...)
```python
def register_onclose(cb: Callable)
```
[`_rsruntime/rs_BOOTSTRAP.py@240:242`](/_rsruntime/rs_BOOTSTRAP.py#L240)

<details>
<summary>Source Code</summary>

```python
def register_onclose(self, cb: typing.Callable[[], None]):
    '''Registers a function to run when self.close() is called'''
    self.shutdown_callbacks.add(cb)
```
</details>

> Registers a function to run when self.close() is called

## run_base_manifest()
```python
def run_base_manifest()
```
[`_rsruntime/rs_BOOTSTRAP.py@198:208`](/_rsruntime/rs_BOOTSTRAP.py#L198)

<details>
<summary>Source Code</summary>

```python
def run_base_manifest(self):
    '''Executes the base manifest (_rsruntime/MANIFEST.ini)'''
    mp = Path('_rsruntime/MANIFEST.ini')
    if not mp.exists():
        self.logger.error(f'Manifest at {mp} does not exist, attempting to download')
        try: request.urlretrieve(self.dl_man, mp)
        except Exception as e:
            self.logger.fatal(f'Could not fetch manifest from {self.dl_man}:\n{"".join(traceback.format_exception(e))}')
            return
    self.logger.info(f'Loading in {mp}')
    self.base_manifest = Manifest.from_file(mp)()
```
</details>

> Executes the base manifest (_rsruntime/MANIFEST.ini)

## setup_logger()
```python
def setup_logger() -> logging.Logger
```
[`_rsruntime/rs_BOOTSTRAP.py@95:178`](/_rsruntime/rs_BOOTSTRAP.py#L95)
> Sets up self.logger, as well as logging.INFOPLUS/IRRECOVERABLE and Logger.infop/irrec()

## stage_entrypoint(...)
```python
def stage_entrypoint(rs_outer: types.ModuleType) -> RunServer
```
[`_rsruntime/rs_BOOTSTRAP.py@215:218`](/_rsruntime/rs_BOOTSTRAP.py#L215)

<details>
<summary>Source Code</summary>

```python
def stage_entrypoint(self, rs_outer: types.ModuleType) -> 'rs_outer.RunServer':
    '''Stages the entrypoint's class'''
    self.logger.warning(f'STAGING ENTRYPOINT: {rs_outer.RunServer.__new__}')
    return rs_outer.RunServer.__new__(rs_outer.RunServer)
```
</details>

> Stages the entrypoint's class


# `Util` (`RunServer.Util` | `RS.U`)
[Standalone doc: parts/RunServer/Util.md](./parts/RunServer/Util.md)  

## `BetterPPrinter` (`RunServer.Util.BetterPPrinter` | `RS.U.BetterPPrinter`)
[`_rsruntime/util/betterprettyprinter.py`](/_rsruntime/util/betterprettyprinter.py "Source")  
[Standalone doc: parts/RunServer/Util/BetterPPrinter.md](./parts/RunServer/Util/BetterPPrinter.md)  

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
[Standalone doc: parts/RunServer/Util/Hooks.md](./parts/RunServer/Util/Hooks.md)  
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
[Standalone doc: parts/RunServer/Util/INIBackedDict.md](./parts/RunServer/Util/INIBackedDict.md)  
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
[Standalone doc: parts/RunServer/Util/JSONBackedDict.md](./parts/RunServer/Util/JSONBackedDict.md)  
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
[Standalone doc: parts/RunServer/Util/Locker.md](./parts/RunServer/Util/Locker.md)  

### `LockedResource` (`RunServer.Util.Locker.LockedResource` | `RS.U.Locker.LockedResource`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/LockedResource.md](./parts/RunServer/Util/Locker/LockedResource.md)  
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
[Standalone doc: parts/RunServer/Util/Locker/basic.md](./parts/RunServer/Util/Locker/basic.md)  
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
[Standalone doc: parts/RunServer/Util/Locker/cls.md](./parts/RunServer/Util/Locker/cls.md)  
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
[Standalone doc: parts/RunServer/Util/Locker/cls_decors.md](./parts/RunServer/Util/Locker/cls_decors.md)  
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
[Standalone doc: parts/RunServer/Util/Locker/etc.md](./parts/RunServer/Util/Locker/etc.md)  
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
[Standalone doc: parts/RunServer/Util/Locker/func_decors.md](./parts/RunServer/Util/Locker/func_decors.md)  
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
[Standalone doc: parts/RunServer/Util/Locker/locked.md](./parts/RunServer/Util/Locker/locked.md)  
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
[Standalone doc: parts/RunServer/Util/Locker/superclasses.md](./parts/RunServer/Util/Locker/superclasses.md)  
> superclasses(LockedResource, LR)

## `PerfCounter` (`RunServer.Util.PerfCounter` | `RS.U.PerfCounter`)
[`_rsruntime/util/perfcounter.py`](/_rsruntime/util/perfcounter.py "Source")  
[Standalone doc: parts/RunServer/Util/PerfCounter.md](./parts/RunServer/Util/PerfCounter.md)  
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
[Standalone doc: parts/RunServer/Util/TimedLoadDebug.md](./parts/RunServer/Util/TimedLoadDebug.md)  
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
[Standalone doc: parts/RunServer/Util/Timer.md](./parts/RunServer/Util/Timer.md)  

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


# `Flags` (`RunServer.Flags` | `RS.F`)
[Standalone doc: parts/RunServer/Flags.md](./parts/RunServer/Flags.md)  
> A simple attribute-based namespace.
> 
> SimpleNamespace(**kwargs)


# `Config` (`RunServer.Config` | `RS.C`)
[`_rsruntime/lib/rs_config.py`](/_rsruntime/lib/rs_config.py "Source")  
[Standalone doc: parts/RunServer/Config.md](./parts/RunServer/Config.md)  
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


# `ExceptionHandlers` (`RunServer.ExceptionHandlers` | `RS.EH`)
[`_rsruntime/lib/rs_exceptionhandlers.py`](/_rsruntime/lib/rs_exceptionhandlers.py "Source")  
[Standalone doc: parts/RunServer/ExceptionHandlers.md](./parts/RunServer/ExceptionHandlers.md)  

## hookin()
```python
def hookin()
```
[`_rsruntime/lib/rs_exceptionhandlers.py@38:41`](/_rsruntime/lib/rs_exceptionhandlers.py#L38)

<details>
<summary>Source Code</summary>

```python
def hookin(self):
    self._hookin_hooktype(sys, 'excepthook')
    self._hookin_hooktype(sys, 'unraisablehook')
    self._hookin_hooktype(threading, 'excepthook')
```
</details>

> <no doc>

## hookout()
```python
def hookout()
```
[`_rsruntime/lib/rs_exceptionhandlers.py@46:49`](/_rsruntime/lib/rs_exceptionhandlers.py#L46)

<details>
<summary>Source Code</summary>

```python
def hookout(self):
    self._hookout_hooktype(sys, 'excepthook')
    self._hookout_hooktype(sys, 'unraisablehook')
    self._hookout_hooktype(threading, 'excepthook')
```
</details>

> <no doc>

## register_exception_hook(...)
```python
def register_exception_hook(callback: Callable(type[BaseException], typing.Any | None, traceback))
```
[`_rsruntime/lib/rs_exceptionhandlers.py@54:55`](/_rsruntime/lib/rs_exceptionhandlers.py#L54)

<details>
<summary>Source Code</summary>

```python
def register_exception_hook(self, callback: typing.Callable[[typing.Type[BaseException], typing.Any | None, types.TracebackType], None]):
    self.exceptionhooks.register(callback)
```
</details>

> <no doc>

## register_thread_exception_hook(...)
```python
def register_thread_exception_hook(callback: Callable(_ExceptHookArgs))
```
[`_rsruntime/lib/rs_exceptionhandlers.py@58:59`](/_rsruntime/lib/rs_exceptionhandlers.py#L58)

<details>
<summary>Source Code</summary>

```python
def register_thread_exception_hook(self, callback: typing.Callable[[threading.ExceptHookArgs], None]):
    self.threadexceptionhooks.register(callback)
```
</details>

> <no doc>

## register_unraisable_hook(...)
```python
def register_unraisable_hook(callback: Callable(ForwardRef('UnraisableHookArgs')))
```
[`_rsruntime/lib/rs_exceptionhandlers.py@56:57`](/_rsruntime/lib/rs_exceptionhandlers.py#L56)

<details>
<summary>Source Code</summary>

```python
def register_unraisable_hook(self, callback: typing.Callable[['UnraisableHookArgs'], None]):
    self.unraisablehook.register(callback)
```
</details>

> <no doc>


# `MinecraftManager` (`RunServer.MinecraftManager` | `RS.MC`)
[`_rsruntime/lib/rs_mcmgr.py`](/_rsruntime/lib/rs_mcmgr.py "Source")  
[Standalone doc: parts/RunServer/MinecraftManager.md](./parts/RunServer/MinecraftManager.md)  

## init2()
```python
def init2()
```
[`_rsruntime/lib/rs_mcmgr.py@32:47`](/_rsruntime/lib/rs_mcmgr.py#L32)

<details>
<summary>Source Code</summary>

```python
def init2(self):
    if Config['minecraft/manager/auto_fetch_if_missing'] or Config['minecraft/manager/auto_update']:
        try: self.setup_manifest()
        except Exception as e:
            self.logger.fatal(f'Could not setup Minecraft version manifest:\n{"".join(traceback.format_exception(e))}')
            self.has_manifest = False
        else: self.has_manifest = True
    if not (p := Path(Config['minecraft/path/base'], Config['minecraft/path/server_jar'])).exists():
        self.logger.warning(f'{p} does not exist!')
        if not self.has_manifest:
            self.logger.irrec('Minecraft version manifest failed earlier; cannot continue')
            raise FileNotFoundError(str(p))
        if not Config['minecraft/manager/auto_fetch_if_missing']:
            self.logger.irrec('Config minecraft/manager/auto_fetch_if_missing is false, cannot download!')
            raise FileNotFoundError(str(p))
        self.missing_fetch()
```
</details>

> <no doc>

## missing_fetch()
```python
def missing_fetch()
```
[`_rsruntime/lib/rs_mcmgr.py@65:66`](/_rsruntime/lib/rs_mcmgr.py#L65)

<details>
<summary>Source Code</summary>

```python
def missing_fetch(self):
    ...
```
</details>

> <no doc>

## setup_manifest()
```python
def setup_manifest()
```
[`_rsruntime/lib/rs_mcmgr.py@49:63`](/_rsruntime/lib/rs_mcmgr.py#L49)

<details>
<summary>Source Code</summary>

```python
def setup_manifest(self):
    self.logger.info(f'Fetching {Config["minecraft/manager/version_manifest_url"]}')
    with request.urlopen(Config['minecraft/manager/version_manifest_url']) as r:
        data = json.load(r)
    tfmt = Config['minecraft/manager/time_fmt']
    versions = {v['id']: v | {
            'time': strptime(v['time'], tfmt), '_time': v['time'],
            'releaseTime': strptime(v['releaseTime'], tfmt), '_releaseTime': v['releaseTime']
        } for v in data['versions']}
    self.versions = self.VersionsType(versions=versions,
        latest=max((versions[data['latest']['release']], versions[data['latest']['snapshot']]), key=lambda v: v['time']),
        latest_release=versions[data['latest']['release']],
        latest_snapshot=versions[data['latest']['snapshot']],
        releases = {k: v for k,v in versions.items() if v['type'] == 'release'},
        snapshots = {k: v for k,v in versions.items() if v['type'] == 'snapshot'},
    )
```
</details>

> <no doc>


# `MCLang` (`RunServer.MCLang` | `RS.L`)
[`_rsruntime/lib/rs_lineparser.py`](/_rsruntime/lib/rs_lineparser.py "Source")  
[Standalone doc: parts/RunServer/MCLang.md](./parts/RunServer/MCLang.md)  

## extract_lang()
```python
def extract_lang() -> dict[str, str]
```
[`_rsruntime/lib/rs_lineparser.py@77:96`](/_rsruntime/lib/rs_lineparser.py#L77)
> Extracts the language file from a server JAR file, sets and returns self.lang

## init2()
```python
def init2()
```
[`_rsruntime/lib/rs_lineparser.py@30:31`](/_rsruntime/lib/rs_lineparser.py#L30)

<details>
<summary>Source Code</summary>

```python
def init2(self):
    self.extract_lang()
```
</details>

> <no doc>

## lang_to_pattern(...)
```python
def lang_to_pattern(lang: str, group_names: tuple[str, ...] | None = None, prefix_suffix: str = '^{}$') -> Pattern
```
[`_rsruntime/lib/rs_lineparser.py@41:75`](/_rsruntime/lib/rs_lineparser.py#L41)
> <no doc>

## strip_prefix(...)
```python
def strip_prefix(line: str) -> tuple[tuple[re.Match, time.struct_time] | None, str]
```
[`_rsruntime/lib/rs_lineparser.py@35:39`](/_rsruntime/lib/rs_lineparser.py#L35)

<details>
<summary>Source Code</summary>

```python
def strip_prefix(self, line: str) -> tuple[tuple[re.Match, time.struct_time] | None, str]:
    if (m := self.prefix.fullmatch(line)) is not None:
        # almost as bad as my first idea: `time.strptime(f'{m.time}|{time.strftime("%x")}', '%H:%M:%S|%x')`
        return ((m, time.struct_time(time.localtime()[:3] + time.strptime(m.group('time'), '%H:%M:%S')[3:6] + time.localtime()[6:])), m.group('line'))
    return (None, line)
```
</details>

> <no doc>


# `LineParser` (`RunServer.LineParser` | `RS.LP`)
[`_rsruntime/lib/rs_lineparser.py`](/_rsruntime/lib/rs_lineparser.py "Source")  
[Standalone doc: parts/RunServer/LineParser.md](./parts/RunServer/LineParser.md)  

## handle_line(...)
```python
def handle_line(line: str)
```
[`_rsruntime/lib/rs_lineparser.py@121:126`](/_rsruntime/lib/rs_lineparser.py#L121)

<details>
<summary>Source Code</summary>

```python
def handle_line(self, line: str):
    pfx, lin = RS.MCLang.strip_prefix(line)
    if pfx is None: return self.hooks_no_prefix(lin) # returns nothing!
    self.hooks_prefix(lin, *pfx)
    if (m := self.chat_patt.fullmatch(lin)) is not None:
        self.hooks_chat(RS.UserManager[m.group('username')], m.group('message'), bool(m.group('not_secure')))
```
</details>

> <no doc>

## init2()
```python
def init2()
```
[`_rsruntime/lib/rs_lineparser.py@106:107`](/_rsruntime/lib/rs_lineparser.py#L106)

<details>
<summary>Source Code</summary>

```python
def init2(self):
    self.chat_patt = RS.MCLang.lang_to_pattern(RS.MCLang.lang['chat.type.text'], ('username', 'message'), prefix_suffix=r'^(?P<not_secure>(?:\[Not Secure\] )?){}$')
```
</details>

> <no doc>

## register_callback(...)
```python
def register_callback(patt: Pattern, callback: Callable(Match, Match, struct_time) | Callable(Match), with_prefix: bool = True)
```
[`_rsruntime/lib/rs_lineparser.py@108:114`](/_rsruntime/lib/rs_lineparser.py#L108)

<details>
<summary>Source Code</summary>

```python
def register_callback(self, patt: re.Pattern, callback: typing.Callable[[re.Match, re.Match, time.struct_time], None] | typing.Callable[[re.Match], None], with_prefix: bool = True):
    '''
        Registers a callback
            If keep_prefix, then lines that have the prefix are passed. callback should have the signature: `callback(match: re.Match, prefix: re.Match, t: time.struct_time)`
            Otherwise, lines that don't have a prefix are passed; the callback should have the signature: `callback(match: re.Match)`
    '''
    (self.hooks_prefix if with_prefix else self.hooks_no_prefix).register(patt, callback)
```
</details>

> Registers a callback
> If keep_prefix, then lines that have the prefix are passed. callback should have the signature: `callback(match: re.Match, prefix: re.Match, t: time.struct_time)`
> Otherwise, lines that don't have a prefix are passed; the callback should have the signature: `callback(match: re.Match)`

## register_chat_callback(...)
```python
def register_chat_callback(callback: Callable(ForwardRef('RS.UM.User'), str, bool))
```
[`_rsruntime/lib/rs_lineparser.py@115:120`](/_rsruntime/lib/rs_lineparser.py#L115)

<details>
<summary>Source Code</summary>

```python
def register_chat_callback(self, callback: typing.Callable[[typing.ForwardRef('RS.UM.User'), str, bool], None]):
    '''
        Registers a callback for when chat is recieved
            The callback should have the signature `callback(user: RS.UserManager.User, message: str, insecure: bool)`
    '''
    self.hooks_chat.register(callback)
```
</details>

> Registers a callback for when chat is recieved
> The callback should have the signature `callback(user: RS.UserManager.User, message: str, insecure: bool)`


# `PluginManager` (`RunServer.PluginManager` | `RS.PM`)
[`_rsruntime/lib/rs_plugins.py`](/_rsruntime/lib/rs_plugins.py "Source")  
[Standalone doc: parts/RunServer/PluginManager.md](./parts/RunServer/PluginManager.md)  

## early_load_plugins()
```python
def early_load_plugins()
```
[`_rsruntime/lib/rs_plugins.py@171:179`](/_rsruntime/lib/rs_plugins.py#L171)

<details>
<summary>Source Code</summary>

```python
def early_load_plugins(self):
    self.ML.scrape_orphaned_manifests(Path(Config['plugins/plugins_path']))
    self.logger.infop('Loading manifests...')
    pc = PerfCounter()
    all(map(self.ML.update_execute, self.ML.discover_manifests(Path(Config['plugins/plugins_path']))))
    self.logger.infop(f'Manifests loaded after {pc}')
    pc = PerfCounter(sec='', secs='')
    for p in Path(Config['plugins/plugins_path']).glob(Config['plugins/glob/early_load']):
        self.logger.infop(f'Executing early load on {p} (T+{pc})')
```
</details>

> <no doc>

## load_plugins()
```python
def load_plugins()
```
[`_rsruntime/lib/rs_plugins.py@181:183`](/_rsruntime/lib/rs_plugins.py#L181)

<details>
<summary>Source Code</summary>

```python
def load_plugins(self):
    bp = Path(Config['plugins/plugins_path'])
    self._traverse_plugins(sorted(set(bp.glob(Config['plugins/glob/basic'])) | set(bp.glob(Config['plugins/glob/standalone']))), PerfCounter(sec='', secs=''))
```
</details>

> <no doc>

## restart()
```python
def restart()
```
[`_rsruntime/lib/rs_plugins.py@212:213`](/_rsruntime/lib/rs_plugins.py#L212)

<details>
<summary>Source Code</summary>

```python
def restart(self):
    self._pmagic('restart', 'Restarting plugin {plug_name}')
```
</details>

> <no doc>

## start()
```python
def start()
```
[`_rsruntime/lib/rs_plugins.py@210:211`](/_rsruntime/lib/rs_plugins.py#L210)

<details>
<summary>Source Code</summary>

```python
def start(self):
    self._pmagic('start', 'Starting plugin {plug_name}')
```
</details>

> <no doc>


# `ServerManager` (`RunServer.ServerManager` | `RS.SM`)
[`_rsruntime/lib/rs_servmgr.py`](/_rsruntime/lib/rs_servmgr.py "Source")  
[Standalone doc: parts/RunServer/ServerManager.md](./parts/RunServer/ServerManager.md)  

## preferred_order()
```python
@classmethod
def preferred_order() -> list[type[BaseServerManager]]
```
[`_rsruntime/lib/rs_servmgr.py@198:200`](/_rsruntime/lib/rs_servmgr.py#L198)

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
[`_rsruntime/lib/rs_servmgr.py@195:197`](/_rsruntime/lib/rs_servmgr.py#L195)

<details>
<summary>Source Code</summary>

```python
@classmethod
def register(cls, manager_type: typing.Type[BaseServerManager]):
    setattr(cls.managers, manager_type.name.replace('.', '_'), manager_type)
```
</details>

> <no doc>


# `UserManager` (`RunServer.UserManager` | `RS.UM`)
[`_rsruntime/lib/rs_usermgr.py`](/_rsruntime/lib/rs_usermgr.py "Source")  
[Standalone doc: parts/RunServer/UserManager.md](./parts/RunServer/UserManager.md)  

## close()
```python
def close()
```
[`_rsruntime/lib/rs_usermgr.py@169:171`](/_rsruntime/lib/rs_usermgr.py#L169)

<details>
<summary>Source Code</summary>

```python
def close(self):
    self.fbd.stop_autosync()
    self.fbd.sync()
```
</details>

> <no doc>

## init2()
```python
def init2()
```
[`_rsruntime/lib/rs_usermgr.py@147:163`](/_rsruntime/lib/rs_usermgr.py#L147)

<details>
<summary>Source Code</summary>

```python
def init2(self):
    # Register hooks
    LineParser.register_callback( # player joins
        MCLang.lang_to_pattern(MCLang.lang['multiplayer.player.joined'], ('username',)),
        lambda m,p,t: self[m.group('username')](connected=True, last_connected=t))
    LineParser.register_callback( # player joins, has changed name
        MCLang.lang_to_pattern(MCLang.lang['multiplayer.player.joined.renamed'], ('username', 'old_name')),
        lambda m,p,t: self[m.group('username')](connected=True, old_name=m.group('old_name'), last_connected=t))
    LineParser.register_callback( # player leaves
        MCLang.lang_to_pattern(MCLang.lang['multiplayer.player.left'], ('username',)),
        lambda m,p,t: self[m.group('username')](connected=False, last_disconnected=t))
    LineParser.register_callback( # player is assigned UUID
        re.compile(r'^UUID of player (?P<username>\w+) is (?P<uuid>[a-z0-6\-]+)$'),
        lambda m,p,t: self[m.group('username')](uuid=m.group('uuid')))
    LineParser.register_callback( # player is assigned entity ID and origin
        re.compile(r'^(?P<username>\w+)\[\/(?P<origin>(?P<ip>[\d.]+):(?P<port>[\d]+))\] logged in with entity id (?P<entity_id>[\d]+) at \((?P<x>\-?[\d.]+), (?P<y>\-?[\d.]+), (?P<z>\-?[\d.]+)\)$'),
        lambda p,t,m: self[m.group('username')](ip=m.group('ip'), port=int(m.group('port')), origin=m.group('origin'), login_coords=(float(m.group('x')), float(m.group('y')), float(m.group('z')))))
```
</details>

> <no doc>


# `TellRaw` (`RunServer.TellRaw` | `RS.TR`)
[`_rsruntime/lib/rs_userio.py`](/_rsruntime/lib/rs_userio.py "Source")  
[Standalone doc: parts/RunServer/TellRaw.md](./parts/RunServer/TellRaw.md)  
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


# `ChatCommands` (`RunServer.ChatCommands` | `RS.CC`)
[`_rsruntime/lib/rs_userio.py`](/_rsruntime/lib/rs_userio.py "Source")  
[Standalone doc: parts/RunServer/ChatCommands.md](./parts/RunServer/ChatCommands.md)  

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


# `Convenience` (`RunServer.Convenience` | `RS._`)
[Standalone doc: parts/RunServer/Convenience.md](./parts/RunServer/Convenience.md)  

## `command` (`RunServer.Convenience.command` | `RS._.command`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/command.md](./parts/RunServer/Convenience/command.md)  
> Writes a command to the server
>> Equivelant to RS.SM.write(line)

## `inject_line` (`RunServer.Convenience.inject_line` | `RS._.inject_line`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/inject_line.md](./parts/RunServer/Convenience/inject_line.md)  
> Injects a line into LineParser, as if it was read from the ServerManager
>> Equivelant to RS.LP.handle_line(line)

## `listen_chat` (`RunServer.Convenience.listen_chat` | `RS._.listen_chat`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/listen_chat.md](./parts/RunServer/Convenience/listen_chat.md)  
> Registers a callback for when LineParser reads a chat message
>> The callback should have three arguments:
>> - the user (RS.UM.User object)
>> - the line (str)
>> - if the message was "not secure" (bool)

## `say` (`RunServer.Convenience.say` | `RS._.say`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/say.md](./parts/RunServer/Convenience/say.md)  

## `tell` (`RunServer.Convenience.tell` | `RS._.tell`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/tell.md](./parts/RunServer/Convenience/tell.md)  

## `tellraw` (`RunServer.Convenience.tellraw` | `RS._.tellraw`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/tellraw.md](./parts/RunServer/Convenience/tellraw.md)  
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
