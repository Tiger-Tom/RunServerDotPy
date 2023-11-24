#!/bin/python3

#> Imports
from pathlib import Path
# Parsing
import re
from ast import literal_eval
# Types
import typing
from typing import MutableMapping
from enum import Enum, IntEnum
# Abstract
from abc import ABC, abstractmethod, abstractproperty
# Local types
from locked_resource import LockedResource, locked
from timer import Timer
#</Imports

#> Header >/
__all__ = ('JSONBackedDict', 'INIBackedDict')

# ABC
class FileBackedDict[Serializable, Serialized, Deserializable](ABC, LockedResource):
    '''
        A dictionary-like class that is backed by an on-disk file
        Asynchronously synchronizes entries with a file on disk
        Subfields are accessed with `key_sep` (default: "/")
    '''
    __slots__ = ('path', '_data', 'watchdog', 'mtimes', 'dirty')

    key_sep = '/'
    key_topp_patt = re.compile(r'^[a-zA-Z\d][\w\d\-]*')
    key_part_patt = re.compile(r'^[a-zA-Z][\w\d\- ;]*$')

    Behavior = Enum('Behavior', ('DEFAULT', 'IGNORE', 'RAISE', 'FORCE'))
    Behavior.__doc__ = \
        '''
            Various behavior modifiers for different methods
                Most functions only specify a subset of accepted Behaviors, see annotations for typing.Literal[]s containing Behaviors
        '''

    @abstractproperty
    def file_suffix() -> str: NotImplemented
    
    _transaction_types = IntEnum('TransactionTypes', ('GETITEM', 'SETITEM'))
    def _validate_transaction(self, key: tuple[str], ttype: _transaction_types, args: tuple[typing.Any] = (), *, _tree: MutableMapping | None = None) -> None:
        '''Allows subclasses to place extra restrictions on types of transactions by throwing exceptions to cancel them. Is a no-op by default'''

    # Concrete methods #
    def __init__(self, path: Path, intvl: float = 120.0):
        LockedResource.__init__(self)
        self.path = path
        self.watchdog = Timer.set_interval(self.sync, intvl, False)
        self.mtimes = {}; self.dirty = set()

    # Key functions
    Key = str | tuple[str]
    @classmethod
    def key(cls, key: Key, top_level: bool = False, /): # key key key
        '''Transform a string / tuple of strings into a key'''
        if isinstance(key, str): key = key.split(cls.key_sep)
        if not key: raise ValueError('Empty key')
        if any(cls.key_sep in part for part in key):
            raise ValueError(f'Part of {key} contains a "{cls.key_sep}"')
        elif (not top_level) and (len(key) == 1):
            raise ValueError('Top-level key disallowed')
        elif not cls.key_topp_patt.fullmatch(key[0]):
            raise ValueError(f'Top-level part of key {key} does not match pattern {cls.key_topp_patt.pattern}')
        elif not all(map(cls.key_part_patt.fullmatch, key[1:])):
            raise ValueError(f'Part of sub-key {key[1:]} (full: {key}) not match pattern {cls.key_part_patt.pattern}')
        return key
    def path_from_topkey(self, topkey: str):
        '''Returns the Path corresponding to the top-key's file'''
        return (self.path / topkey).with_suffix(self.file_suffix)
    # Syncing functions
    @locked
    def sync(self):
        '''Convenience method for writeback_dirty and readin_changed'''
        self.writeback_dirty()
        self.readin_changed()
    ## Write-back
    @locked
    def writeback_dirty(self):
        while self.dirty:
            self.writeback(self.dirty.pop(), only_if_dirty=False, clean=False)
    @locked
    def writeback(self, topkey: str, *, only_if_dirty: bool = True, clean: bool = True):
        '''Writes back a top-level key'''
        if topkey in self.dirty:
            if clean: self.dirty.remove(topkey)
        elif only_if_dirty: return
        self.path_from_topkey(topkey).write_text(self._to_string(topkey))
    @abstractmethod
    def _to_string(self, topkey: str): NotImplemented
    ## Read-in
    @locked
    def readin_modified(self):
        '''Reads in top-level keys that have been changed'''
        raise NotImplementedError
    @locked
    def readin(self, topkey: str):
        '''Reads in a top-level key'''
        self._from_string(topkey, self.path_from_topkey(topkey).read_text())
    @abstractmethod
    def _from_string(self, topkey: str, value: str): NotImplemented

    # High-level item manipulation
    def bettergetter(self, key: Key, default: typing.Literal[Behavior.RAISE] | typing.Any = Behavior.RAISE, set_default: bool = True) -> Deserializable | typing.Any:
        '''
            Gets the value of key
                If the key is missing, then:
                    if default is Behavior.RAISE: raises KeyError
                    otherwise: returns default, and if set_default is truthy then sets the key to default
        '''
        key = self.key(key)
        _tree = self._gettree(key, make_if_missing=(default is not self.Behavior.RAISE) and set_default, fetch_if_missing=True, no_raise_keyerror=(default is not self.Behavior.RAISE))
        self._validate_transaction(key, self._transaction_types.GETITEM, _tree=_tree)
        if _tree is None: return default
        if key[-1] in _tree: return self._deserialize(_tree[key[-1]])
        if set_default: self.setitem(key, default, _tree=_tree)
        return default
    __call__ = bettergetter
    
    # Med-level item manipulation
    ## Getting
    @locked
    def get(self, key: Key, default: typing.Literal[Behavior.RAISE] | Serializable = Behavior.RAISE, converter: typing.Callable[str, Deserializable] = literal_eval, *, _tree: MutableMapping | None = None) -> Deserializable:
        '''
            Gets the value of key
                If the key is missing, then raises KeyError if default is Behavior.RAISE, otherwise returns default
        '''
        key = self.key(key) if (_tree is None) else key
        sect = _tree if (_tree is not None) else \
               self._gettree(key, make_if_missing=False, fetch_if_missing=True, no_raise_keyerror=(default is not self.Behavior.RAISE))
        self._validate_transaction(key, self._transaction_types.GETITEM, _tree=sect)
        if sect is None: return default
        if key[-1] not in sect:
            raise KeyError(f'{key}[-1]')
        val = sect[key[-1]]
        return converter(sect[key[-1]])
    __getitem__ = getitem = get
    ## Setting
    @locked
    def setitem(self, key: Key, val: Serializable, *, _tree: MutableMapping | None = None):
        '''Sets a key to a value'''
        key = self.key(key) if (_tree is None) else key
        sect = (self._gettree(key, make_if_missing=True, fetch_if_missing=True) if (_tree is None) else _tree)
        self._validate_transaction(key, self._transaction_types.GETITEM, (val,), _tree=sect)
        sect[key[-1]] = self._serialize(val)
        self.dirty.add(key[0])
    __setitem__ = setitem
    ## Containing
    @locked
    def contains(self, key: Key, *, _tree: MutableMapping | None) -> bool:
        '''Returns whether or not the key exists'''
        key = self.key(key) if (_tree is None) else key
        sect = self._gettree(key, make_if_missing=False, fetch_if_missing=True, no_raise_keyerror=True) if (_tree is None) else _tree
        if (sect is None) or (key[-1] not in sect): return False
        return True
    __contains__ = contains
    
    # Low-level functions
    @abstractmethod
    def _init_topkey(self, topkey: str): NotImplemented
    def _gettop(self, topkey: str, *, make_if_missing: bool, fetch_if_missing: bool = True, no_raise_keyerror: bool = False) -> MutableMapping | None:
        '''Gets the mapping of the toppkey'''
        if topkey not in self._data:
            if fetch_if_missing and self.path_from_topkey(topkey).exists():
                self.readin(topkey)
            elif make_if_missing: self._init_topkey(topkey)
            elif no_raise_keyerror: return None
            else: raise KeyError(topkey)
        return self._data[topkey]
    @abstractmethod
    def _gettree(self, key: tuple[str], *, make_if_missing: bool, fetch_if_missing: bool = True, no_raise_keyerror: bool = False) -> MutableMapping | None: NotImplemented
    @abstractmethod
    def _serialize(self, val: Serializable) -> Serialized: NotImplemented
    def _deserialize(self, value: Serialized) -> Deserializable: NotImplemented
