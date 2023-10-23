#!/bin/python3

#> Imports
# Types
from abc import ABC, abstractmethod, abstractproperty
import typing
# System
import threading
import sys
import subprocess
import selectors
# general_helpers.py
from _rslib import general_helpers as helpers
#</Imports

#> Logging
import logging
#</Logging

#> Header >/
# Main IO Handler base class
class RSIO_Base(ABC):
    __slots__ = ('rs', 'logger', 'hooks', 'cmdline')
    def __init__(self, rs: 'RunServer'):
        self.rs = rs
        #self.hooks = helpers.GenericHooks('input', 'output')
        #self.logger = rs.logger.getChild('RunServer.IO')
        #self.logger.debug(f'Initialized: {self}')
    def register(self, hook: typing.Literal['input', 'output'], callback: typing.Callable):
        self.logger.debug(f'Registering {hook} hook: {callback}')
        self.hooks.register(hook, callback)

    @classmethod
    @property # could be overridden, but is still optional
    def type(cls) -> str:
        return '/'.join(t for c in cls.__mro__[cls.__mro__.index(RSIO_Base)-1::-1] for t in c._type)
    @classmethod
    @abstractproperty
    def supports_detach(cls) -> bool: pass
    @abstractproperty
    def metadata(cls) -> dict | None: pass

    @abstractmethod
    def start(self): pass
    @abstractmethod
    def write(self, line: str): pass

    #optional abstractmethod
    def detach(self):
        if self.supports_detach:
            raise NotImplementedError(f'{self} supports detaching but does not implement it')
        else: raise TypeError(f'{self} does not support detaching')
# Generic writer implementation
class RSIO_PopenWriter(RSIO_Base):
    __slots__ = ('proc_stdin',)
    
    _type = ('popen_writer',)

    def __init__(self, rs: 'RunServer'):
        self.proc_stdin = pop.stdin
        super().__init__(rs)
    def write(self, line: str):
        return self.proc_stdin.write(line)
    
# Select implementation
class RSIO_Select(RSIO_PopenWriter):
    __slots__ = ('sel', 'iothread')

    _type = ('builtin_select',)
    supports_detach = True
    metadata = None

    def __init__(self, rs: 'RunServer'):
        self.sel = selectors.DefaultSelector()
        super().__init__(rs, pop)
        self.sel.register(pop.stdout, selectors.EVENT_READ)
        self.sel.register(sys.stdin, selectors.EVENT_READ)
    def select(self):
        return self.sel.select()
    def start(self):
        self.iothread = threading.Thread(target=self._start, daemon=True)
        self.iothread.start()
    def _start(self):
        
# Screen implementation
class RSIO_Screen(RSIO_Base):
    __slots__ = ()
    
    _type = ('builtin_screen',)
    supports_detach = True
    metadata = None

    def __init__(self, rs: 'RunServer', pop: subprocess.Popen):
        super().__init__(rs, pop)
