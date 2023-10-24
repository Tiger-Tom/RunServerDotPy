#!/bin/python3

#> Imports
#</Imports

#> Header >/

class Hooks(dict):
    ...
class ReHooks(Hooks):
    ...
class SubHooks(Hooks):
    ...

Hooks.ReHooks = ReHooks
Hooks.SubHooks = SubHooks
