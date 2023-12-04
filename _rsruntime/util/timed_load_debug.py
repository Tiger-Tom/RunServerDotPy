#!/bin/python3

#> Imports
import itertools
import typing
from types import TracebackType
from .perfcounter import PerfCounter
#</Imports

#> Header >/
__all__ = ('TimedLoadDebug',)

type t_messagefmt = tuple[tuple[str, str], tuple[str, str], typing.Callable[[type | None, typing.Any | None, TracebackType | None], str | None | typing.Literal[False]]]
class TimedLoadDebug:
    '''Helper class for debugging time spent doing things'''
    __slots__ = ('logfn', 'msgfmt', 'cur', 'ocounter', 'icounter')
    
    def __init__(self, logfunc: typing.Callable[[str], None],
                 messagefmt: t_messagefmt = (('started@T+{opc}', 'completed@T+{opc}'),
                                             ('start:load_{c}@T+{opc}', 'complete:load_{c}@T+{opc} (ΔT={ipc})'),
                                             lambda et, ev, tb: (False if (tb is not None) else None)),
                 iterable: typing.Iterable | typing.Callable[[], typing.Iterator] = itertools.count):
        self.logfn = logfunc; self.msgfmt = messagefmt
        self.ocounter = PerfCounter(sec='', secs=''); self.icounter = None
        self.logfn(self.msgfmt[0][0].format(opc=self.ocounter, ipc=self.icounter))
        self.cur = itertools.tee(iterable() if callable(iterable) else iter(iterable))
    def final(self):
        self.logfn(self.msgfmt[0][1].format(opc=self.ocounter, ipc=self.icounter))
        self.ocounter = None # stop accidental multiple final() calls
    def ienter(self):
        self.icounter = PerfCounter(sec='', secs='')
        self.logfn(self.msgfmt[1][0].format(c=next(self.cur[0]), opc=self.ocounter, ipc=self.icounter))
    __enter__ = ienter
    def iexit(self, exc_type: type | None, exc_value: typing.Any | None, traceback: TracebackType):
        r = self.msgfmt[2](exc_type, exc_value, traceback)
        if r is False: return
        self.logfn(self.msgfmt[1][1].format(c=next(self.cur[1]), opc=self.ocounter, ipc=self.icounter) if r is None else r)
    __exit__ = iexit

    @classmethod
    def foreach(cls, logfunc: typing.Callable[[str], None], *each: tuple[tuple[str, typing.Callable[[], None]], ...], **tld_args):
        '''Executes each callable (second element of every "each" tuple) in each and times it with TimedLoadDebug, setting {c} as the first element of every "each" tuple'''
        tld = cls(logfunc, iterable=(n for n,c in each), **tld_args)
        for n,c in each:
            with tld: c()
