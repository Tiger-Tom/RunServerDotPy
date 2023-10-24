#!/bin/python3

#> Imports
#</Imports

#> Header >/
def SimpleContainer(*names):
    class SimpleContainer:
        __slots__ = names
        def __init__(self, **vals):
            for k,v in vals.items():
                setattr(self, k, v)
    return SimpleContainer
