[Standalone doc: parts/RunServer/Util/fetch/RunServer.Util.fetch.fetch_nocache.md](RunServer.Util.fetch.fetch_nocache.md)  
> partial(func, *args, **keywords) - new function with partial application  
> of the given arguments and keywords.

## fetch(...)
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

[`_rsruntime/util/fetch.py@24:34`](/_rsruntime/util/fetch.py#L24)

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