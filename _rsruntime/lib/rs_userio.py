#!/bin/python3

#> Imports
# Parsing
import re
# Types
import time # struct_time
from dataclasses import dataclass
import typing
from pathlib import Path
#</Imports

# RunServer Module
import RS
from RS import Config, MCLang, LineParser
from RS.Types import FileBackedDict

#> Header >/
class UserManager:
    __slots__ = ('logger', 'users', 'fbd')

    @dataclass(slots=True)
    class User:
        name: str
        old_name: str | None = None
        uuid: str | None = None
        connected: bool = False
        ip: str | None = None
        port: int | None = None
        origin: str | None = None
        entity_id: int | None = None
        login_coords: tuple[float] | None = None
        last_connected: time.struct_time | None = None
        last_disconnected: time.struct_time | None = None

        @property
        def permission(self) -> int:
            return RS.UserManager.fbd(f'{self.uuid}/ChatCommand Permission Level', 0)
        @permission.setter
        def permission(self, val: int):
            return RS.UserManager.fbd[f'{self.uuid}/ChatCommand Permission Level'] = val

        store_attrs: typing.ClassVar = {
            'name': ('Username', None),
            'old_name': ('(Previously known as)', None),
            'uuid': ('UUID', None),
            'origin': ('Last login origin', None),
            'login_coords': ('Last login coordinates', None),
            'last_connected': ('Last joined time', time.asctime),
            'last_disconnected': ('Last left time', time.asctime),
        }
        
        def __setattr__(self, attr, val):
            object.__setattr__(self, attr, val)
            if attr not in self.store_attrs: return
            if getattr(self, 'uuid', None) is None: return
            if val is None:
                RS.UserManager.fbd.set_default(f'{self.uuid}/{self.store_attrs[attr][0]}', None)
                return
            RS.UserManager.fbd[f'{self.uuid}/{self.store_attrs[attr][0]}'] = val if (self.store_attrs[attr][1] is None) else self.store_attrs[attr][1](val)
            print(f'set {self.uuid}/{self.store_attrs[attr][0]} to {val if (self.store_attrs[attr][1] is None) else self.store_attrs[attr][1](val)}')
        def __call__(self, **attrs: dict[str, ...]):
            for a,v in attrs.items(): setattr(self, a, v)
            return self

    def __init__(self):
        self.logger = RS.logger.getChild('UserManager')
        self.users = {}
        # FileBackedDict
        path = Path(Config('users/fbd/path', './_rsusers/'))
        path.mkdir(parents=True, exist_ok=True)
        self.fbd = FileBackedDict(path, Config('users/fbd/sync_time', 60.0))
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
        
    def __getitem__(self, username: str) -> User:
        if username in self.users: return self.users[username]
        else: return self.User(username)

class TellRaw:
    ...

class ChatCommands:
    ...
    class ChatCommand:
        ...
