#!/bin/python3

#> Imports
import typing
from functools import wraps
#</Imports

#> Header >/
_cache_arg_missing = object()
def custom_method_cache(func: typing.Callable | None = None, *,
                        capture_attrs: tuple[str] = (), capture_args: tuple[int] = (), capture_kwargs: tuple[str] = ()):
    cache = {}
    def decorator(func: typing.Callable):
        @wraps(func)
        def wrapper(cls_or_self, *args, **kwargs):
            hsh = hash((tuple((attr, getattr(cls_or_self, attr, _cache_arg_missing)) for attr in capture_attrs),
                        tuple((arg, args[arg] if (arg < len(args)) else _cache_arg_missing) for arg in capture_args),
                        tuple((kwarg, kwargs.get(arg, _cache_arg_missing)) for kwarg in capture_kwargs)))
            if hsh not in cache:
                cache[hsh] = func(cls_or_self, *args, **kwargs)
            return cache[hsh]
        wrapper.__wcache__ = cache
        return wrapper
    decorator.__dcache__ = cache
    if func is not None:
        return decorator(func)
    return decorator
