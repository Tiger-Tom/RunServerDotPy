[`_rsruntime/util/locked_resource.py`](/_rsruntime/util/locked_resource.py "Source")  
[Standalone doc: parts/RunServer/Util/Locker/RunServer.Util.Locker.LockedResource.md](RunServer.Util.Locker.LockedResource.md)  
> Adds a "lock" parameter to class instances (and slots!)  
> This should be used in tandem with the @locked decorator:
>> class DemoLocked(LockedResource): # note subclass
>>> def __init__(self):
>>>> super().__init__() # note super init, needed to setup .lock  
>>>> print("initialized!")
>>> @locked # note decorator  
>>> def test_lock(self):
>>>> print("lock acquired!")