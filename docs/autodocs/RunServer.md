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
[`_rsruntime/rs_BOOTSTRAP.py@209:213`](/_rsruntime/rs_BOOTSTRAP.py#L209)  
> Loads the entrypoint's surrounding module

## bootstrap(...)
```python
def bootstrap(close_after: bool = True)
```
[`_rsruntime/rs_BOOTSTRAP.py@182:195`](/_rsruntime/rs_BOOTSTRAP.py#L182)  
> Executes the base manifest, then accesses, assigns, and chainloads the entrypoint

## chainload_entrypoint(...)
```python
def chainload_entrypoint(rs: Callable)
```
[`_rsruntime/rs_BOOTSTRAP.py@218:222`](/_rsruntime/rs_BOOTSTRAP.py#L218)  
> Runs the entrypoint's __call__ method

## close(...)
```python
def close(do_exit: bool | int = False)
```
[`_rsruntime/rs_BOOTSTRAP.py@226:234`](/_rsruntime/rs_BOOTSTRAP.py#L226)  
> Executes all shutdown callbacks and closes logging (logging.shutdown()), and exits with exit code do_exit if it isn't False

## ensure_python_version()
```python
@classmethod
def ensure_python_version()
```
[`_rsruntime/rs_BOOTSTRAP.py@69:73`](/_rsruntime/rs_BOOTSTRAP.py#L69)  
> Ensure that the Python version meets the minimum requirements

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
[`_rsruntime/rs_BOOTSTRAP.py@235:237`](/_rsruntime/rs_BOOTSTRAP.py#L235)  
> Registers a function to run when self.close() is called

## run_base_manifest()
```python
def run_base_manifest()
```
[`_rsruntime/rs_BOOTSTRAP.py@197:207`](/_rsruntime/rs_BOOTSTRAP.py#L197)  
> Executes the base manifest (_rsruntime/MANIFEST.ini)

## setup_logger()
```python
def setup_logger() -> logging.Logger
```
[`_rsruntime/rs_BOOTSTRAP.py@95:178`](/_rsruntime/rs_BOOTSTRAP.py#L95)  
> Sets up self.logger, as well as logging.INFOPLUS/IRRECOVERABLE and Logger.infop/irrec()

## stage_entrypoint(...)
```python
def stage_entrypoint(rs_outer: types.ModuleType) -> rs_outer.RunServer
```
[`_rsruntime/rs_BOOTSTRAP.py@214:217`](/_rsruntime/rs_BOOTSTRAP.py#L214)  
> Initializes the entrypoint's class (with self as an argument)
**[Standalone: parts/RunServer/Bootstrapper.md](./parts/RunServer/Bootstrapper.md)**


# `Util` (`RunServer.Util` | `RS.U`)

[Standalone doc: parts/RunServer/Util.md](./parts/RunServer/Util.md)  



# `BetterPPrinter` (`RunServer.Util.BetterPPrinter` | `RS.U.BetterPPrinter`)
[`_rsruntime/util/betterprettyprinter.py`](/_rsruntime/util/betterprettyprinter.py "Source")  
[Standalone doc: parts/RunServer/Util/BetterPPrinter.md](./parts/RunServer/Util/BetterPPrinter.md)  

### format(...)
```python
@staticmethod
def format(self, obj, _indent_: int = 0) -> Generator
```
[`_rsruntime/util/betterprettyprinter.py@35:67`](/_rsruntime/util/betterprettyprinter.py#L35)  
> <no doc>

### formats(...)
```python
@staticmethod
def formats(self, obj, joiner: str = ) -> str
```
[`_rsruntime/util/betterprettyprinter.py@68:69`](/_rsruntime/util/betterprettyprinter.py#L68)  
> <no doc>

### writes(...)
```python
@staticmethod
def writes(...)
```
<details><summary>Parameters...</summary>
```python
    self, obj, fp=<_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>,
    end: str = 
, delay: float | None = None, collect: list | Callable | NoneType = None
```
</details>
[`_rsruntime/util/betterprettyprinter.py@70:78`](/_rsruntime/util/betterprettyprinter.py#L70)  
> <no doc>
**[Standalone: parts/RunServer/Util/BetterPPrinter.md](./parts/RunServer/Util/BetterPPrinter.md)**



# `Hooks` (`RunServer.Util.Hooks` | `RS.U.Hooks`)
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
> Adds a callback to be called by __call__(hook)

### unregister(...)
```python
@staticmethod
def unregister(self, hook: HookType, callback: FuncType)
```
[`_rsruntime/util/hooks.py@26:29`](/_rsruntime/util/hooks.py#L26)  
> Removes a callback that would be called by __call__(hook) (if it exists)

### unregister_hook(...)
```python
@staticmethod
def unregister_hook(self, hook: HookType)
```
[`_rsruntime/util/hooks.py@30:33`](/_rsruntime/util/hooks.py#L30)  
> Deletes all callbacks that would be called by __call__(hook)
**[Standalone: parts/RunServer/Util/Hooks.md](./parts/RunServer/Util/Hooks.md)**



# `INIBackedDict` (`RunServer.Util.INIBackedDict` | `RS.U.INIBackedDict`)
[`_rsruntime/util/fbd.py`](/_rsruntime/util/fbd.py "Source")  
[Standalone doc: parts/RunServer/Util/INIBackedDict.md](./parts/RunServer/Util/INIBackedDict.md)  
> A FileBackedDict implementation that uses ConfigParser as a backend

### bettergetter(...)
```python
@staticmethod
def bettergetter(...) -> Deserialized | Any
```
<details><summary>Parameters...</summary>
```python
    self, key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Any = Behavior.RAISE,
    set_default: bool = True
```
</details>
[`_rsruntime/util/fbd.py@137:153`](/_rsruntime/util/fbd.py#L137)  
> Gets the value of key
>> If the key is missing, then:
>>> if default is Behavior.RAISE: raises KeyError
>>> otherwise: returns default, and if set_default is truthy then sets the key to default

### contains(...)
```python
@staticmethod
def contains(self, key: Key, _tree: MutableMapping | NoneType = None) -> bool
```
[`_rsruntime/util/fbd.py@188:194`](/_rsruntime/util/fbd.py#L188)  
> Returns whether or not the key exists

### get(...)
```python
@staticmethod
def get(...) -> Deserialized
```
<details><summary>Parameters...</summary>
```python
    self, key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Serializable = Behavior.RAISE,
    _tree: MutableMapping | NoneType = None
```
</details>
[`_rsruntime/util/fbd.py@160:175`](/_rsruntime/util/fbd.py#L160)  
> Gets the value of key
>> If the key is missing, then raises KeyError if default is Behavior.RAISE, otherwise returns default

### get(...)
```python
@staticmethod
def get(...) -> Deserialized
```
<details><summary>Parameters...</summary>
```python
    self, key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Serializable = Behavior.RAISE,
    _tree: MutableMapping | NoneType = None
```
</details>
[`_rsruntime/util/fbd.py@160:175`](/_rsruntime/util/fbd.py#L160)  
> Gets the value of key
>> If the key is missing, then raises KeyError if default is Behavior.RAISE, otherwise returns default

### is_autosyncing(...)
```python
@staticmethod
def is_autosyncing(self) -> bool
```
[`_rsruntime/util/fbd.py@97:100`](/_rsruntime/util/fbd.py#L97)  
> Returns whether or not the internal watchdog timer is ticking

### items_full(...)
```python
@staticmethod
def items_full(self, start_key: Key, key_join: bool = True) -> Generator
```
[`_rsruntime/util/fbd.py@197:200`](/_rsruntime/util/fbd.py#L197)  
> Iterates over every (key, value) pair, yielding the entire key

### items_short(...)
```python
@staticmethod
def items_short(self, start_key: Key)
```
[`_rsruntime/util/fbd.py@201:204`](/_rsruntime/util/fbd.py#L201)  
> Iterates over every (key, value) pair, yielding the last part of the key

### key(...)
```python
@classmethod
def key(key: Key, top_level: bool = False) -> tuple
```
[`_rsruntime/util/fbd.py@65:78`](/_rsruntime/util/fbd.py#L65)  
> Transform a string / tuple of strings into a key

### keys(...)
```python
@staticmethod
def keys(self, start_key: Key | None = None, key_join: bool = True) -> Generator
```
[`_rsruntime/util/fbd.py@205:214`](/_rsruntime/util/fbd.py#L205)  
> Iterates over every key

### path_from_topkey(...)
```python
@staticmethod
def path_from_topkey(self, topkey: str)
```
[`_rsruntime/util/fbd.py@79:81`](/_rsruntime/util/fbd.py#L79)  
> Returns the Path corresponding to the top-key's file

### readin(...)
```python
@staticmethod
def readin(self, topkey: str)
```
[`_rsruntime/util/fbd.py@127:132`](/_rsruntime/util/fbd.py#L127)  
> Reads in a top-level key

### readin_modified(...)
```python
@staticmethod
def readin_modified(self)
```
[`_rsruntime/util/fbd.py@116:126`](/_rsruntime/util/fbd.py#L116)  
> Reads in top-level keys that have been changed

### setitem(...)
```python
@staticmethod
def setitem(...)
```
<details><summary>Parameters...</summary>
```python
    self, key: Key, val: Serializable,
    _tree: MutableMapping | NoneType = None
```
</details>
[`_rsruntime/util/fbd.py@178:185`](/_rsruntime/util/fbd.py#L178)  
> Sets a key to a value

### sort(...)
```python
@staticmethod
def sort(self, by: Callable = <lambda>)
```
[`_rsruntime/util/fbd.py@277:283`](/_rsruntime/util/fbd.py#L277)  
> Sorts the data of this INIBackedDict in-place, marking all touched sections as dirty

### start_autosync(...)
```python
@staticmethod
def start_autosync(self)
```
[`_rsruntime/util/fbd.py@89:92`](/_rsruntime/util/fbd.py#L89)  
> Starts the internal watchdog timer

### stop_autosync(...)
```python
@staticmethod
def stop_autosync(self)
```
[`_rsruntime/util/fbd.py@93:96`](/_rsruntime/util/fbd.py#L93)  
> Stops the internal watchdog timer

### sync(...)
```python
@staticmethod
def sync(self)
```
[`_rsruntime/util/fbd.py@83:87`](/_rsruntime/util/fbd.py#L83)  
> Convenience method for writeback_dirty and readin_modified

### values(...)
```python
@staticmethod
def values(self, start_key: Key) -> Generator
```
[`_rsruntime/util/fbd.py@216:219`](/_rsruntime/util/fbd.py#L216)  
> Iterates over every value

### writeback(...)
```python
@staticmethod
def writeback(...)
```
<details><summary>Parameters...</summary>
```python
    self, topkey: str, only_if_dirty: bool = True,
    clean: bool = True
```
</details>
[`_rsruntime/util/fbd.py@106:112`](/_rsruntime/util/fbd.py#L106)  
> Writes back a top-level key

### writeback_dirty(...)
```python
@staticmethod
def writeback_dirty(self)
```
[`_rsruntime/util/fbd.py@102:105`](/_rsruntime/util/fbd.py#L102)  
> <no doc>
**[Standalone: parts/RunServer/Util/INIBackedDict.md](./parts/RunServer/Util/INIBackedDict.md)**



# `JSONBackedDict` (`RunServer.Util.JSONBackedDict` | `RS.U.JSONBackedDict`)
[`_rsruntime/util/fbd.py`](/_rsruntime/util/fbd.py "Source")  
[Standalone doc: parts/RunServer/Util/JSONBackedDict.md](./parts/RunServer/Util/JSONBackedDict.md)  
> A FileBackedDict implementation that uses JSON as a backend

### bettergetter(...)
```python
@staticmethod
def bettergetter(...) -> Deserialized | Any
```
<details><summary>Parameters...</summary>
```python
    self, key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Any = Behavior.RAISE,
    set_default: bool = True
```
</details>
[`_rsruntime/util/fbd.py@137:153`](/_rsruntime/util/fbd.py#L137)  
> Gets the value of key
>> If the key is missing, then:
>>> if default is Behavior.RAISE: raises KeyError
>>> otherwise: returns default, and if set_default is truthy then sets the key to default

### contains(...)
```python
@staticmethod
def contains(self, key: Key, _tree: MutableMapping | NoneType = None) -> bool
```
[`_rsruntime/util/fbd.py@188:194`](/_rsruntime/util/fbd.py#L188)  
> Returns whether or not the key exists

### get(...)
```python
@staticmethod
def get(...) -> Deserialized
```
<details><summary>Parameters...</summary>
```python
    self, key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Serializable = Behavior.RAISE,
    _tree: MutableMapping | NoneType = None
```
</details>
[`_rsruntime/util/fbd.py@160:175`](/_rsruntime/util/fbd.py#L160)  
> Gets the value of key
>> If the key is missing, then raises KeyError if default is Behavior.RAISE, otherwise returns default

### get(...)
```python
@staticmethod
def get(...) -> Deserialized
```
<details><summary>Parameters...</summary>
```python
    self, key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Serializable = Behavior.RAISE,
    _tree: MutableMapping | NoneType = None
```
</details>
[`_rsruntime/util/fbd.py@160:175`](/_rsruntime/util/fbd.py#L160)  
> Gets the value of key
>> If the key is missing, then raises KeyError if default is Behavior.RAISE, otherwise returns default

### is_autosyncing(...)
```python
@staticmethod
def is_autosyncing(self) -> bool
```
[`_rsruntime/util/fbd.py@97:100`](/_rsruntime/util/fbd.py#L97)  
> Returns whether or not the internal watchdog timer is ticking

### items_full(...)
```python
@staticmethod
def items_full(self, start_key: Key, key_join: bool = True) -> Generator
```
[`_rsruntime/util/fbd.py@197:200`](/_rsruntime/util/fbd.py#L197)  
> Iterates over every (key, value) pair, yielding the entire key

### items_short(...)
```python
@staticmethod
def items_short(self, start_key: Key)
```
[`_rsruntime/util/fbd.py@201:204`](/_rsruntime/util/fbd.py#L201)  
> Iterates over every (key, value) pair, yielding the last part of the key

### key(...)
```python
@classmethod
def key(key: Key, top_level: bool = False) -> tuple
```
[`_rsruntime/util/fbd.py@65:78`](/_rsruntime/util/fbd.py#L65)  
> Transform a string / tuple of strings into a key

### keys(...)
```python
@staticmethod
def keys(self, start_key: Key | None = None, key_join: bool = True) -> Generator
```
[`_rsruntime/util/fbd.py@205:214`](/_rsruntime/util/fbd.py#L205)  
> Iterates over every key

### path_from_topkey(...)
```python
@staticmethod
def path_from_topkey(self, topkey: str)
```
[`_rsruntime/util/fbd.py@79:81`](/_rsruntime/util/fbd.py#L79)  
> Returns the Path corresponding to the top-key's file

### readin(...)
```python
@staticmethod
def readin(self, topkey: str)
```
[`_rsruntime/util/fbd.py@127:132`](/_rsruntime/util/fbd.py#L127)  
> Reads in a top-level key

### readin_modified(...)
```python
@staticmethod
def readin_modified(self)
```
[`_rsruntime/util/fbd.py@116:126`](/_rsruntime/util/fbd.py#L116)  
> Reads in top-level keys that have been changed

### setitem(...)
```python
@staticmethod
def setitem(...)
```
<details><summary>Parameters...</summary>
```python
    self, key: Key, val: Serializable,
    _tree: MutableMapping | NoneType = None
```
</details>
[`_rsruntime/util/fbd.py@178:185`](/_rsruntime/util/fbd.py#L178)  
> Sets a key to a value

### sort(...)
```python
@staticmethod
def sort(self, by: Callable = <lambda>)
```
[`_rsruntime/util/fbd.py@374:378`](/_rsruntime/util/fbd.py#L374)  
> Sorts the data of this JSONBackedDict (semi-)in-place, marking all touched sections as dirty

### start_autosync(...)
```python
@staticmethod
def start_autosync(self)
```
[`_rsruntime/util/fbd.py@89:92`](/_rsruntime/util/fbd.py#L89)  
> Starts the internal watchdog timer

### stop_autosync(...)
```python
@staticmethod
def stop_autosync(self)
```
[`_rsruntime/util/fbd.py@93:96`](/_rsruntime/util/fbd.py#L93)  
> Stops the internal watchdog timer

### sync(...)
```python
@staticmethod
def sync(self)
```
[`_rsruntime/util/fbd.py@83:87`](/_rsruntime/util/fbd.py#L83)  
> Convenience method for writeback_dirty and readin_modified

### values(...)
```python
@staticmethod
def values(self, start_key: Key) -> Generator
```
[`_rsruntime/util/fbd.py@216:219`](/_rsruntime/util/fbd.py#L216)  
> Iterates over every value

### writeback(...)
```python
@staticmethod
def writeback(...)
```
<details><summary>Parameters...</summary>
```python
    self, topkey: str, only_if_dirty: bool = True,
    clean: bool = True
```
</details>
[`_rsruntime/util/fbd.py@106:112`](/_rsruntime/util/fbd.py#L106)  
> Writes back a top-level key

### writeback_dirty(...)
```python
@staticmethod
def writeback_dirty(self)
```
[`_rsruntime/util/fbd.py@102:105`](/_rsruntime/util/fbd.py#L102)  
> <no doc>
**[Standalone: parts/RunServer/Util/JSONBackedDict.md](./parts/RunServer/Util/JSONBackedDict.md)**



# `Locker` (`RunServer.Util.Locker` | `RS.U.Locker`)

[Standalone doc: parts/RunServer/Util/Locker.md](./parts/RunServer/Util/Locker.md)  



# `LockedResource` (`RunServer.Util.Locker.LockedResource` | `RS.U.Locker.LockedResource`)
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
**[Standalone: parts/RunServer/Util/Locker/LockedResource.md](./parts/RunServer/Util/Locker/LockedResource.md)**



# `b` (`RunServer.Util.Locker.b` | `RS.U.Locker.b`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/b.md](./parts/RunServer/Util/Locker/b.md)  
> basic(LockedResource, LR, locked, lockd)

#### count(...)
```python
def count(value)
```
> Return number of occurrences of value.

#### index(...)
```python
def index(value, start=0, stop=9223372036854775807)
```
> Return first index of value.
> 
> Raises ValueError if the value is not present.

#### locked(...)
```python
@staticmethod
def locked(func: Callable)
```
[`_rsruntime/util/locked_resource.py@76:92`](/_rsruntime/util/locked_resource.py#L76)  
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
> Waits to acquire the method's self's .lock attribute (uses "with")
> This should be used in tandem with the LockedResource superclass:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock
>>>> print("initialized!")
>>> @locked # note decorator
>>> def test_lock(self):
>>>> print("lock acquired!")
**[Standalone: parts/RunServer/Util/Locker/b.md](./parts/RunServer/Util/Locker/b.md)**



# `basic` (`RunServer.Util.Locker.basic` | `RS.U.Locker.basic`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/basic.md](./parts/RunServer/Util/Locker/basic.md)  
> basic(LockedResource, LR, locked, lockd)

#### count(...)
```python
def count(value)
```
> Return number of occurrences of value.

#### index(...)
```python
def index(value, start=0, stop=9223372036854775807)
```
> Return first index of value.
> 
> Raises ValueError if the value is not present.

#### locked(...)
```python
@staticmethod
def locked(func: Callable)
```
[`_rsruntime/util/locked_resource.py@76:92`](/_rsruntime/util/locked_resource.py#L76)  
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
> Waits to acquire the method's self's .lock attribute (uses "with")
> This should be used in tandem with the LockedResource superclass:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock
>>>> print("initialized!")
>>> @locked # note decorator
>>> def test_lock(self):
>>>> print("lock acquired!")
**[Standalone: parts/RunServer/Util/Locker/basic.md](./parts/RunServer/Util/Locker/basic.md)**



# `cls` (`RunServer.Util.Locker.cls` | `RS.U.Locker.cls`)
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

#### count(...)
```python
def count(value)
```
> Return number of occurrences of value.

#### iclasslocked(...)
```python
@staticmethod
def iclasslocked(func: Callable)
```
[`_rsruntime/util/locked_resource.py@113:123`](/_rsruntime/util/locked_resource.py#L113)  
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
> Is the same as @classlocked (it even calls it), but also wraps the method in classmethod
> Meant to be used with @LockedClass:
>> @LockedClass()
>> class Locked:
>>> @iclasslocked
>>> def classlocked_classmethod(cls):
>>>> print("class lock acquired!")

#### index(...)
```python
def index(value, start=0, stop=9223372036854775807)
```
> Return first index of value.
> 
> Raises ValueError if the value is not present.
**[Standalone: parts/RunServer/Util/Locker/cls.md](./parts/RunServer/Util/Locker/cls.md)**



# `cls_decors` (`RunServer.Util.Locker.cls_decors` | `RS.U.Locker.cls_decors`)
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

#### count(...)
```python
def count(value)
```
> Return number of occurrences of value.

#### index(...)
```python
def index(value, start=0, stop=9223372036854775807)
```
> Return first index of value.
> 
> Raises ValueError if the value is not present.
**[Standalone: parts/RunServer/Util/Locker/cls_decors.md](./parts/RunServer/Util/Locker/cls_decors.md)**



# `etc` (`RunServer.Util.Locker.etc` | `RS.U.Locker.etc`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/etc.md](./parts/RunServer/Util/Locker/etc.md)  
> etc(locked_by, lockdby)

#### count(...)
```python
def count(value)
```
> Return number of occurrences of value.

#### index(...)
```python
def index(value, start=0, stop=9223372036854775807)
```
> Return first index of value.
> 
> Raises ValueError if the value is not present.

#### locked_by(...)
```python
@staticmethod
def locked_by(lock: AbstractContextManager)
```
[`_rsruntime/util/locked_resource.py@125:132`](/_rsruntime/util/locked_resource.py#L125)  
> <no doc>

#### locked_by(...)
```python
@staticmethod
def locked_by(lock: AbstractContextManager)
```
[`_rsruntime/util/locked_resource.py@125:132`](/_rsruntime/util/locked_resource.py#L125)  
> <no doc>
**[Standalone: parts/RunServer/Util/Locker/etc.md](./parts/RunServer/Util/Locker/etc.md)**



# `func_decors` (`RunServer.Util.Locker.func_decors` | `RS.U.Locker.func_decors`)
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

#### count(...)
```python
def count(value)
```
> Return number of occurrences of value.

#### iclasslocked(...)
```python
@staticmethod
def iclasslocked(func: Callable)
```
[`_rsruntime/util/locked_resource.py@113:123`](/_rsruntime/util/locked_resource.py#L113)  
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
> Is the same as @classlocked (it even calls it), but also wraps the method in classmethod
> Meant to be used with @LockedClass:
>> @LockedClass()
>> class Locked:
>>> @iclasslocked
>>> def classlocked_classmethod(cls):
>>>> print("class lock acquired!")

#### index(...)
```python
def index(value, start=0, stop=9223372036854775807)
```
> Return first index of value.
> 
> Raises ValueError if the value is not present.

#### locked(...)
```python
@staticmethod
def locked(func: Callable)
```
[`_rsruntime/util/locked_resource.py@76:92`](/_rsruntime/util/locked_resource.py#L76)  
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
> <no doc>

#### locked_by(...)
```python
@staticmethod
def locked_by(lock: AbstractContextManager)
```
[`_rsruntime/util/locked_resource.py@125:132`](/_rsruntime/util/locked_resource.py#L125)  
> <no doc>
**[Standalone: parts/RunServer/Util/Locker/func_decors.md](./parts/RunServer/Util/Locker/func_decors.md)**



# `locked` (`RunServer.Util.Locker.locked` | `RS.U.Locker.locked`)
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
**[Standalone: parts/RunServer/Util/Locker/locked.md](./parts/RunServer/Util/Locker/locked.md)**



# `superclasses` (`RunServer.Util.Locker.superclasses` | `RS.U.Locker.superclasses`)
[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/superclasses.md](./parts/RunServer/Util/Locker/superclasses.md)  
> superclasses(LockedResource, LR)

#### count(...)
```python
def count(value)
```
> Return number of occurrences of value.

#### index(...)
```python
def index(value, start=0, stop=9223372036854775807)
```
> Return first index of value.
> 
> Raises ValueError if the value is not present.
**[Standalone: parts/RunServer/Util/Locker/superclasses.md](./parts/RunServer/Util/Locker/superclasses.md)**
**[Standalone: parts/RunServer/Util/Locker.md](./parts/RunServer/Util/Locker.md)**



# `PerfCounter` (`RunServer.Util.PerfCounter` | `RS.U.PerfCounter`)
[`_rsruntime/util/perfcounter.py`](/_rsruntime/util/perfcounter.py "Source")  
[Standalone doc: parts/RunServer/Util/PerfCounter.md](./parts/RunServer/Util/PerfCounter.md)  
> Provides an object-oriented (because why not) way to use (and format) time.perf_counter

### as_integer_ratio(...)
```python
@staticmethod
def as_integer_ratio(self)
```
> Return a pair of integers, whose ratio is exactly equal to the original float.
> 
> The ratio is in lowest terms and has a positive denominator.  Raise
> OverflowError on infinities and a ValueError on NaNs.
> 
> >>> (10.0).as_integer_ratio()
> (10, 1)
> >>> (0.0).as_integer_ratio()
> (0, 1)
> >>> (-.25).as_integer_ratio()
> (-1, 4)

### conjugate(...)
```python
@staticmethod
def conjugate(self)
```
> Return self, the complex conjugate of any float.

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

### hex(...)
```python
@staticmethod
def hex(self)
```
> Return a hexadecimal representation of a floating-point number.
> 
> >>> (-0.1).hex()
> '-0x1.999999999999ap-4'
> >>> 3.14159.hex()
> '0x1.921f9f01b866ep+1'

### is_integer(...)
```python
@staticmethod
def is_integer(self)
```
> Return True if the float is an integer.
**[Standalone: parts/RunServer/Util/PerfCounter.md](./parts/RunServer/Util/PerfCounter.md)**



# `Timer` (`RunServer.Util.Timer` | `RS.U.Timer`)
[`_rsruntime/util/timer.py`](/_rsruntime/util/timer.py "Source")  
[Standalone doc: parts/RunServer/Util/Timer.md](./parts/RunServer/Util/Timer.md)  

### clear(...)
```python
@staticmethod
def clear(timer: BaseTimer) -> BaseTimer
```
[`_rsruntime/util/timer.py@84:86`](/_rsruntime/util/timer.py#L84)  
> <no doc>

### set_timer(...)
```python
@staticmethod
def set_timer(...) -> Timer.BaseTimer
```
<details><summary>Parameters...</summary>
```python
    timer_type: type, func: Callable, secs: float,
    activate_now: bool = True
```
</details>
[`_rsruntime/util/timer.py@80:83`](/_rsruntime/util/timer.py#L80)  
> <no doc>
**[Standalone: parts/RunServer/Util/Timer.md](./parts/RunServer/Util/Timer.md)**
**[Standalone: parts/RunServer/Util.md](./parts/RunServer/Util.md)**


# `Flags` (`RunServer.Flags` | `RS.F`)
[Standalone doc: parts/RunServer/Flags.md](./parts/RunServer/Flags.md)  
> A simple attribute-based namespace.
> 
> SimpleNamespace(**kwargs)
**[Standalone: parts/RunServer/Flags.md](./parts/RunServer/Flags.md)**


# `Config` (`RunServer.Config` | `RS.C`)
[`_rsruntime/lib/rs_config.py`](/_rsruntime/lib/rs_config.py "Source")  
[Standalone doc: parts/RunServer/Config.md](./parts/RunServer/Config.md)  
> A thin wrapper around INIBackedDict

## bettergetter(...)
```python
def bettergetter(key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Any = Behavior.RAISE, set_default: bool = True) -> Deserialized | Any
```
[`_rsruntime/util/fbd.py@137:153`](/_rsruntime/util/fbd.py#L137)  
> Gets the value of key
>> If the key is missing, then:
>>> if default is Behavior.RAISE: raises KeyError
>>> otherwise: returns default, and if set_default is truthy then sets the key to default

## close()
```python
def close()
```
[`_rsruntime/lib/rs_config.py@65:68`](/_rsruntime/lib/rs_config.py#L65)  
> <no doc>

## contains(...)
```python
def contains(key: Key, _tree: MutableMapping | NoneType = None) -> bool
```
[`_rsruntime/util/locked_resource.py@88:91`](/_rsruntime/util/locked_resource.py#L88)  
> Returns whether or not the key exists

## get(...)
```python
def get(key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Serializable = Behavior.RAISE, _tree: MutableMapping | NoneType = None) -> Deserialized
```
[`_rsruntime/util/locked_resource.py@88:91`](/_rsruntime/util/locked_resource.py#L88)  
> Gets the value of key
>> If the key is missing, then raises KeyError if default is Behavior.RAISE, otherwise returns default

## get(...)
```python
def get(key: Key, default: ForwardRef('FileBackedDict.Behavior.RAISE') | Serializable = Behavior.RAISE, _tree: MutableMapping | NoneType = None) -> Deserialized
```
[`_rsruntime/util/locked_resource.py@88:91`](/_rsruntime/util/locked_resource.py#L88)  
> Gets the value of key
>> If the key is missing, then raises KeyError if default is Behavior.RAISE, otherwise returns default

## is_autosyncing()
```python
def is_autosyncing() -> bool
```
[`_rsruntime/util/locked_resource.py@88:91`](/_rsruntime/util/locked_resource.py#L88)  
> Returns whether or not the internal watchdog timer is ticking

## items_full(...)
```python
def items_full(start_key: Key, key_join: bool = True) -> Generator
```
[`_rsruntime/util/locked_resource.py@88:91`](/_rsruntime/util/locked_resource.py#L88)  
> Iterates over every (key, value) pair, yielding the entire key

## items_short(...)
```python
def items_short(start_key: Key)
```
[`_rsruntime/util/locked_resource.py@88:91`](/_rsruntime/util/locked_resource.py#L88)  
> Iterates over every (key, value) pair, yielding the last part of the key

## key(...)
```python
@classmethod
def key(key: Key, top_level: bool = False) -> tuple
```
[`_rsruntime/util/fbd.py@65:78`](/_rsruntime/util/fbd.py#L65)  
> Transform a string / tuple of strings into a key

## keys(...)
```python
def keys(start_key: Key | None = None, key_join: bool = True) -> Generator
```
[`_rsruntime/util/locked_resource.py@88:91`](/_rsruntime/util/locked_resource.py#L88)  
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
> Returns the Path corresponding to the top-key's file

## readin(...)
```python
def readin(topkey: str)
```
[`_rsruntime/util/locked_resource.py@88:91`](/_rsruntime/util/locked_resource.py#L88)  
> Reads in a top-level key

## readin_modified()
```python
def readin_modified()
```
[`_rsruntime/util/locked_resource.py@88:91`](/_rsruntime/util/locked_resource.py#L88)  
> Reads in top-level keys that have been changed

## set_default(...)
```python
def set_default(option: str | tuple[str], value: Serializable)
```
[`_rsruntime/lib/rs_config.py@24:27`](/_rsruntime/lib/rs_config.py#L24)  
> Sets an option if it does not exist

## setitem(...)
```python
def setitem(key: Key, val: Serializable, _tree: MutableMapping | NoneType = None)
```
[`_rsruntime/util/locked_resource.py@88:91`](/_rsruntime/util/locked_resource.py#L88)  
> Sets a key to a value

## sort(...)
```python
def sort(by: Callable = <lambda>)
```
[`_rsruntime/util/fbd.py@277:283`](/_rsruntime/util/fbd.py#L277)  
> Sorts the data of this INIBackedDict in-place, marking all touched sections as dirty

## start_autosync()
```python
def start_autosync()
```
[`_rsruntime/util/locked_resource.py@88:91`](/_rsruntime/util/locked_resource.py#L88)  
> Starts the internal watchdog timer

## stop_autosync()
```python
def stop_autosync()
```
[`_rsruntime/util/locked_resource.py@88:91`](/_rsruntime/util/locked_resource.py#L88)  
> Stops the internal watchdog timer

## sync()
```python
def sync()
```
[`_rsruntime/util/locked_resource.py@88:91`](/_rsruntime/util/locked_resource.py#L88)  
> Convenience method for writeback_dirty and readin_modified

## values(...)
```python
def values(start_key: Key) -> Generator
```
[`_rsruntime/util/locked_resource.py@88:91`](/_rsruntime/util/locked_resource.py#L88)  
> Iterates over every value

## writeback(...)
```python
def writeback(topkey: str, only_if_dirty: bool = True, clean: bool = True)
```
[`_rsruntime/util/locked_resource.py@88:91`](/_rsruntime/util/locked_resource.py#L88)  
> Writes back a top-level key

## writeback_dirty()
```python
def writeback_dirty()
```
[`_rsruntime/util/locked_resource.py@88:91`](/_rsruntime/util/locked_resource.py#L88)  
> <no doc>
**[Standalone: parts/RunServer/Config.md](./parts/RunServer/Config.md)**


# `ExceptionHandlers` (`RunServer.ExceptionHandlers` | `RS.EH`)
[`_rsruntime/lib/rs_exceptionhandlers.py`](/_rsruntime/lib/rs_exceptionhandlers.py "Source")  
[Standalone doc: parts/RunServer/ExceptionHandlers.md](./parts/RunServer/ExceptionHandlers.md)  

## hookin()
```python
def hookin()
```
[`_rsruntime/lib/rs_exceptionhandlers.py@38:41`](/_rsruntime/lib/rs_exceptionhandlers.py#L38)  
> <no doc>

## hookout()
```python
def hookout()
```
[`_rsruntime/lib/rs_exceptionhandlers.py@46:49`](/_rsruntime/lib/rs_exceptionhandlers.py#L46)  
> <no doc>

## register_exception_hook(...)
```python
def register_exception_hook(callback: Callable)
```
[`_rsruntime/lib/rs_exceptionhandlers.py@54:55`](/_rsruntime/lib/rs_exceptionhandlers.py#L54)  
> <no doc>

## register_thread_exception_hook(...)
```python
def register_thread_exception_hook(callback: Callable)
```
[`_rsruntime/lib/rs_exceptionhandlers.py@58:59`](/_rsruntime/lib/rs_exceptionhandlers.py#L58)  
> <no doc>

## register_unraisable_hook(...)
```python
def register_unraisable_hook(callback: Callable)
```
[`_rsruntime/lib/rs_exceptionhandlers.py@56:57`](/_rsruntime/lib/rs_exceptionhandlers.py#L56)  
> <no doc>
**[Standalone: parts/RunServer/ExceptionHandlers.md](./parts/RunServer/ExceptionHandlers.md)**


# `MCLang` (`RunServer.MCLang` | `RS.L`)
[`_rsruntime/lib/rs_lineparser.py`](/_rsruntime/lib/rs_lineparser.py "Source")  
[Standalone doc: parts/RunServer/MCLang.md](./parts/RunServer/MCLang.md)  

## extract_lang()
```python
def extract_lang() -> dict
```
[`_rsruntime/lib/rs_lineparser.py@77:96`](/_rsruntime/lib/rs_lineparser.py#L77)  
> Extracts the language file from a server JAR file, sets and returns self.lang

## lang_to_pattern(...)
```python
def lang_to_pattern(lang: str, group_names: tuple[str, ...] | None = None, prefix_suffix: str = ^{}$) -> Pattern
```
[`_rsruntime/lib/rs_lineparser.py@41:75`](/_rsruntime/lib/rs_lineparser.py#L41)  
> <no doc>

## strip_prefix(...)
```python
def strip_prefix(line: str) -> tuple
```
[`_rsruntime/lib/rs_lineparser.py@35:39`](/_rsruntime/lib/rs_lineparser.py#L35)  
> <no doc>
**[Standalone: parts/RunServer/MCLang.md](./parts/RunServer/MCLang.md)**


# `LineParser` (`RunServer.LineParser` | `RS.LP`)
[`_rsruntime/lib/rs_lineparser.py`](/_rsruntime/lib/rs_lineparser.py "Source")  
[Standalone doc: parts/RunServer/LineParser.md](./parts/RunServer/LineParser.md)  

## handle_line(...)
```python
def handle_line(line: str)
```
[`_rsruntime/lib/rs_lineparser.py@120:125`](/_rsruntime/lib/rs_lineparser.py#L120)  
> <no doc>

## register_callback(...)
```python
def register_callback(patt: Pattern, callback: Callable | Callable, with_prefix: bool = True)
```
[`_rsruntime/lib/rs_lineparser.py@107:113`](/_rsruntime/lib/rs_lineparser.py#L107)  
> Registers a callback
>> If keep_prefix, then lines that have the prefix are passed. callback should have the signature: `callback(match: re.Match, prefix: re.Match, t: time.struct_time)`
>> Otherwise, lines that don't have a prefix are passed; the callback should have the signature: `callback(match: re.Match)`

## register_chat_callback(...)
```python
def register_chat_callback(callback: Callable)
```
[`_rsruntime/lib/rs_lineparser.py@114:119`](/_rsruntime/lib/rs_lineparser.py#L114)  
> Registers a callback for when chat is recieved
>> The callback should have the signature `callback(user: RS.UserManager.User, message: str, insecure: bool)`
**[Standalone: parts/RunServer/LineParser.md](./parts/RunServer/LineParser.md)**


# `PluginManager` (`RunServer.PluginManager` | `RS.PM`)
[`_rsruntime/lib/rs_plugins.py`](/_rsruntime/lib/rs_plugins.py "Source")  
[Standalone doc: parts/RunServer/PluginManager.md](./parts/RunServer/PluginManager.md)  

## early_load_plugins()
```python
def early_load_plugins()
```
[`_rsruntime/lib/rs_plugins.py@171:179`](/_rsruntime/lib/rs_plugins.py#L171)  
> <no doc>

## load_plugins()
```python
def load_plugins()
```
[`_rsruntime/lib/rs_plugins.py@181:183`](/_rsruntime/lib/rs_plugins.py#L181)  
> <no doc>

## restart()
```python
def restart()
```
[`_rsruntime/lib/rs_plugins.py@212:213`](/_rsruntime/lib/rs_plugins.py#L212)  
> <no doc>

## start()
```python
def start()
```
[`_rsruntime/lib/rs_plugins.py@210:211`](/_rsruntime/lib/rs_plugins.py#L210)  
> <no doc>
**[Standalone: parts/RunServer/PluginManager.md](./parts/RunServer/PluginManager.md)**


# `ServerManager` (`RunServer.ServerManager` | `RS.SM`)
[`_rsruntime/lib/rs_servmgr.py`](/_rsruntime/lib/rs_servmgr.py "Source")  
[Standalone doc: parts/RunServer/ServerManager.md](./parts/RunServer/ServerManager.md)  

## preferred_order()
```python
@classmethod
def preferred_order() -> list
```
[`_rsruntime/lib/rs_servmgr.py@199:201`](/_rsruntime/lib/rs_servmgr.py#L199)  
> <no doc>

## register(...)
```python
@classmethod
def register(manager_type: Type)
```
[`_rsruntime/lib/rs_servmgr.py@196:198`](/_rsruntime/lib/rs_servmgr.py#L196)  
> <no doc>
**[Standalone: parts/RunServer/ServerManager.md](./parts/RunServer/ServerManager.md)**


# `UserManager` (`RunServer.UserManager` | `RS.UM`)
[`_rsruntime/lib/rs_usermgr.py`](/_rsruntime/lib/rs_usermgr.py "Source")  
[Standalone doc: parts/RunServer/UserManager.md](./parts/RunServer/UserManager.md)  

## close()
```python
def close()
```
[`_rsruntime/lib/rs_usermgr.py@168:170`](/_rsruntime/lib/rs_usermgr.py#L168)  
> <no doc>
**[Standalone: parts/RunServer/UserManager.md](./parts/RunServer/UserManager.md)**


# `TellRaw` (`RunServer.TellRaw` | `RS.TR`)
[`_rsruntime/lib/rs_userio.py`](/_rsruntime/lib/rs_userio.py "Source")  
[Standalone doc: parts/RunServer/TellRaw.md](./parts/RunServer/TellRaw.md)  
> Generates a TellRaw JSON
>> Praise be to https://www.minecraftjson.com !
> Who doesn't want object-oriented TellRaws???

## append(...)
```python
@staticmethod
def append(self, object)
```
> Append object to the end of the list.

## clear(...)
```python
@staticmethod
def clear(self)
```
> Remove all items from list.

## copy(...)
```python
@staticmethod
def copy(self)
```
> Return a shallow copy of the list.

## count(...)
```python
@staticmethod
def count(self, value)
```
> Return number of occurrences of value.

## extend(...)
```python
@staticmethod
def extend(self, iterable)
```
> Extend list by appending elements from the iterable.

## ijoin(...)
```python
@staticmethod
def ijoin(self, tellraws: tuple) -> Generator
```
[`_rsruntime/lib/rs_userio.py@105:109`](/_rsruntime/lib/rs_userio.py#L105)  
> <no doc>

## index(...)
```python
@staticmethod
def index(...)
```
<details><summary>Parameters...</summary>
```python
    self, value, start=0,
    stop=9223372036854775807
```
</details>
> Return first index of value.
> 
> Raises ValueError if the value is not present.

## insert(...)
```python
@staticmethod
def insert(self, index, object)
```
> Insert object before index.

## itell(...)
```python
@classmethod
def itell(user: User, args, kwargs)
```
[`_rsruntime/lib/rs_userio.py@114:117`](/_rsruntime/lib/rs_userio.py#L114)  
> Convenience method for `user.tell(RS.TR().text(*args, **kwargs))`

## join(...)
```python
@staticmethod
def join(self, tellraws: tuple) -> Self
```
[`_rsruntime/lib/rs_userio.py@110:111`](/_rsruntime/lib/rs_userio.py#L110)  
> <no doc>

## line_break(...)
```python
@staticmethod
def line_break(self, count: int = 1)
```
[`_rsruntime/lib/rs_userio.py@99:103`](/_rsruntime/lib/rs_userio.py#L99)  
> Append n newlines to self (where n >= 0)

## pop(...)
```python
@staticmethod
def pop(self, index=-1)
```
> Remove and return item at index (default last).
> 
> Raises IndexError if list is empty or index is out of range.

## remove(...)
```python
@staticmethod
def remove(self, value)
```
> Remove first occurrence of value.
> 
> Raises ValueError if the value is not present.

## render(...)
```python
@staticmethod
def render(self)
```
[`_rsruntime/lib/rs_userio.py@37:38`](/_rsruntime/lib/rs_userio.py#L37)  
> <no doc>

## reverse(...)
```python
@staticmethod
def reverse(self)
```
> Reverse *IN PLACE*.

## sort(...)
```python
@staticmethod
def sort(self, key=None, reverse=False)
```
> Sort the list in ascending order and return None.
> 
> The sort is in-place (i.e. the list itself is modified) and stable (i.e. the
> order of two equal elements is maintained).
> 
> If a key function is given, apply it once to each list item and sort them,
> ascending or descending, according to their function values.
> 
> The reverse flag can be set to sort in descending order.

## text(...)
```python
@staticmethod
def text(...)
```
<details><summary>Parameters...</summary>
```python
    self, text: str, color: str | None = None,
    fmt: _rsruntime.lib.rs_userio.TextFormat | dict = 0, insertion: str | None = None, type: TextType = TextType.TEXT,
    objective: None | str = None, click_event: _rsruntime.lib.rs_userio.ClickEvent | None = None, click_contents: None | str = None,
    hover_event: _rsruntime.lib.rs_userio.HoverEvent | None = None, hover_contents: NoneType | ForwardRef('TellRaw') | tuple | dict = None
```
</details>
[`_rsruntime/lib/rs_userio.py@43:98`](/_rsruntime/lib/rs_userio.py#L43)  
> Appends a tellraw text to self
>> text is the text to show unless type is:
>>> SELECTOR, in which case text is the selector type
>>> SCORE, in which case text is the name of the player
>>> KEYBIND, in which case text is the ID of the keybind
>> fmt is the formatting to apply to the text
>> insertion is text that is entered into the user's chat-box when the text is shift-clicked
>> type should be self-explanatory
>> objective is None unless type is SCORE, in which case objective is the scoreboard objective
>> click_event is either a ClickEvent or None for nothing
>>> click_contents is the text to use for the click_event (the URL to open, text to copy, etc.)
>> hover_event is either a HoverEvent or None for nothing
>>> hover_contents is the data to use for the hover_event (the entity to display, the TellRaw to show [as text])
**[Standalone: parts/RunServer/TellRaw.md](./parts/RunServer/TellRaw.md)**


# `ChatCommands` (`RunServer.ChatCommands` | `RS.CC`)
[`_rsruntime/lib/rs_userio.py`](/_rsruntime/lib/rs_userio.py "Source")  
[Standalone doc: parts/RunServer/ChatCommands.md](./parts/RunServer/ChatCommands.md)  

## compose_command(...)
```python
def compose_command(cmd: str, args: str | None) -> str
```
[`_rsruntime/lib/rs_userio.py@325:330`](/_rsruntime/lib/rs_userio.py#L325)  
> Compiles cmd and args together using various configuration to compose a command string

## help(...)
```python
def help(...)
```
<details><summary>Parameters...</summary>
```python
    user: User, on: str | Literal | NoneType = None, section: None | str = None,
    force_console: bool | None = None
```
</details>
[`_rsruntime/lib/rs_userio.py@392:458`](/_rsruntime/lib/rs_userio.py#L392)  
> Shows help on commands or sections.
>> If on is "section", then shows help on the section specified by "section"
>> If on is a command, then shows help on that command
>> If on is not supplied, then shows a list of top-level sections

## helpcmd_for(...)
```python
def helpcmd_for(item: str | None = None, for_section: bool = False)
```
[`_rsruntime/lib/rs_userio.py@465:472`](/_rsruntime/lib/rs_userio.py#L465)  
> Composes a help command for the item

## parse_command(...)
```python
def parse_command(line: str) -> tuple
```
[`_rsruntime/lib/rs_userio.py@331:341`](/_rsruntime/lib/rs_userio.py#L331)  
> Returns:
>> - a (True, ChatCommand, args) tuple if the line is a ChatCommand
>> - a (False, command, args) tuple if the line matches as a ChatCommand, but the command in question hasn't been registered
>> - None if the line doesn't match as a ChatCommand

## register(...)
```python
def register(cmd: ChatCommands.ChatCommand, aliases: set = set()) -> ChatCommands.ChatCommand
```
[`_rsruntime/lib/rs_userio.py@364:382`](/_rsruntime/lib/rs_userio.py#L364)  
> <no doc>

## register_func(...)
```python
def register_func(...) -> ChatCommands.ChatCommand
```
<details><summary>Parameters...</summary>
```python
    func: Callable, aliases: set = set(), permission: Perm = 80,
    help_section: str | tuple[str, ...] = ()
```
</details>
[`_rsruntime/lib/rs_userio.py@360:363`](/_rsruntime/lib/rs_userio.py#L360)  
> <no doc>

## run_command(...)
```python
def run_command(user: User, line: str, not_secure: bool = False)
```
[`_rsruntime/lib/rs_userio.py@342:358`](/_rsruntime/lib/rs_userio.py#L342)  
> <no doc>
**[Standalone: parts/RunServer/ChatCommands.md](./parts/RunServer/ChatCommands.md)**


# `Convenience` (`RunServer.Convenience` | `RS._`)

[Standalone doc: parts/RunServer/Convenience.md](./parts/RunServer/Convenience.md)  



# `command` (`RunServer.Convenience.command` | `RS._.command`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/command.md](./parts/RunServer/Convenience/command.md)  
> Writes a command to the server
>> Equivelant to RS.SM.write(line)
**[Standalone: parts/RunServer/Convenience/command.md](./parts/RunServer/Convenience/command.md)**



# `inject_line` (`RunServer.Convenience.inject_line` | `RS._.inject_line`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/inject_line.md](./parts/RunServer/Convenience/inject_line.md)  
> Injects a line into LineParser, as if it was read from the ServerManager
>> Equivelant to RS.LP.handle_line(line)
**[Standalone: parts/RunServer/Convenience/inject_line.md](./parts/RunServer/Convenience/inject_line.md)**



# `listen_chat` (`RunServer.Convenience.listen_chat` | `RS._.listen_chat`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/listen_chat.md](./parts/RunServer/Convenience/listen_chat.md)  
> Registers a callback for when LineParser reads a chat message
>> The callback should have three arguments:
>> - the user (RS.UM.User object)
>> - the line (str)
>> - if the message was "not secure" (bool)
**[Standalone: parts/RunServer/Convenience/listen_chat.md](./parts/RunServer/Convenience/listen_chat.md)**



# `say` (`RunServer.Convenience.say` | `RS._.say`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/say.md](./parts/RunServer/Convenience/say.md)  
**[Standalone: parts/RunServer/Convenience/say.md](./parts/RunServer/Convenience/say.md)**



# `tell` (`RunServer.Convenience.tell` | `RS._.tell`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/tell.md](./parts/RunServer/Convenience/tell.md)  
**[Standalone: parts/RunServer/Convenience/tell.md](./parts/RunServer/Convenience/tell.md)**



# `tellraw` (`RunServer.Convenience.tellraw` | `RS._.tellraw`)
[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/tellraw.md](./parts/RunServer/Convenience/tellraw.md)  
> Tells a user something. See RS.TR.text for more advanced usage
>> This function uses RS.TR.itell

### tell(...)
```python
@staticmethod
def tell(self, text: ForwardRef('TellRaw') | tuple | str)
```
[`_rsruntime/lib/rs_usermgr.py@96:101`](/_rsruntime/lib/rs_usermgr.py#L96)  
> <no doc>
**[Standalone: parts/RunServer/Convenience/tellraw.md](./parts/RunServer/Convenience/tellraw.md)**
**[Standalone: parts/RunServer/Convenience.md](./parts/RunServer/Convenience.md)**
