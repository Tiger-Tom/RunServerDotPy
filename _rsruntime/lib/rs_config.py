#!/bin/python3

#> Imports
from pathlib import Path
# Types
from enum import Enum
#</Imports

# RunServer Module
import RS
from RS.Types import LockedResource, locked

#> Header >/
class Config(RS.FileBackedDict):
    '''A thin wrapper around FileBackedDict'''
    __slots__ = ('logger',)
    conf_path = Path('./_rsconfig/')


    def __init__(self):
        self.logger = RS.logger.getChild('Config')
        self.conf_path.mkdir(parents=True, exist_ok=True)
        super().__init__(self.conf_path, 60.0)

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
                if default is None: raise ExceptionGroup(KeyError(key), TypeError('Default is None'))
                self[key] = default
                return default
            case self.on_missing.ERROR: raise KeyError(key)

    def get_set_default(self, key: str | tuple[str], default):
        '''
            Gets an item.
            If the item doesn't exist, tries to set "default" as its value and returns default with set_default
        '''
        self.set_default(key, default)
        return self[key]
    def set_default(self, key: str | tuple[str], default):
        '''If the item corresponding to key doesn't exist, then set it to default. Has no effect otherwise'''
        if key not in self:
            self.logger.warn(f'Setting default for {key}')
            self[key] = default
    def mass_set_default(self, **values):
        if len(values) == 0:
            self.logger.error(f'Instructed to set mass default of 0 values?')
            return
        if len(values) == 1:
            self.logger.warning(f'Setting mass default on 1 value')
            self.get_set_default(*(*values.items(),))
            return
        self.logger.warning(f'Setting mass default on {len(values)} values')
        with self.lock:
            # Store bg loop
            resume = self.is_autosyncing()
            if resume: self.stop_autosync()
            # Final sync and begin setting defaults
            self.sync_all()
            for k,v in values.items():
                self.set_default(k, v)
            # Resume bg loop if needed
            if resume: self.fbd.sync_all_bg_loop(intvl)
            else: self.start_autosync()
