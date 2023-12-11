[Standalone doc: parts/RunServer/ShaeLib/net/RunServer.ShaeLib.net.fetch.md](RunServer.ShaeLib.net.fetch)  

## `CHUNK_FETCH_ABORT` (`RunServer.ShaeLib.net.fetch.CHUNK_FETCH_ABORT` | `RS.SL.net.fetch.CHUNK_FETCH_ABORT`)
[Standalone doc: parts/RunServer/ShaeLib/net/fetch/RunServer.ShaeLib.net.fetch.CHUNK_FETCH_ABORT.md](RunServer.ShaeLib.net.fetch.CHUNK_FETCH_ABORT)  
> The base class of the class hierarchy.  
>   
> When called, it accepts no arguments and returns a new featureless  
> instance that has no instance attributes and cannot be given any.

## `chunk_fetch` (`RunServer.ShaeLib.net.fetch.chunk_fetch` | `RS.SL.net.fetch.chunk_fetch`)
[`_rsruntime/ShaeLib/net/fetch.py`](/_rsruntime/ShaeLib/net/fetch.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/net/fetch/RunServer.ShaeLib.net.fetch.chunk_fetch.md](RunServer.ShaeLib.net.fetch.chunk_fetch)  
> Fetch and yield bytes from the URL in chunks of chunksize  
> Yields a Chunk object  
> If the URL is cached, and ignore_cache is false, then yields the data (as Chunk, with from_cache=True) and returns it  
> Once all data has been read and yielded, it is returned as bytes, and added to the cache if add_to_cache is true
>> Cache is not written to if CHUNK_FETCH_ABORT is used to interrupt the download

## `fetch` (`RunServer.ShaeLib.net.fetch.fetch` | `RS.SL.net.fetch.fetch`)
[`_rsruntime/ShaeLib/net/fetch.py`](/_rsruntime/ShaeLib/net/fetch.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/net/fetch/RunServer.ShaeLib.net.fetch.fetch.md](RunServer.ShaeLib.net.fetch.fetch)  
> Fetch bytes from the URL  
> If the URL is cached, and ignore_cache is false, then returns the cached value  
> Otherwise, fetch the data and return it, as well as add it to the cache if add_to_cache is true

## `fetch_nocache` (`RunServer.ShaeLib.net.fetch.fetch_nocache` | `RS.SL.net.fetch.fetch_nocache`)
[Standalone doc: parts/RunServer/ShaeLib/net/fetch/RunServer.ShaeLib.net.fetch.fetch_nocache.md](RunServer.ShaeLib.net.fetch.fetch_nocache)  
> partial(func, *args, **keywords) - new function with partial application  
> of the given arguments and keywords.

### fetch(...)
```python
@staticmethod
def fetch(...) -> bytes
```
<details>
<summary>Parameters...</summary>

```python
    url: str, add_to_cache: bool = True, ignore_cache: bool = False,
    add_headers
```
</details>

[`_rsruntime/ShaeLib/net/fetch.py@24:34`](/_rsruntime/ShaeLib/net/fetch.py#L24)

<details>
<summary>Source Code</summary>

```python
def fetch(url: str, *, add_to_cache: bool = True, ignore_cache: bool = False, **add_headers) -> bytes:
    '''
        Fetch bytes from the URL
        If the URL is cached, and ignore_cache is false, then returns the cached value
        Otherwise, fetch the data and return it, as well as add it to the cache if add_to_cache is true
    '''
    h = hash(url)
    if (not ignore_cache) and (h in cache): return cache[h]
    d = request('GET', url, headers={'User-Agent': user_agent} | add_headers).data
    if add_to_cache: cache[h] = d
    return d
```
</details>

> Fetch bytes from the URL  
> If the URL is cached, and ignore_cache is false, then returns the cached value  
> Otherwise, fetch the data and return it, as well as add it to the cache if add_to_cache is true

## `flush_cache` (`RunServer.ShaeLib.net.fetch.flush_cache` | `RS.SL.net.fetch.flush_cache`)
[`_rsruntime/ShaeLib/net/fetch.py`](/_rsruntime/ShaeLib/net/fetch.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/net/fetch/RunServer.ShaeLib.net.fetch.flush_cache.md](RunServer.ShaeLib.net.fetch.flush_cache)  
> Removes a URL entry from the cache, or everything if url is None

## `foreach_chunk_fetch` (`RunServer.ShaeLib.net.fetch.foreach_chunk_fetch` | `RS.SL.net.fetch.foreach_chunk_fetch`)
[`_rsruntime/ShaeLib/net/fetch.py`](/_rsruntime/ShaeLib/net/fetch.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/net/fetch/RunServer.ShaeLib.net.fetch.foreach_chunk_fetch.md](RunServer.ShaeLib.net.fetch.foreach_chunk_fetch)  
> Calls callback for each Chunk yielded by chunk_fetch, then returns the bytes