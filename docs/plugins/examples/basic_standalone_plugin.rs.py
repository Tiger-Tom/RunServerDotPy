#!/bin/python

'''
    Loaded by itself by PluginManager.load_plugins()
        must have the extension .rs.py
        cannot have any early-load components
        does not get the benefit of a manifest
'''

#> Imports
import RS
#</Imports

#> Main >/
print(f'I\'m all alone, {RS}!')

def __start__(self):
    print(f'{self} is alone')
