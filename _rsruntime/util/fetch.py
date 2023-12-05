#!/bin/python3

#> Imports
import typing
from urllib import request
from functools import partial
#</Imports

#> Header >/
__all__ = ('CHUNK_FETCH_ABORT', 'fetch', 'fetch_nocache', 'chunk_fetch', 'foreach_chunk_fetch')

cache = {}

def fetch(url: str, *, add_to_cache: bool = True, ignore_cache: bool = False, **urlopen_kwargs) -> bytes:
    '''
        Fetch bytes from the URL
        If the URL is cached, and ignore_cache is false, then returns the cached value
        Otherwise, fetch the data and return it, as well as add it to the cache if add_to_cache is true
    '''
    h = hash(url)
    if (not ignore_cache) and (h in cache): return _cache[h]
    with request.urlopen(url, **urlopen_kwargs) as r:
        d = r.read()
        if add_to_cache: cache[h] = d
        return d
#__call__ = fetch   # one day...
fetch_nocache = partial(fetch, add_to_cache=False, ignore_cache=True)

class Chunk(bytes):
    target:     str
    chunk_size: int
    from_cache: bool
    obtained:   int
    remain:     int

    def __call__(self, d_attrs: dict = {}, **kw_attrs: dict) -> typing.Self:
        self.__dict__ |= d_attrs | kw_attrs
        return self
    def __bytes__(self) -> bytes: return self

    def format(self, fmt: str) -> str:
        return fmt.format_map(self.__dict__)
    __format__ = format

CHUNK_FETCH_ABORT = object()
def chunk_fetch(url: str, chunksize: int = 1024**2*4, *, add_to_cache: bool = False, ignore_cache: bool = False) -> typing.Generator[Chunk, None | typing.Literal[CHUNK_FETCH_ABORT], bytes]:
    '''
        Fetch and yield bytes from the URL in chunks of chunksize
        Yields a Chunk object
        If the URL is cached, and ignore_cache is false, then yields the data (as Chunk, with from_cache=True) and returns it
        Once all data has been read and yielded, it is returned as bytes, and added to the cache if add_to_cache is true
            Cache is not written to if CHUNK_FETCH_ABORT is used to interrupt the download
    '''
    d_attrs = {'target': url, 'chunk_size': chunksize, from_cache: False}
    h = hash(url)
    if (not ignore_cache) and (h in cache):
        d = cache[h]
        yield Chunk(d)(d_attrs, from_cache=True, obtained=len(d), remain=0)
        return d
    data = bytearray()
    with request.urlopen(url) as r:
        while r.length:
            d = r.read(chunksize)
            data.extend(d)
            if (yield Chunk(d)(d_attrs, obtained=len(data), remain=r.length, chunk_size=chunksize)) is CHUNK_FETCH_ABORT:
                return bytes(b) # do not add aborted data to cache
    if add_to_cache: cache[h] = data
    return bytes(data)
def foreach_chunk_fetch(url: str, callback: typing.Callable[[Chunk], None | typing.Literal[CHUNK_FETCH_ABORT]] = lambda *d: ..., chunksize: int = 1024**2*4, **cfetch_kwargs) -> bytes:
    cfi = chunk_fetch(url, chunksize, **cfetch_kwargs)
    while True:
        try: chunk = next(cfi)
        except StopIteration as e:
            return e.value
        else:
            if callback(chunk) is CHUNK_FETCH_ABORT:
                cfi.send(CHUNK_FETCH_ABORT)
