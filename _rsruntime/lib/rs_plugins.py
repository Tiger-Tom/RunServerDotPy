#!/bin/python3

#> Imports
#</Imports

# RunServer Module
import RS

#> Header >/
class PluginManager:
    __slots__ = ('logger', 'plugins')

    class Plugin:
        ...
    
    def __init__(self):
        self.logger = RS.logger.getChild('PM')
    def early_load_plugins(self):
        ...
    def load_plugins(self):
        ...
    def start(self):
        ...
