#!/bin/python3

# Sources configuration from files and arguments #

# hack
import sys
sys.path.append('..')
import RunServer
RunServer.setup_logger()

#> Imports
import typing
# File
from pathlib import Path
import logging
# Parsing
import re
import json
#import argparse
# System
import threading
# general_helpers.py
from _rslib import general_helpers as helpers
#</Imports

#> Header >/
class Args:
    __slots__ = ()
class Config:
    '''
        Manages configuration.
        Where configuration keys are required, either a slash-delimited string or tuple of strings is given.
        Configuration is stored in _rsconfig/, the "top-level" key (first place in the key, such as 'toplevel/secondlevel' or ('toplevel', 'secondlevel') is used for the filename, in this case 'toplevel.json'
    '''
    __slots__ = ('rs', 'logger', 'fbd')

    def __init__(self, rs: 'RunServer'):
        self.rs = rs
        self.logger = self.rs.logger.getChild('Config')
        self.fbd = helpers.FileBackedDict(Path('./_rsconfig/'))
        self.logger.debug(f'Initialized: {self}')

    def setitem(self, key: str | tuple[str], val):
        '''
            Sets the config key to the given value
        '''
        self.fbd[key] = val
    def get(self, key: str | tuple[str], default = None):
        '''
            Gets a config value. If the value doesn't already exist, default is returned
        '''
        if key not in self.fbd: return default
        return self.fbd[key]
    def get_set_default(self, key: str | tuple[str], default = None):
        '''
            Gets a config value. If the value doesn't already exist, default is set and then returned
        '''
        if key not in self.fbd:
            self.fbd[key] = default
            return default
        return self.fbd[key]
    def delete(self, key: str | tuple[str], *, allow_top_level_delete: bool = False, allow_subkey_delete: bool = False):
        '''
            Deletes the config key
        '''
        self.fbd.delete(key, allow_top_level_delete=allow_top_level_delete, allow_subkey_delete=allow_subkey_delete)            
    
    _on_missing_behavior = {
        'set_default': get_set_default,
        'get_default': get,
        'error': None,
    }
    def __call__(self, key: str | tuple[str], default = None, on_missing: typing.Literal[*_on_missing_behavior.keys()] = 'set_default'):
        '''
            By default, or when on_missing is "set_default", this function acts like get_set_default
            If on_missing is "get_default", this function acts like get
            If on_missing is "error", then a KeyError error is thrown if the value isn't set
        '''
        assert on_missing in _on_missing_behavior
        if (f := self._on_missing_behavior[on_missing]) is not None:
            if key not in self.return f(self, key, default)
        else: raise KeyError(key)
    def __getitem__(self, key: str | tuple[str]):
        return self.fbd[key]
    __setitem__ = set
    __delitem__ = setitem
