#!/bin/python3

#> Imports
import abc
#</Imports

# RunServer Module
RunServer = RS = NotImplemented

#> Header >/
# Base classes
class BaseServerManager(abc.ABC):
    ...
class BasePopenManager(BaseServerManager):
    ...
# Implementations
class ScreenManager(BaseServerManager):
    ...
class RConManager(BaseServerManager):
    ...
class SelectManager(BasePopenManager):
    ...
# Manager
class ServerManager:
    def __new__(cls):
        return super().__new__(self.preferred_order[0])
    @classmethod
    def preferred_order(cls) -> tuple[BaseServerManager]:
        raise NotImplementedError

ServerManager.BaseServerManager = BaseServerManager
ServerManager.BasePopenManager = BasePopenManager
ServerManager.ScreenManager = ScreenManager
ServerManager.RConManager = RConManager
ServerManager.SelectManager = SelectManager
