#!/bin/python3

#> Imports
from pathlib import Path
import functools
import logging
# Parsing
import json
import re
# Types
import typing
from collections import UserDict
from enum import Enum
from .timer import Timer
from .locked_resource import LockedResource, locked
#</Imports

#> Header >/
serializable = (dict, list, str, int, float, bool, type(None))

class FileBackedDict(UserDict, LockedResource):
    '''
        A dictionary backed by an on-disk JSON file
        Asynchronously synchronizes entries with a file on disk when enabled
        Detects file changes by checking its modification time
        Detects dict changes by adding keys to a "dirty" flag
        Sub-dictionaries can be accessed with "/" notation
    '''
    __slots__ = ('path', 'logger', 'dirty', 'watchdog', 'watchdog_times')
    key_patt_shrt = re.compile(r'^[\w\d][\w\d\t .\-;()[\]]*$')
    key_patt_long = re.compile(fr'^{key_patt_shrt.pattern[1:-1]}/.*?[^/]$')
    # Ironic that the word "short" is longer than the word "long"...

    def __init__(self, path: Path, interval: float = 120.0):
        LockedResource.__init__(self)
        UserDict.__init__(self)
        self.path = Path(path) # path path path
        self.logger = logging.getLogger(f'FileBackedDict[{self.path.name.replace(".", "_")}]')
        self.dirty = set()
        self.watchdog = Timer.set_interval(self.sync_all, interval, False); self.watchdog_times = {}
    def __hash__(self):
        '''Exclusively for functools.cache'''
        return hash((self.path, self.key_patt_long.pattern, self.key_patt_shrt.pattern))

    # Key functions
    @functools.cache
    def key(self, key: str | tuple[str], *, allow_top_lvl_key: bool = False) -> tuple[str]:
        '''
            Converts a str a key, ensures that it matches against key_patt_long
                (or key_patt_shrt if allow_top_lvl_key is truthy)
            When passed a tuple of str, simply checks if it meets length requirements
        '''
        if isinstance(key, str):
            if self.key_patt_long.fullmatch(key) is not None:
                key = tuple(key.split('/'))
            elif allow_top_lvl_key:
                if self.key_patt_shrt.fullmatch(key) is None:
                    raise ValueError(f'Key must match pattern {self.key_patt_shrt.pattern} or {self.key_patt_long.pattern}')
                return (key,)
            else:
                raise ValueError(f'Key must match pattern: {self.key_patt_long.pattern}')
        if len(key) == 0: raise ValueError('Key cannot have a length of 0')
        elif len(key) == 1 and not allow_top_lvl_key:
            raise ValueError(f'Key cannot be a top-level key')
        return key
    @functools.cache
    def key_path(self, key: str | tuple[str]) -> Path:
        '''Converts the key with self.key(), returns the Path corresponding to its JSON file'''
        return self.path / f'{self.key(key, allow_top_lvl_key=True)[0]}.json'

    # Dict functions
    @locked
    def _get_(self, key: tuple[str], *, make_if_missing: bool = False, no_raise: bool = False) -> dict | None:
        '''Gets the dictionary referenced by the key, useful for mutating'''
        d = self.data
        for i,k in enumerate(key):
            if k not in d:
                if not make_if_missing:
                    if no_raise: return None
                    raise KeyError(f'{key}[{i}]')
                d[k] = {}
            d = d[k]
            if not isinstance(d, dict):
                if no_raise: return None
                raise TypeError(f'{key}[{i}] referenced as subkey, but it is a value')
        return d
    ## Getting
    @locked
    def get_item(self, key: str | tuple[str], *, unsafe_allow_get_subkey: bool = False) -> typing.Union[*serializable]:
        '''
            Gets an item
                (raises TypeError upon trying to return a dict, use unsafe_allow_get_subkey=True to bypass)
            If the top-level key cannot be found, but it exists in JSON form, then it is read in
                (if a key is not found, KeyError is raised)
        '''
        key = self.key(key) # key key key
        if key[0] not in self.data:
            if not self.key_path(key).exists(): raise KeyError(f'{key}[0]')
            self.readin_data(key[0])
        d = self._get_(key[:-1])
        if key[-1] not in d: raise KeyError(f'{key}[-1]')
        if (not unsafe_allow_get_subkey) and isinstance(d[key[-1]], dict): raise TypeError(f'{key} refers to a subkey, pass unsafe_allow_get_subkey=True to bypass')
        return d[key[-1]]
    __getitem__ = get_item
    def get_set_default(self, key: str | tuple[str], default):
        '''
            Gets an item.
            If the item doesn't exist, tries to set "default" as its value and returns default with set_default
        '''
        self.set_default(key, default)
        return self[key]
    ## Setting
    def set_item(self, key: str | tuple[str], val: typing.Any | dict, *, unsafe_allow_set_subkey: bool = False, unsafe_allow_assign_dict: bool = False):
        '''	
            Sets an item.
                Throws TypeError upon trying to overwrite a subkey, pass unsafe_allow_set_subkey=True (also implied by unsafe_allow_set_top_lvl_key=True) to bypass
                Throws TypeError upon trying to assign a dict (AKA subkey) as a value, pass unsafe_allow_assign_dict=True to bypass
        '''
        if isinstance(val, dict) and not unsafe_allow_assign_dict:
            raise TypeError('Cannot assign dict as value, pass unsafe_allow_assign_dict=True (also implied by unsafe_allow_set_subkey=True) to bypass')
        key = self.key(key) # key key key
        d = self._get_(key[:-1], make_if_missing=True)
        if (not unsafe_allow_set_subkey) and (key[-1] in d) and isinstance(d[key[-1]], dict):
            raise TypeError('Cannot assign to a subkey, pass unsafe_allow_set_subkey=True to bypass')
        d[key[-1]] = val
        self.dirty.add(key[0])
    __setitem__ = set_item
    def set_default(self, key: str | tuple[str], default):
        '''If the item corresponding to key doesn't exist, then sets it to default. Has no effect otherwise'''
        if key not in self:
            self.logger.warn(f'Setting default for {key}')
            self[key] = default
    ## Containing
    @locked
    def contains(self, key: str | tuple[str], *, unsafe_no_error_on_subkey: bool = False) -> bool:
        '''
            Checks if the key exists
                If the key resolves to a subkey, then TypeError is raised unless unsafe_no_error_on_subkey is truthy
        '''
        key = self.key(key) # key key key
        if key[0] not in self.data:
            if not self.key_path(key).exists(): return False
            self.readin_data(key[0])
        d = self._get_(key[:-1], no_raise=True)
        if (d is None) or (key[-1] not in d): return False
        if (not unsafe_no_error_on_subkey) and isinstance(d[key[-1]], dict):
            raise TypeError(f'{key} resolved to a subkey, pass unsafe_no_error_on_subkey=True if this is intended')
        return True
    __contains__ = contains
    ## Deleting
    @locked
    def delete(self, key: str | tuple[str], *, unsafe_allow_delete_subkey: bool = False):
        '''
            Deletes an item
            Raises TypeError upon trying to delete a suspected subkey (dict), pass unsafe_allow_delete_subkey=True to bypass
        '''
        key = self.key(key) # key key key
        d = self._get_(key[:-1])
        if key[-1] not in d: raise KeyError(f'{key}[-1]')
        if (not unsafe_allow_delete_subkey) and isinstance(d[key[-1]], dict):
            raise TypeError(f'{key} refers to a subkey, pass unsafe_allow_delete_subkey=True to bypass')
        del d[key[-1]]
        self.prune(key[0])
        self.dirty.add(key[0])
    __delitem__ = delete
    @locked
    def remove(self, key: str, *, unsafe_I_know_what_I_am_doing: bool = False):
        '''Deletes a top level key AND it's corresponding JSON file. Don\'t call if you don\'t know what you are doing'''
        if not I_know_what_I_am_doing: raise RuntimeError('Pass unsafe_I_know_what_I_am_doing=True if you really want to do this')
        del self.data[key]
        self.key_path(key).unlink()
        self.dirty.remove(key)
        self.watchdog_times
    ### Pruning
    def __count_entries(self, d: dict) -> int:
        '''
            Recursively counts non-dictionary entries in d
            Should never be called unless the lock is held, but is not locked by default for performance reasons
        '''
        return sum(self.__count_entries(e) if isinstance(e, dict) else 1 for e in d.values())
    def __prune(self, data: dict):
        '''
            Recursively removes empty dictionaries in data
            Should never be called unless the lock is held, but is not locked by default for performance reasons
        '''
        for k,v in tuple(data.items()):
            if not isinstance(v, dict): continue
            if self.__count_entries(v) == 0:
                del data[k]
                continue
            self.__prune(v)
    @locked
    def prune(self, start_key: str | None = None):
        '''Recursively removes empty dictionaries, starting with start_key (or from root if start_key is None)'''
        self.__prune(self.data if start_key is None else self._get_(self.key(start_key, allow_top_lvl_key=True)))

    # Augmented get
    on_missing = Enum('OnMissing', ('RETURN_DEFAULT', 'SET_RETURN_DEFAULT', 'SET_RETURN_DEFAULT_BUT_ERROR_ON_NONE', 'ERROR'))
    def __call__(self, key: str | tuple[str], default: None | typing.Any = None, on_missing: on_missing = on_missing.SET_RETURN_DEFAULT_BUT_ERROR_ON_NONE):
        '''
            Behavior of on_missing when the key isn't found:
                RETURN_DEFAULT: returns the default field
                SET_RETURN_DEFAULT: same as the get_set_default method
                SET_RETURN_DEFAULT_BUT_ERROR_ON_NONE: (the default) same as SET_RETURN_DEFAULT unless default is None, in which case ExceptionGroup(KeyError, TypeError) is raised
                ERROR: raises KeyError
        '''
        assert isinstance(on_missing, self.on_missing)
        if key in self: return self[key]
        match on_missing:
            case self.on_missing.RETURN_DEFAULT: return default
            case self.on_missing.SET_RETURN_DEFAULT:
                self[key] = default
                return default
            case self.on_missing.SET_RETURN_DEFAULT_BUT_ERROR_ON_NONE:
                if default is None: raise ExceptionGroup('Key was not found, on_missing is SET_RETURN_DEFAULT_BUT_ERROR_ON_NONE, and default=None', (KeyError(key), TypeError('Default is None')))
                self[key] = default
                return default
            case self.on_missing.ERROR: raise KeyError(key)

    # Data sync functions
    ## Reading in
    @locked
    def readin_data(self, key: str):
        '''Reads in data from the JSON value corresponding to key (found via self.key_path)'''
        p = self.key_path(key)
        self.logger.warning(f'Reading in {key} from {p}...')
        with p.open() as f:
            self.data[key] = json.load(f)
        self.watchdog_times[key] = p.stat().st_mtime
    @locked
    def readin_watchdog(self):
        '''
            Reads in data from files that have been modified since the last read
            If a file is missing, it is removed from the watchdog list
        '''
        self.logger.debug(f'Readin watchdog ticked: checking {len(self.watchdog_times)} key(s)')
        for k,t in tuple(self.watchdog_times.items()):
            p = self.key_path(k)
            if not p.exists():
                self.logger.warning(f'File {p} no longer exists, removing {k} from watchdogs')
                del self.watchdog_times[k]
                continue
            nt = p.stat().st_mtime
            if nt <= t: continue
            self.watchdog_times[k] = nt
            self.readin_data(k)
    ## Writing back
    @locked
    def writeback(self, key: str, *, clean: bool = True, force: bool = False) -> bool:
        '''
            Writes back a top-level key to its JSON file
                If "force" is not truthy, and the key is not dirty, then nothing is written back and False is returned
                Otherwise:
                - the data is written back
                - watchdog times are updated
                - the key is "cleaned" (removed from dirty) if clean is Truthy
                - True is returned
        '''
        if (not force) and (key not in self.dirty): return False
        self.prune(key)
        p = self.key_path(key)
        self.logger.warning(f'Writing back {key} to {p}...')
        with p.open('w') as f:
            json.dump(self.data[key], f, indent=4)
        self.watchdog_times[key] = p.stat().st_mtime
        if clean: self.dirty.remove(key)
        return True
    @locked
    def writeback_dirty(self):
        '''Writes back all dirty keys'''
        self.logger.debug(f'Writing back dirty keys: {len(self.dirty)} key(s) to clean')
        while len(self.dirty):
            self.writeback(self.dirty.pop(), clean=False, force=True)
    ## Dual-ways sync
    @locked
    def sync_all(self):
        self.logger.info('Syncing all...')
        self.writeback_dirty()
        self.readin_watchdog()
    ## Sync timer
    @locked
    def start_autosync(self):
        self.watchdog.start()
    @locked
    def stop_autosync(self):
        self.watchdog.stop()
    @locked
    def is_autosyncing(self) -> bool:
        return self.watchdog.is_alive()
