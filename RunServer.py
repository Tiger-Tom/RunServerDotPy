#!/bin/python3

'''This is simply a stub file that fetches the bootstrapper (if it's missing) and executes it'''

#> Imports
import os
import sys
from pathlib import Path
#</Imports

# Typeguard
if os.getenv('RS_USETYPEGUARD'):
    import typeguard
    class CustomFinder(typeguard.TypeguardFinder):
        exclude = {'cryptography.hazmat.backends.',}
        def should_instrument(self, module_name: str) -> bool:
            return not any(module_name.startswith(p) for p in self.exclude)
    typeguard.install_import_hook(cls=CustomFinder)

#> Bootstrap**2 >/
if __name__ == '__main__':
    try:
        from _rsruntime.rs_BOOTSTRAP import Bootstrapper
    except ImportError as e:
        from urllib import request
        print(e, file=sys.stderr)
        bpath = Path('_rsruntime/rs_BOOTSTRAP.py')
        bpath.parent.mkdir(parents=True, exist_ok=True)
        request.urlretrieve('https://raw.githubusercontent.com/Tiger-Tom/RunServerDotPy/v3.x.x/_rsruntime/rs_BOOTSTRAP.py', bpath)
        from _rsruntime.rs_BOOTSTRAP import Bootstrapper
    RS_Bootstrapper = Bootstrapper()
    RS_Bootstrapper.bootstrap()
