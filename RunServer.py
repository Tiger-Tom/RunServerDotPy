#!/bin/python3

#> Imports
import sys
#</Imports

#> Header
def chainload_bootstrapper():
    from _rsruntime.rs_BOOTSTRAP import Bootstrapper
    bs = Bootstrapper()
    bs.bootstrap()
    return bs
def fetch_bootstrapper():
    ...
#</Header

#> Bootstrap >/
if __name__ == '__main__':
    try:
        from _rsruntime.rs_BOOTSTRAP import Bootstrapper
    except ImportError as e:
        raise e
    RS_Bootstrapper = chainload_bootstrapper()
