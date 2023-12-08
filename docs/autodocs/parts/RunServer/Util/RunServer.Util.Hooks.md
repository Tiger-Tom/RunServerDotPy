[`_rsruntime/util/hooks.py`](/_rsruntime/util/hooks.py "Source")  
[Standalone doc: parts/RunServer/Util/RunServer.Util.Hooks.md](RunServer.Util.Hooks.md)  
> The most caustic generic hooks class
>> Has no difference in behavior from GenericHooks other than typehinting
>>> basically syntactic sugar for dict[typing.Hashable, typing.Callable]
> Also serves as a container for the other types of hooks

## register(...)
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

## unregister(...)
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

## unregister_hook(...)
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