#!/bin/python3

#> Imports
from configparser import ConfigParser, SectionProxy
from pathlib import Path
import re
import functools
import typing
from ast import literal_eval
from enum import Enum
from .timer import Timer
from .locked_resource import basic
#</Imports

#> Header >/
__all__ = ('FileBackedDict',)

class FileBackedDict(basic.LockedResource):
    '''
        A dictionary backed by an on-disk INI file
        Asynchronously synchronizes entries with a file on disk when enabled
            Detects file changes by checking modification times
            Detects local changes by adding mutated keys to a "dirty" set
        Sub-fields are accessed with `key_sep` (default: "/")
    '''
    __slots__ = ('path', 'c', 'watchdog', 'mtimes', 'dirty')

    key_sep = '/'
    key_topp_patt = re.compile(r'^[a-zA-Z\d][\w\d\-]*')
    key_part_patt = re.compile(r'^[a-zA-Z][\w\d\- ;]*$')
    file_suffix = '.ini'

    serializable = (type(...), type(None), # simple literals
        bool, int, float, complex,         # numeric literals
        str, bytes, list, frozenset)       # collection literals
    serializable_convert = { # types that need conversion to be immutable
        list: tuple,
        set: frozenset,
    }
    Serializable = typing.Union[*serializable, *serializable_convert]
    Deserializable = typing.Union[*serializable]
    
    def __init__(self, path: Path, intvl: float = 120.0):
        super().__init__()
        self.path = Path(path)
        self.c = {}
        self.watchdog = Timer.set_interval(self.sync, intvl, False)
        self.mtimes = {}; self.dirty = set()
    optionxform = staticmethod(lambda o: str(o))
    @basic.locked
    def _init_topkey(self, topkey: str) -> ConfigParser:
        self.c[topkey] = ConfigParser()
        self.c[topkey].optionxform = self.optionxform
        return self.c[topkey]

    Behavior = Enum('Behavior', ('DEFAULT', 'IGNORE', 'RAISE', 'FORCE'))
    Behavior.__doc__ = \
        '''
            Various behaviors for error/"warning" handlers.
                Most functions only specify a subset of accepted Behaviors, see annotations for typing.Literal[]s containing Behaviors
        '''

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
    def tkey_path(self, topkey: str):
        '''Returns the Path corresponding to the topkey's INI file'''
        return (self.path / topkey).with_suffix(self.file_suffix)

    # Syncing methods
    @basic.locked
    def sync(self):
        '''Convenience method for readin_changed and writeback_dirty'''
        writeback_dirty()
        readin_modified()
    ## Read-in
    @basic.locked
    def readin_modified(self):
        '''Reads in top-level keys that have been changed'''
        raise NotImplementedError
    @basic.locked
    def readin(self, topkey: str):
        '''Reads in a top-level key'''
        self._init_topkey(topkey).read_string(self.tkey_path(topkey).read_text())
    ## Write-back
    @basic.locked
    def writeback_dirty(self):
        '''Writes back all top-level keys marked as dirty'''
        while self.dirty:
            self.writeback(self.dirty.pop(), False, False)
    @basic.locked
    def writeback(self, topkey: str, only_if_dirty: bool = True, clean: bool = True):
        '''Writes back a top-level key'''
        if topkey in self.dirty:
            if clean: self.dirty.remove(topkey)
        elif only_if_dirty: return
        with self.tkey_path(topkey).open('w') as f:
            self.c[topkey].write(f)

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
        if _tree is None: return default
        if key[-1] in _tree: return literal_eval(_tree[key[-1]])
        if set_default: self.setitem(key, default, _tree=_tree)
        return default
    __call__ = bettergetter
    
    # Med-level item manipulation
    ## Getting
    @basic.locked
    def get(self, key: Key, default: typing.Literal[Behavior.RAISE] | Serializable = Behavior.RAISE, converter: typing.Callable[str, Deserializable] = literal_eval, *, _tree: SectionProxy | None = None) -> Deserializable:
        '''
            Gets the value of key
                If the key is missing, then raises KeyError if default is Behavior.RAISE, otherwise returns default
        '''
        key = self.key(key) if (_tree is None) else key
        sect = _tree if (_tree is not None) else \
               self._gettree(key, make_if_missing=False, fetch_if_missing=True, no_raise_keyerror=(default is not self.Behavior.RAISE))
        if sect is None: return default
        if key[-1] not in sect:
            raise KeyError(f'{key}[-1]')
        val = sect[key[-1]]
        return converter(sect[key[-1]])
    __getitem__ = getitem = get
    ## Setting
    @basic.locked
    def setitem(self, key: Key, val: Serializable,
                type_convert: typing.Literal[Behavior.DEFAULT, Behavior.IGNORE] = Behavior.DEFAULT, converter: typing.Callable[[Serializable], str] = repr,
                *, _tree: SectionProxy | None = None):
        '''
            Sets a key
            As values in INI are untyped strings, the following rulesets are used to retain typing, depending on if type_convert is:
                Behavior.DEFAULT:
                    If the type of val is in serializable_convert, then the value (callable) associated with that type is called to convert it
                    Then, val is checked for being an instance of any of serializable (isinstance(val, serializable)), throwing TypeError if it isn't
                    Then, val is passed to converter and saved
                Behavior.IGNORE:
                    Val is passed to converter without checking it against serializable or serializable_convert before being saved
        '''
        assert type_convert in {self.Behavior.DEFAULT, self.Behavior.IGNORE}
        key = self.key(key) if (_tree is None) else key
        if type_convert is self.Behavior.DEFAULT:
            if type(val) in self.serializable_convert:
                val = self.serializable_convert[type(val)](val)
        if not isinstance(val, self.serializable):
            raise TypeError(f'Cannot serialize type {type(val)} of {val!r}, must be one of {self.serializable} or {tuple(self.serializable_convert)}')
        (self._gettree(key, make_if_missing=True, fetch_if_missing=True) if (_tree is None) else _tree)[key[-1]] = converter(val)
        self.dirty.add(key[0])
    __setitem__ = setitem
    ## Containing
    @basic.locked
    def contains(self, key: Key, *, _tree: SectionProxy | None) -> bool:
        '''Returns whether or not the key exists'''
        key = self.key(key) if (_tree is None) else key
        sect = self._gettree(key, make_if_missing=False, fetch_if_missing=True, no_raise_keyerror=True) if (_tree is None) else _tree
        if (sect is None) or (key[-1] not in sect): return False
        return True
    __contains__ = contains
    ## Deleting
    @basic.locked
    def delitem(self, key: str | tuple[str]):
        '''Deletes an item'''
        key = self.key(key)
        ck = '.'.join(key[1:-1])
        if ck not in self.c[key[0]]:
            raise KeyError(f'{key} ({ck})')
        del self.c[key[0]][ck]
    __delitem__ = delitem
    # Low-level item manipulation
    @basic.locked
    def _gettree(self, key: tuple[str], *, make_if_missing: bool, fetch_if_missing: bool = True, no_raise_keyerror: bool = False) -> SectionProxy | None:
        '''Gets the section that contains key[-1]'''
        if key[0] not in self.c:
            if fetch_if_missing and self.tkey_path(key[0]).exists():
                self.readin(key[0])
            elif make_if_missing: self._init_topkey(key[0])
            elif no_raise_keyerror: return None
            else: raise KeyError(f'{key}[0]')
        ck = '.'.join(key[1:-1])
        if ck not in self.c[key[0]]:
            if not make_if_missing:
                if no_raise_keyerror: return None
                raise KeyError(f'{key} ({ck})')
            self.c[key[0]][ck] = {}
        return self.c[key[0]][ck]
