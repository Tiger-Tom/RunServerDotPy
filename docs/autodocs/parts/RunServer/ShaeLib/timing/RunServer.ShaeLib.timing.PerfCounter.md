[`_rsruntime/ShaeLib/timing/perfcounter.py`](/_rsruntime/ShaeLib/timing/perfcounter.py "Source")  
[Standalone doc: parts/RunServer/ShaeLib/timing/RunServer.ShaeLib.timing.PerfCounter.md](RunServer.ShaeLib.timing.PerfCounter)  
> Provides an object-oriented (because why not) way to use (and format) time.perf_counter

## fromhex(...)
```python
@classmethod
def fromhex(string)
```
> Create a floating-point number from a hexadecimal string.  
>   
> >>> float.fromhex('0x1.ffffp10')  
> 2047.984375  
> >>> float.fromhex('-0x1p-1074')  
> -5e-324