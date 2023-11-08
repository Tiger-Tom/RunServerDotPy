#!/bin/python3

#> Imports
import sys
#</Imports

#> Header
def chainload_bootstrapper():
    from _rsruntime.rs_BOOTSTRAP import Bootstrapper
    bs = Bootstrapper()
    bs.bootstrap()
def fetch_bootstrapper():
    ...
#</Header

#> Bootstrap >/
if __name__ == '__main__':
    try:
        from _rsruntime.rs_BOOTSTRAP import Bootstrapper
    except Exception as e:
        ...
    chainload_bootstrapper()
