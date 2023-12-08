# `UserManager` (`RunServer.UserManager` | `RS.UM`)
[`_rsruntime/lib/rs_usermgr.py`](/_rsruntime/lib/rs_usermgr.py "Source")  
[Standalone doc: parts/RunServer/RunServer.UserManager.md](RunServer.UserManager.md)  

## close()
```python
def close()
```

[`_rsruntime/lib/rs_usermgr.py@169:171`](/_rsruntime/lib/rs_usermgr.py#L169)

<details>
<summary>Source Code</summary>

```python
def close(self):
    self.fbd.stop_autosync()
    self.fbd.sync()
```
</details>

> <no doc>

## init2()
```python
def init2()
```

[`_rsruntime/lib/rs_usermgr.py@147:163`](/_rsruntime/lib/rs_usermgr.py#L147)

<details>
<summary>Source Code</summary>

```python
def init2(self):
    # Register hooks
    LineParser.register_callback( # player joins
        MCLang.lang_to_pattern(MCLang.lang['multiplayer.player.joined'], ('username',)),
        lambda m,p,t: self[m.group('username')](connected=True, last_connected=t))
    LineParser.register_callback( # player joins, has changed name
        MCLang.lang_to_pattern(MCLang.lang['multiplayer.player.joined.renamed'], ('username', 'old_name')),
        lambda m,p,t: self[m.group('username')](connected=True, old_name=m.group('old_name'), last_connected=t))
    LineParser.register_callback( # player leaves
        MCLang.lang_to_pattern(MCLang.lang['multiplayer.player.left'], ('username',)),
        lambda m,p,t: self[m.group('username')](connected=False, last_disconnected=t))
    LineParser.register_callback( # player is assigned UUID
        re.compile(r'^UUID of player (?P<username>\w+) is (?P<uuid>[a-z0-6\-]+)$'),
        lambda m,p,t: self[m.group('username')](uuid=m.group('uuid')))
    LineParser.register_callback( # player is assigned entity ID and origin
        re.compile(r'^(?P<username>\w+)\[\/(?P<origin>(?P<ip>[\d.]+):(?P<port>[\d]+))\] logged in with entity id (?P<entity_id>[\d]+) at \((?P<x>\-?[\d.]+), (?P<y>\-?[\d.]+), (?P<z>\-?[\d.]+)\)$'),
        lambda p,t,m: self[m.group('username')](ip=m.group('ip'), port=int(m.group('port')), origin=m.group('origin'), login_coords=(float(m.group('x')), float(m.group('y')), float(m.group('z')))))
```
</details>

> <no doc>