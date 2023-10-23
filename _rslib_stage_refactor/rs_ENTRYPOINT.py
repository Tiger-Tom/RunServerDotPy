#!/bin/python3

# The main program, or "entrypoint" #

#hacky
import sys
sys.path.append('..')

#> Imports
from _rslib_stage_refactor import *
#</Imports

#> Header >/
class RunServer:
    __slots__ = (
        'logger',
        'Bootstrapper', 'BS',
        'HelperTypes', 'HT',
    )
    def __init__(self, bs: 'Bootstrapper'):
        # Init
        self.Bootstrapper = self.BS = bs
        #self.logger = self.bs.root_logger
        #self.logger.info('Initializing entrypoint')
        # Helper types
        self.HelperTypes = self.HT = base.helper_types
    def __class_wrapper(rs, cls):
        class RunServerModule(cls):
            __slots__ = ('logger',)
            def __init__(self, rs: 'RunServer'):
                self.logger = rs.logger.getChild(self.__class__.__qualname__)
                super().__init__(self)
        RunServerModule.__slots__ += rs.__slots__
        return RunServerModule
    def __call__(self):
        self.logger.info('Entrypoint starting')
