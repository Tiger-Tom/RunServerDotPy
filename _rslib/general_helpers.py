#!/bin/python3

# hack
import sys
sys.path.append('..')
import RunServer
RunServer.setup_logger()

#> Imports
import re
import logging
import json
import threading
import functools
from pathlib import Path
#</Imports

#> Header >/
# Hooks
class GenericHooks(dict):
    '''
        A class that implements hooks
        Hooks can be registered, and when exec_hooks is called, every hook is registered
        A hook can return HOOK_DESTROY, to delete itself after being called, or HOOK_FAILURE to raise a RuntimeError
    '''
    __slots__ = ()
    HOOK_DESTROY  = 0b00000001
    HOOK_FAILURE  = 0b00000010

    def __init__(self, *names):
        if names: self.add_hooks(*names)
        super().__init__(self)
    def add_hooks(self, *names):
        for h in names:
            self[h] = set()
    def register(self, hook, callback):
        if hook in self: self[hook].add(callback)
        else: self[hook] = {callback,}
    def exec_hooks(self, hook, *args, **kwargs):
        if hook not in self: return
        for h in tuple(self[hook]):
            v = h(*args, **kwargs)
            if not isinstance(v, int): continue
            if v & HOOK_DESTROY: self[hook].remove(h)
            if v & HOOK_FAILURE: raise RuntimeError(hook, h)
class ReHooks(GenericHooks):
    '''
        Hook keys are regular exceptions (or anything that implements a "match" function)
        This class implements a "match" function, which evaluates every key (regular expression pattern) and executes any hooks that match, passing the match object as a parameter
    '''
    __slots__ = ()

    def match(self, line: str):
        for p in self:
            if m := p.match(line):
                self.exec_hooks(p, m)
class SubHooks(GenericHooks):
    '''
        Basically a wrapper for a dict of hooks
    '''
    __slots__ = ()
    
    def __init__(self, *names):
        super().__init__(self)
        if names: self.add_hooks(*names)
    def add_hooks(self, *names):
        for h in names:
            self[h] = GenericHooks()
    def add_subhooks(self, hook, *subnames):
        if hook not in self: self[hook] = GenericHooks()
        self[hook].add_hooks(*subnames)
    def register(self, hook, subhook, callback):
        if hook not in self:
            self[hook] = GenericHooks()
        self[hook].register(subhook, callback)
    def exec_hooks(self, hook, subhook, *args, **kwargs):
        if hook not in self: return
        self[hook].exec_hooks(subhook, *args, **kwargs)
# Dictionary
class FileBackedDict(dict):
    '''
        A dictionary backed by an on-disk JSON file
        Asynchronously syncronized entries with a file on disk when enabled
        Detects file changes by checking its modification time
        Detects dict changes by adding it to a "dirty" flag
        Sub-dictionaries can be accessed with "/" notation
    '''
    __slots__ = ('logger', 'path', 'dirty', 'lock', 'bgtimer', 'watchdog_times')
    short_key_patt = re.compile(r'^[\w\d][\w\d\-; ()\[\].]*$')
    key_patt = re.compile(rf'^{short_key_patt.pattern}/.*?[^/]$')

    def __init__(self, path: Path):
        super().__init__()
        self.logger = logging.getLogger(f'FileBackedDict[{path.name}]')
        self.path = path
        self.dirty = set()
        self.lock = threading.RLock()
        self.watchdog_times = {}

    @staticmethod
    def _locked(func):
        @functools.wraps(func)
        def _synced(self, *args, **kwargs):
            with self.lock: return func(self, *args, **kwargs)
        return _synced
    def _keyify(self, key: str | tuple[str], allow_top_lvl_key: bool = False) -> tuple[str] | str:
        if isinstance(key, str):
            if self.key_patt.match(key) is None:
                if allow_top_lvl_key:
                    if self.short_key_patt.match(key) is None:
                        raise ValueError(f'Key must match pattern: {self.key_patt.pattern} or: {self.short_key_patt.pattern}')
                    return key
                raise ValueError(f'Key must match pattern: {self.key_patt.pattern}')
            key = tuple(key.split('/'))
        else:
            if (len(key) == 1) and allow_top_lvl_key:
                return key[0]
        return key

    @_locked
    def getitem(self, key: str | tuple[str], *, allow_unsafe_return: bool = False):
        self.logger.debug(f'{key}')
        key = self._keyify(key)
        if not self._rawcontains(key[0]):
            if (self.path / f'{key[0]}.json').exists(): self.readin(key[0])
            else: raise KeyError(f'{key}[0]')
        d = self._rawget(key[0])
        for i,k in enumerate(key[1:]):
            if k not in d: raise KeyError(f'{key}[{i+1}]')
            if not isinstance(d, dict): raise TypeError(f'Key {key}[{i+1}] tried to reference non-subkey {k} as a subkey')
            d = d[k]
        if isinstance(d, dict) and not allow_unsafe_return:
            raise TypeError(f'Unsafe direct read of possible subkey at {key}[-1], dicts should not be edited manually (try using "/" notation or allow_unsafe_return=True)')
        return d
    __getitem__ = getitem
    def _rawget(self, key: str): return super().__getitem__(key)
    @_locked
    def setitem(self, key: str | tuple[str], val, *, unsafe_write: bool = False):
        self.logger.debug(f'{key},{val!r}')
        key = self._keyify(key)
        if len(key) < 2: raise ValueError('Assigning to top-level (or no) keys is prohibited')
        if not self._rawcontains(key[0]): self._rawset(key[0], {})
        d = self._rawget(key[0])
        for i,k in enumerate(key[1:-1]):
            if k not in d: d[k] = dict()
            d = d[k]
            if not isinstance(d, dict): raise TypeError(f'Key {key}[{i+1}] tried to reference non-subkey {k} as a subkey')
        if isinstance(d.get(key[-1], None), dict) and not unsafe_write:
            raise TypeError(f'Unsafe write to potential sub-key at {key}[-1] (set unsafe_write=True to bypass)')
        d[key[-1]] = val
        self.dirty.add(key[0])
    __setitem__ = setitem
    def _rawset(self, key: str, val):
        if not key: raise ValueError(key)
        super().__setitem__(key, val)
    @_locked
    def delete(self, key: str | tuple[str] | None, *, allow_top_level_delete: bool = False, allow_subkey_delete: bool = False, collapse_empty: bool = True):
        if key is None: return
        key = self._keyify(key, allow_top_lvl_key=True)
        if isinstance(key, str):
            if not allow_top_level_delete:
                raise ValueError(f'Cannot delete a top-level key {key} -- set allow_top_lvl_key=True to bypass')
            self.logger.fatal(f'Deleting top-level key {key}')
            self._rawdel(key)
            (self.path / f'{key}.json').unlink(True)
            return
        d = self._rawget(key[0])
        for i,k in enumerate(key[1:-1]):
            if k not in d: raise KeyError(f'{key}[{i+1}]')
            if not isinstance(d, dict): raise TypeError(f'Key {key}[{i+1}] tried to reference non-subkey {k} as a subkey')
            d = d[k]
        if key[-1] not in d: raise KeyError(f'{key}[-1]')
        if isinstance(d[key[-1]], dict) and not allow_subkey_delete:
            raise TypeError(f'Unsafe write to potential sub-key at {key}[-1] (set allow_subkey_delete=True to bypass)')
        del d[key[-1]]
        self.dirty.add(key[0])
        if not collapse_empty: return
        for k in (key[:i] for i in range(len(key)-1, 0, -1)):
            if len(self[k]): break
            self.logger.warning(f'Collapsing empty: {k}')
            self.delete(k, allow_top_level_delete=True, allow_subkey_delete=True, collapse_empty=False)
    __delitem__ = delete
    def _rawdel(self, key: str):
        super().__delitem__(key)
    @_locked
    def contains(self, key: str | tuple[str], *, fetch_if_missing: bool = True) -> bool:
        self.logger.debug(key)
        key = self._keyify(key)
        if not self._rawcontains(key[0]):
            if fetch_if_missing and (self.path / f'{key[0]}.json').exists():
                self.readin(key[0])
                return self.contains(key, fetch_if_missing=False)
            return False
        d = self._rawget(key[0])
        for k in key[1:]:
            if (k not in d) or (not isinstance(d, dict)): return False
            d = d[k]
        return True
    __contains__ = contains
    def _rawcontains(self, key: str): return super().__contains__(key)

    @_locked
    def writeback(self, topkey: str, force: bool = False) -> int:
        if (not force) and (topkey not in self.dirty): return False
        self.logger.warning(f'Writing back {topkey}...')
        with (self.path / f'{topkey}.json').open('w') as f:
            json.dump(self._rawget(topkey), f, indent=4)
        self.watchdog_times[topkey] = (self.path / f'{topkey}.json').stat().st_mtime
        return True
    @_locked
    def writeback_alldirty(self):
        while len(self.dirty) and (k := self.dirty.pop()):
            self.writeback(k, force=True)
    @_locked
    def readin(self, topkey: str):
        self.logger.warning(f'Reading in {topkey}...')
        p = self.path / f'{topkey}.json'
        with p.open() as f:
            self._rawset(topkey, json.load(f))
        self.watchdog_times[topkey] = p.stat().st_mtime
    @_locked
    def readin_needed(self):
        self.logger.debug('Searching files...')
        rm = set()
        for k,t in self.watchdog_times.items():
            if not (self.path / f'{k}.json').exists(): rm.add(k)
            cmt = (self.path / f'{k}.json').stat().st_mtime
            if cmt == t: continue
            self.readin(k)
            self.watchdog_times[k] = cmt
        for k in rm:
            self.logger.fatal(f'File for key {k} missing, removing from watchdog')
            del self.watchdog_times[k]
    @_locked
    def sync_topkey(self, topkey: str | tuple[str]):
        self.logger.info(f'Syncing {topkey}...')
        self.writeback(topkey)
        self.readin(topkey)
    @_locked
    def sync_all(self):
        self.logger.info('Syncing all...')
        self.writeback_alldirty()
        self.readin_needed()
    @_locked
    def sync_all_bg_loop(self, interval_secs: float):
        self.logger.debug('bg_tick')
        self.sync_all()
        self.bgtimer = threading.Timer(interval_secs, self.sync_all_bg_loop, (interval_secs,))
        self.bgtimer.start()
    def start_bg_loop(self, interval_secs: float = 60.0):
        self.sync_all_bg_loop(interval_secs)
    @_locked # to avoid edge cases where bg_loop is already running and will set a timer object
    def stop_bg_loop(self) -> bool:
        r = self.bg_loop_running()
        self.bgtimer.cancel()
        return r
    @_locked
    def bg_loop_running(self):
        return hasattr(self, 'bgtimer') and self.bgtimer.is_alive()

    def close(self):
        if self.bgtimer: self.stop_bg_loop()
        self.sync_all()
    
    def __enter__(self): self.start_bg_loop()
    def __exit__(self): self.close()
