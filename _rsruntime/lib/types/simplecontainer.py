#!/bin/python3

#> Imports
#</Imports

#> Header >/
def SimpleContainer(*names):
    class SimpleContainer:
        __slots__ = names
    return SimpleContainer
