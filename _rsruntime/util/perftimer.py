#!/bin/python3

#> Imports
import time
import math
#</Imports

#> Header >/
__all__ = ('PerfCounter',)

class PerfCounter(float):
    '''Provides an object-oriented (because why not) way to use (and format) time.perf_counter'''
    __slots__ = ('prec', 'magic_prec_reduce', 'sec_text')
    def __new__(cls, prec: int = 3, sec: str = ' sec', secs: str = ' secs'):
        self = float.__new__(cls, time.perf_counter())
        self.__init__(prec, sec, secs)
        return self
    def __init__(self, prec: int = 3, sec: str = ' sec', secs: str = ' secs'):
        self.prec = prec # not used in calculations, for introspection (maybe) and bench_round
        self.magic_prec_reduce = 10**prec
        self.sec_text = (sec, secs)
    # Types
    def __round__(self) -> float:
        '''
            Rounds time.perf_counter()-self; slightly more efficient than builtin round() as we don't need to handle negatives
                Found to be roughly 113.20% faster than (taking 88.34% of the time of) the equivelant usage of builtin over 50000000 tests
                    (calculated via: `_benchmark_round(PerfCounter(), n=50000000, notify_every=0.01)`)
        '''
        return (int((time.perf_counter() - self) * self.magic_prec_reduce) + 0.5) / self.magic_prec_reduce
    __float__ = __round__
    def __int__(self) -> int:
        '''Rounds time.perf_counter()-self to an int; more efficient than builtin round() and keeps a bit more precision than builtin int()'''
        return int(time.perf_counter() - self + 0.5)
    def __repr__(self) -> str:
        '''Returns a string representing round(self)'''
        return float.__repr__(round(self))
    def __str__(self):
        '''Returns a string containing a rounded representation of self appended by self.sec_text[0] if rounded self is "plural" (not one), otherwise self.sec_text[1]'''
        r = round(self)
        return float.__str__(r)+self.sec_text[r != 1] # cursed code (explanation below)
        # r != 1 is a boolean, True if r is "plural" (not one), or False
        # sec_text is a tuple of strings in the form (text_if_singular, text_if_plural)
        # booleans can be used as indexes, resolving to 1 for True and 0 for False

def _benchmark_round(self: PerfCounter, n: int = 1000000, notify_every: float | None = None):
    '''Prints out benchmark results of PerfCounter.__round__ vs a function with body float.__round__(time.perf_counter()-PerfCounter, self.prec) (AKA the builtin equivelant)'''
    def float_round(self):
        return float.__round__(time.perf_counter()-self, self.prec)
    times = tuple((
        (-time.perf_counter())+((self.__round__() and 0)+time.perf_counter()), # equivelant to the `time.perf_counter()-temp` part of `temp = time.perf_counter(); self.__round__(); time.perf_counter()-temp`
        (-time.perf_counter())+((float_round(self) and 0)+time.perf_counter()), # equivelant to the `time.perf_counter()-temp` part of `temp = time.perf_counter(); float_round(self); time.perf_counter()-temp`
    ) for i in range(n) if (((notify_every is not None) and (not (i % int(n*notify_every))) and print(f'{i}/{n} ({i/n*100}%)')) or True))
    totals = (sum(t[0] for t in times), sum(t[1] for t in times))
    print(f'--Results of {n} runs--')
    print(f'category:{"average":^26}|{"overall":^26}')
    print(f'new impl:{totals[0]/n:.20E}|{totals[0]:.20E}')
    print(f'builtin: {totals[1]/n:.20E}|{totals[1]:.20E}')
    print('-'*len(f'--Results of {n} runs--'))
    print(f'new impl. / builtin = {(totals[0] / totals[1] * 100):.2f}%')
    print(f'new impl. is {(totals[1] / totals[0] * 100):.2f}% faster than builtin')
