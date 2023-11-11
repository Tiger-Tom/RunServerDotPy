#!/bin/python3

#> Imports
from pathlib import Path
#</Imports

# RunServer Module
import RS
from RS.Types import FileBackedDict, LockedResource, locked

#> Header >/
class Config(FileBackedDict):
    '''A thin wrapper around FileBackedDict'''
    __slots__ = ('logger',)
    conf_path = Path('./_rsconfig/')

    def __init__(self):
        self.logger = RS.logger.getChild('C')
        self.conf_path.mkdir(parents=True, exist_ok=True)
        super().__init__(self.conf_path, 60.0)
        self.start_autosync()
        RS.BS.register_onclose(self.close)
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
    def close(self):
        self.stop_autosync()
        self.sync_all()
