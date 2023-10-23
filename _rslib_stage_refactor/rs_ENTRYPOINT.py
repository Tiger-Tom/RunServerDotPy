#!/bin/python3

# The main program, or "entrypoint" #

#> Imports
from _rslib import helper_types
from _rslib.rschatcommand import ChatCommands
from _rslib.rsconfig import Config
from _rslib.rsio import RSIO
from _rslib.rsmcserv import MCServerLang, MCServerOutputParser, UserManager, Tellraw
from _rslib.rschatcommand import ChatCommands
from _rslib.rsplugins import PluginManager
#</Imports

#> Header
class RunServer:
    __slots__ = (
        'logger',
        'HelperTypes', 'HT',
        'Bootstrapper', 'BS',
        'Config', 'C',
        'IO',
        'Lang', 'L',
        'Parser', 'Pa',
        'Users', 'U',
        'Tellraw', 'TR',
        'ChatCommands', 'CC',
        'Plugins', 'P',
    )
    def __init__(self, bs: 'Bootstrapper'):
        self.logger = bs.root_logger
        self.logger.info('Initializing entrypoint')
        self.HelperTypes = self.HT = helper_types
        self.Bootstrapper = self.BS = bs
        self.Config = self.C = Config(self)
        self.IO = RSIO(self)
        self.Lang = self.L = MCServerLang(self)
        self.Parser = self.Pa = MCServerOutputParser(self)
        self.Users = self.U = UserManager(self)
        self.Tellraw = self.TR = Tellraw(self)
        self.ChatCommands = self.CC = ChatCommands(self)
        self.Plugins = self.P = PluginManager(self)
    def __calL__(self):
        self.logger.info('Entrypoint starting')
#</Header
