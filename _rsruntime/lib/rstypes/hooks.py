#!/bin/python3

#> Imports
import re
import typing
#</Imports

#> Header >/
HookType = typing.TypeVar('HookType', bound='GenericHook')
FuncType = typing.TypeVar('FuncType', bound='GenericHook')
class GenericHook(dict, typing.Generic[HookType, FuncType]):
    __slots__ = ()

    def __init__(self): super().__init__()
    def register(self, hook: HookType, callback: FuncType):
        if hook not in self: self[hook] = set()
        self[hook].add(callback)
    def unregister(self, hook: HookType, callback: FuncType):
        if hook not in self: return
        self[hook].remove(callback)
    def unregister_hook(self, hook: HookType):
        if hook not in self: return
        del self[hook]
    def __call__(self, hook: HookType, *args, **kwargs):
        if hook not in self: return
        for h in self[hook]: h(*args, **kwargs)

class Hooks(GenericHook[typing.Hashable, typing.Callable]): __slots__ = ()
class ReHooks(GenericHook[re.Pattern, typing.Callable[[re.Match], ...]]):
    __slots__ = ()

    def __call__(self, line: str, *args, **kwargs):
        for p in self:
            if m := p.match(line):
                super().__call__(p, m, *args, **kwargs)
Hooks.ReHooks = ReHooks
class SubHooks(GenericHook[typing.Hashable, typing.Callable]):
    __slots__ = ('hooks',)

    def __init__(self, cls=Hooks):
        self.hooks = cls
    def register(self, hook: HookType, subhook: HookType, callback: FuncType):
        if hook not in self: self[hook] = self.hooks()
        self.hooks.register(subhook, callback)
    def unregister(self, hook: HookType, subhook: HookType, callback: FuncType):
        if hook not in self: return
        self.hooks.unregister(subhook, callback)
    def unregister_subhook(self, hook: HookType, subhook: HookType):
        if hook not in self: return
        self.hooks.unregister_ull(subhook)
    def unregister_hook(self, hook: HookType):
        if hook not in self: return
        del self[hook]
    def __call__(self, hook: HookType, subhook: HookType, *args, **kwargs):
        if hook not in self: return
        self[hook](subhook, *args, **kwargs)
Hooks.SubHooks = SubHooks
