#!/bin/python3

#> Imports
from pathlib import Path
# Parsing
import json
import re
# Types
from collections import UserDict
from .timer import Timer
from .locked_resource import LockedResource, locked
#</Imports

#> Header >/
class FileBackedDict(LockedResource, UserDict):
    '''
        A dictionary backed by an on-disk JSON file
        Asynchronously syncronizes entries with a file on disk when enabled
        Detects file changes by checking its modification time
        Detects dict changes by adding it to a "dirty" flag
        Sub-dictionaries can be accessed with "/" notation
    '''
    __slots__ = ('path', 'logger', 'dirty', 'watchdog', 'watchdog_times')
    key_patt_shrt = re.compile(r'^[\w\d][\w\d\t .\-;()[\]]*$')
    key_patt_long = re.compile(fr'^{key_patt_shrt.pattern[1:-1]}/.*?[^/]$')
    # Ironic that the word "short" is longer than the word "long"...

    def __init__(self, path: Path):
        self.data = {}
        self.path = path
        self.logger = logging.getLogger(f'FileBackedDict[{path.name.replace(".", "_")}]')
        self.dirty = set()
        self.watchdog = None; self.watchdog_times = None

    def key(self, *key: str | tuple[str], allow_top_lvl_key: bool = False) -> tuple[str]:
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
