#!/bin/python3

'''This is simply a stub file that fetches the bootstrapper (if it's missing) and executes it'''

#> Imports
from pathlib import Path
#</Imports

#> Bootstrap**2 >/
if __name__ == '__main__':
    try:
        from _rsruntime.rs_BOOTSTRAP import Bootstrapper
    except ImportError as e:
        import sys
        from urllib import request
        print(e, file=sys.stderr)
        bpath = Path('_rsruntime/rs_BOOTSTRAP.py')
        bpath.parent.mkdir(parents=True, exist_ok=True)
        request.urlretrieve('https://raw.githubusercontent.com/Tiger-Tom/RunServerDotPy/v3.x.x/_rsruntime/rs_BOOTSTRAP.py', bpath)
        from _rsruntime.rs_BOOTSTRAP import Bootstrapper
    RS_Bootstrapper = Bootstrapper()
    RS_Bootstrapper.bootstrap()
