#!/bin/python3

#> Imports
from pathlib import Path
from RS import Flags
# Chainloads
auto_eula = this.chainload(Path('./auto_eula.py'))
this.chainload(Path('./server_control_commands.py'))
#</Imports

#> Header >/
def __start__(self):
    auto_eula.check_eula()

def __restart__(self):
    Flags.force_restart = False
    Flags.force_no_restart = False
