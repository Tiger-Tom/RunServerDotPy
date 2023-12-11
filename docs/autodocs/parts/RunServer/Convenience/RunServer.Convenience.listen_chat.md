[`_rsruntime/lib/rs_convenience.py`](/_rsruntime/lib/rs_convenience.py "Source")  
[Standalone doc: parts/RunServer/Convenience/RunServer.Convenience.listen_chat.md](RunServer.Convenience.listen_chat)  
> Registers a callback for when LineParser reads a chat message
>> The callback should have three arguments:  
>> - the user (RS.UM.User object)  
>> - the line (str)  
>> - if the message was "not secure" (bool)