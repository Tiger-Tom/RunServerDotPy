#!/bin/python3

#> Imports
import sys
#</Imports

#> Bootstrap >/
if __name__ == '__main__':
    if 1:#try:
        from _rsruntime.rs_BOOTSTRAP import Bootstrapper
        bs = Bootstrapper() # not the kind you're thinking of!!!
    #except Exception as e:
    #    ...
    bs.bootstrap()
