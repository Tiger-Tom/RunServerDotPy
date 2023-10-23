#!/bin/python3

# The main program, or "entrypoint" #

#> Imports
from _rslib import helper_types
#</Imports

#> Header
class RunServer:
    __slots__ = (
        'logger',
        'Bootstrapper', 'BS',
        'HelperTypes', 'HT',
    )
    def __init__(self, bs: 'Bootstrapper'):
        self.logger = bs.root_logger
        self.logger.info('Initializing entrypoint')
        self.Bootstrapper = self.BS = bs
        self.HelperTypes = self.HT = helper_types
    def __calL__(self):
        self.logger.info('Entrypoint starting')
#</Header
