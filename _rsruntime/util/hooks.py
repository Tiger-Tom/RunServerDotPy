#!/bin/python3

#> Imports
import re
import typing
#</Imports

#> Header >/
__all__ = ('GenericHooks', 'Hooks', 'SingleHook', 'FuncHooks', 'ReHooks', 'SubHooks')

class GenericHooks[HookType, FuncType]:
    '''
        A generic hooks class
        Allows callback functions (of type FuncType) to be registered with a "key" of HookType
        Can be called with the key to call all functions registered with it, passing *args and **kwargs
    '''
    __slots__ = ('hooks',)

    def __init__(self):
        self.hooks = {}
        super().__init__()
    def register(self, hook: HookType, callback: FuncType):
        '''Adds a callback to be called by __call__(hook)'''
        if hook not in self.hooks: self.hooks[hook] = set()
        self.hooks[hook].add(callback)
    def unregister(self, hook: HookType, callback: FuncType):
        '''Removes a callback that would be called by __call__(hook) (if it exists)'''
        if hook not in self.hooks: return
        self.hooks[hook].remove(callback)
    def unregister_hook(self, hook: HookType):
        '''Deletes all callbacks that would be called by __call__(hook)'''
        if hook not in self.hooks: return
        del self.hooks[hook]
    def __call__(self, hook: HookType, *args, **kwargs):
        '''Calls all callbacks that have been registered to be called by __call__(hook)'''
        if hook not in self.hooks: return
        for h in self.hooks[hook]: h(*args, **kwargs)
class Hooks(GenericHooks[typing.Hashable, typing.Callable]):
    '''
        The most caustic generic hooks class
            Has no difference in behavior from GenericHooks other than typehinting
                basically syntactic sugar for dict[typing.Hashable, typing.Callable]
        Also serves as a container for the other types of hooks
    '''
    __slots__ = ()
Hooks.GenericHooks = GenericHooks
class SingleHook(GenericHooks[None, typing.Callable]):
    '''A hooks class that has no key'''
    __slots__ = ()

    def __init__(self):
        self.hooks = set()
    def register(self, callback: typing.Callable):
        '''Adds a callback to be called by __call__()'''
        self.hooks.add(callback)
    def unregister(self, callback: typing.Callable):
        '''Removes a callback that would be called by __call__() (if it exists)'''
        self.hooks.remove(callback)
    unregister_hook = NotImplemented
    def __call__(self, *args, **kwargs):
        '''Calls all callbacks that have been registered to be called by __call__()'''
        for c in self.hooks: c(*args, **kwargs)
Hooks.SingleHook = SingleHook
class FuncHooks[FuncTakes, FuncReturns](GenericHooks[typing.Callable[[FuncTakes], FuncReturns], typing.Callable[[FuncReturns], ...]]):
    '''
        A hooks class that uses functions that take FuncTakes and return FuncReturns as keys
        When called with a FuncTakes, each hook is called with the FuncTakes
            If a hook returns a falsey FuncReturns value, then nothing happens
            If a hook returns a truthy FuncReturns value, then each callback registered under that function is called with the FuncReturns value
    '''
    __slots__ = ()

    def __call__(self, inp: FuncTakes, *args, **kwargs):
        '''Calls all keys and passes any truthy responses to all callbacks that have been registered to be called by a __call__(...) matching the inp(ut)'''
        for f in self.hooks:
            if m := f(inp):
                super().__call__(f, m, *args, **kwargs)
Hooks.FuncHooks = FuncHooks
class ReHooks(GenericHooks[re.Pattern, typing.Callable[[re.Match], ...]]):
    '''
        A hooks class that matches patterns as keys
        When called with a string, all keys are [search|match|fullmatch]ed (decided upon init) against the string
            'search' (the default): calls each callback with the re.Match of the first place where the pattern produces a match
            'match': calls each callback with the re.Match of the beginning of the string that matches the pattern
            'fullmatch': calls each callback with the re.Match of the entire string if it matches the pattern
    '''
    __slots__ = ('type',)

    def __init__(self, type: typing.Literal['search', 'match', 'fullmatch'] = 'search', *, no_check: bool = False):
        super().__init__()
        if not no_check: assert hasattr(re.Pattern, type)
        self.type = type
    def __call__(self, line: str, *args, **kwargs):
        '''Runs a [search|match|fullmatch]es with each key on line, passing re.Match(es) to all callbacks that have been registered to be called by a __call__(...) matching the line'''
        for p in self.hooks:
            if m := getattr(p, self.type)(line):
                super().__call__(p, m, *args, **kwargs)
Hooks.ReHooks = ReHooks
class SubHooks[HookType, SubHookType, FuncType](GenericHooks[SubHookType, FuncType]):
    '''
        A hooks class that has two keys instead of one
        Basically syntactic sugar for either of:
        - GenericHooks[HookType, GenericHooks[SubHookType, FuncType]]
        - dict[HookType, GenericHooks[SubHookType, FuncType]]
    '''
    __slots__ = ('hook',)

    def __init__(self, cls=Hooks):
        super().__init__()
        self.hook = cls
    def register(self, hook: HookType, subhook: SubHookType, callback: FuncType):
        '''Adds a callback to be called by __call__(hook, subhook)'''
        if hook not in self.hooks: self.hooks[hook] = self.hook()
        self.hooks[hook].register(subhook, callback)
    def unregister(self, hook: HookType, subhook: SubHookType, callback: FuncType):
        '''Removes a callback that would be called by __call__(hook, subhook)'''
        if hook not in self.hooks: return
        self.hooks[hook].unregister(subhook, callback)
    def unregister_subhook(self, hook: HookType, subhook: SubHookType):
        '''Removes all callbacks that would be called by __call__(hook, subhook)'''
        if hook not in self.hooks: return
        self.hooks[hook].unregister_hook(subhook)
    def unregister_hook(self, hook: HookType):
        '''Removes all callbacks that would be called by __call__(hook, ...) (with ... being anything)'''
        if hook not in self.hooks: return
        del self.hooks[hook]
    def __call__(self, hook: HookType, subhook: SubHookType, *args, **kwargs):
        '''Calls all hooks thet have been registered to be called by __call__(hook, subhook)'''
        if hook not in self.hooks: return
        self.hooks[hook](subhook, *args, **kwargs)
Hooks.SubHooks = SubHooks
