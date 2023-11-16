#!/bin/python3

#> Imports
from pathlib import Path
import warnings
#</Imports

# RunServer Module
import RS
from RS.Util import FileBackedDict

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
    def mass_set_default(self, pfx: str | None = None, dict_vals: dict[str, ...] | None = None, **values: dict[str, ...]):
        '''
            Sets a large amount of default values
                When pfx is not None, it is prepended (with a / if it doesn't already have one) to each key
            Values are either given through dict_vals or **values (keyword args)
                Using both is probably bad but not prohibited
                    A SyntaxWarning shall be issued upon you to remind you of your choices. 
                If a value is in both:
                    if it is the same in both, a UserWarning is issued
                    if it is not the same in both, ValueError is raised
                    Once this has been checked, they are merged together
            If a total of 0 values are given, an error is logged
            If a total of 1 value is given, a warning is logged
            Otherwise, an infop is logged decribing how many keys will be set
        '''
        if dict_vals is not None:
            if dict_vals.keys() and values.keys():
                warnings.warn('Using both dict_vals and values is a bad practice', SyntaxWarning)
            for k in dict_vals.keys() & values.keys():
                if dict_vals[k] == values[k]: continue
                raise ValueError(f'''Cannot resolve *A* (there could be more!) mismatched duplicate key from dict_vals and **values:
                    dict_vals[{k!r}] = {dict_vals[k]!r}
                    values    = {values[k]!r}''')
            values |= dict_vals
        if len(values) == 0:
            self.logger.error(f'Instructed to set mass default of 0 values?')
            return
        if len(values) == 1:
            self.logger.warning(f'Setting mass default on 1 value')
            self.get_set_default(*(*values.items(),))
            return
        self.logger.infop(f'Setting mass default on {len(values)} values')
        with self.lock:
            # Store bg loop
            resume = self.is_autosyncing()
            if resume: self.stop_autosync()
            # Final sync and begin setting defaults
            self.sync_all()
            if pfx is None: pfx = ''
            elif not pfx.endswith('/'): pfx = f'{pfx}/'
            for k,v in values.items():
                self.set_default(f'{pfx}{k}', v)
            # Resume bg loop if needed
            if resume: self.start_autosync()
    def close(self):
        self.stop_autosync()
        self.sync_all()
