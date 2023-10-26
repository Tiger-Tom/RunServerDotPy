#!/bin/python3

#> Imports
import re
import typing
#</Imports

#> Header >/
class GenericHook[HookType, FuncType]:
    __slots__ = ('hooks',)

    def __init__(self):
        self.hooks = {}
        super().__init__()
    def register(self, hook: HookType, callback: FuncType):
        if hook not in self.hooks: self.hooks[hook] = set()
        self.hooks[hook].add(callback)
    def unregister(self, hook: HookType, callback: FuncType):
        if hook not in self.hooks: return
        self.hooks[hook].remove(callback)
    def unregister_hook(self, hook: HookType):
        if hook not in self.hooks: return
        del self.hooks[hook]
    def __call__(self, hook: HookType, *args, **kwargs):
        if hook not in self.hooks: return
        for h in self.hooks[hook]: h(*args, **kwargs)

class Hooks(GenericHook[typing.Hashable, typing.Callable]): __slots__ = ()
Hooks.GenericHook = GenericHook
class FuncHooks[FuncTakes, FuncReturns](GenericHook[typing.Callable[[FuncTakes], FuncReturns], typing.Callable[[FuncReturns], ...]]):
    __slots__ = ()

    def __call__(self, inp: FuncTakes, *args, **kwargs):
        for f in self.hooks:
            if m := f(inp):
                super().__call__(f, m, *args, **kwargs)
Hooks.FuncHooks = FuncHooks
class ReHooks(GenericHook[re.Pattern, typing.Callable[[re.Match], ...]]):
    __slots__ = ('type',)

    def __init__(self, type: typing.Literal['search', 'match', 'fullmatch'] = 'search', *, no_check: bool = False):
        super().__init__()
        if not no_check: assert hasattr(re.Pattern, type)
        self.type = type
    def __call__(self, line: str, *args, **kwargs):
        for p in self.hooks:
            if m := getattr(p, self.type)(line):
                super().__call__(p, m, *args, **kwargs)
Hooks.ReHooks = ReHooks
class SubHooks[HookType, SubHookType, FuncType](GenericHook[SubHookType, FuncType]):
    __slots__ = ('hook',)

    def __init__(self, cls=Hooks):
        super().__init__()
        self.hook = cls
    def register(self, hook: HookType, subhook: SubHookType, callback: FuncType):
        if hook not in self.hooks: self.hooks[hook] = self.hook()
        self.hooks[hook].register(subhook, callback)
    def unregister(self, hook: HookType, subhook: SubHookType, callback: FuncType):
        if hook not in self.hooks: return
        self.hooks[hook].unregister(subhook, callback)
    def unregister_subhook(self, hook: HookType, subhook: SubHookType):
        if hook not in self.hooks: return
        self.hooks[hook].unregister_hook(subhook)
    def unregister_hook(self, hook: HookType):
        if hook not in self.hooks: return
        del self.hooks[hook]
    def __call__(self, hook: HookType, subhook: HookType, *args, **kwargs):
        if hook not in self.hooks: return
        self.hooks[hook](subhook, *args, **kwargs)
Hooks.SubHooks = SubHooks
