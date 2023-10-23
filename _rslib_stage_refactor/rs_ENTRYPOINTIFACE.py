#!/bin/python3

#> Imports
#</Imports

#> Header >/
class RunServerModule:
    __slots__ = (
        'rs',
        'logger',
        'BS',
        'HT',
    )

    def __init__(self, rs: 'RunServer'):
        self.logger = self.rs.logger.getChild(__class__.__qualname__)
        self.BS = self.rs.BS
        self.HT = self.rs.HT
