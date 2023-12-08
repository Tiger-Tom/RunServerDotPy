[`_rsruntime/util/fetch.py`](/_rsruntime/util/fetch.py "Source")  
[Standalone doc: parts/RunServer/Util/fetch/RunServer.Util.fetch.chunk_fetch.md](RunServer.Util.fetch.chunk_fetch.md)  
> Fetch and yield bytes from the URL in chunks of chunksize  
> Yields a Chunk object  
> If the URL is cached, and ignore_cache is false, then yields the data (as Chunk, with from_cache=True) and returns it  
> Once all data has been read and yielded, it is returned as bytes, and added to the cache if add_to_cache is true
>> Cache is not written to if CHUNK_FETCH_ABORT is used to interrupt the download