#!/bin/python3

#> Imports
import re
import json
from pathlib import Path
# Types
import typing
from dataclasses import dataclass
from enum import IntEnum
from time import asctime, struct_time
#</Imports

# RunServer Module
import RS
from RS import Bootstrapper, Config, MCLang, LineParser
from RS.ShaeLib.types.fbd import JSONBackedDict

#> Header >/
class UserManager:
    __slots__ = ('logger', 'users', 'fbd')

    # Setup config
    Config.set_default('permissions/default_level', 'USER')
    Config.mass_set_default('users/fbd', path='./_rsusers/', sync_time=60.0)

    # Permissions
    ## Insert comments
    Config['permissions/levels/__comment_0'] = 'Lower permission numbers are more \'powerful\'.'
    Config['permissions/levels/__comment_1'] = 'In the config `users/[uuid]/permissions`, permissions can be given as strings (corresponding to keys in the config `permissions/levels/`), or as integers.'
    Config['permissions/levels/__comment_2'] = ' Permission level names are always given as, or converted to, uppercase'
    Config['permissions/levels/__comment_3'] = ' Permission level values are always positive integers, being silently set to 255 if they are not and cannot be converted'
    Config['permissions/levels/__comment_4'] = 'The excessive number of default permissions are more for example/documentational use than for real use, but are put in anyway.'
    Config['permissions/levels/__comment_5'] = 'The large gaps in the default permissions are to allow modification if, somehow, finer control is needed.',

    ## Insert defaults
    Config.mass_set_default('permissions/levels',
        LIMITED = 100, USER    = 80,
        KNOWN   =  60, TRUSTED = 40,
        ADMIN   =  20, OWNER   =  0,
    )

    ## Enum
    Permission = Perm = IntEnum('Perm', {
        n.upper(): (v if v >= 0 else 255) if isinstance(v, int) else (int(v) if v.isdigit() else 255) if isinstance(v, str) else 255
        for n,v in Config.items_short('permissions/levels') if not n.startswith('_')
    })

    @dataclass(slots=True)
    class User:
        name: str
        old_name: str | None = None
        uuid: str | object | None = None
        connected: bool = False
        ip: str | None = None
        port: int | None = None
        origin: str | None = None
        entity_id: int | None = None
        login_coords: tuple[float] | None = None
        last_connected: struct_time | None = None
        last_disconnected: struct_time | None = None

        _no_cache: bool = False

        _console_uuid: typing.ClassVar[object] = object()

        @classmethod
        @property
        def default_perm_str(cls) -> str:
            return Config['permissions/default_level'].upper()
        @classmethod
        def perm_from_value(cls, val: str | int | typing.ForwardRef('Permission')):
            if isinstance(val, RS.UM.Perm): return val
            if not isinstance(val, (str, int)):
                return cls.perm_from_value(cls.default_perm_str)
            try:
                if isinstance(val, int): return Perm(val.upper())
                return RS.UM.Perm[val.upper()]
            except ValueError: return cls.perm_from_value(cls.default_perm_str)

        @property
        def is_console(self) -> bool:
            return getattr(self, 'uuid', None) is self._console_uuid
        @property
        def is_selector(self) -> bool:
            return getattr(self, 'name', '').startswith('@')

        @property
        def permission(self) -> 'Perm':
            if self.is_console: return RS.UM.Perm.OWNER
            return self.perm_from_value(RS.UM.fbd(f'{self.uuid}/ChatCommand Permission Level', self.default_perm_str))
        @permission.setter
        def permission(self, val: 'Perm'):
            if self.is_console: raise AttributeError('Cannot set permission of console')
            RS.UserManager.fbd[f'{self.uuid}/ChatCommand Permission Level'] = int(val)

        def tell(self, text: typing.ForwardRef('RS.TellRaw') | tuple[str | dict] | str):
            if not (hasattr(self, 'name') or self.is_console):
                raise TypeError(f'User {self} has no name; cannot tell')
            if isinstance(text, RS.TellRaw): text = text.render()
            if self.is_console: print(f'CONSOLE.tell: {text if isinstance(text, str) else json.dumps(text, indent=4)}')
            else: RS.SM.command(f'tellraw {self.name} {json.dumps(text)}')

        store_attrs: typing.ClassVar = {
            'name': ('Username', None),
            'old_name': ('(Previously known as)', None),
            'uuid': ('UUID', None),
            'origin': ('Last login origin', None),
            'login_coords': ('Last login coordinates', None),
            'last_connected': ('Last joined time', asctime),
            'last_disconnected': ('Last left time', asctime),
        }
        def __setattr__(self, attr, val):
            if self.is_console: raise AttributeError('Cannot mutate attributes of console')
            object.__setattr__(self, attr, val)
            if attr.startswith('_') or getattr(self, '_no_cache', False) or (attr not in self.store_attrs) or (getattr(self, 'uuid', None) is None): return
            if val is None:
                RS.UserManager.fbd.set_default(f'{self.uuid}/{self.store_attrs[attr][0]}', None)
                return
            RS.UserManager.fbd[f'{self.uuid}/{self.store_attrs[attr][0]}'] = val if (self.store_attrs[attr][1] is None) else self.store_attrs[attr][1](val)
        def __call__(self, **attrs: dict[str, ...]):
            for a,v in attrs.items(): setattr(self, a, v)
            return self

        def __str__(self):
            return '<CONSOLE>' if self.is_console else \
                   self.name   if self.is_selector else \
                   f'"{getattr(self, "name", "[NAME UNKNOWN]")}" ({user.uuid})'
        def __repr__(self):
            return '<User CONSOLE>' if self.is_console else f'<User "{getattr(self, "name", "[NAME UNKNOWN]")}" {user.uuid}>'

        _at_sel_uuid: typing.ClassVar[object] = object()
        @classmethod
        def __mmull__(cls, selector: str):
            u = cls(_no_cache=True, name=f'@{selector}')
            u.uuid = cls._at_sel_uuid
            return u
    CONSOLE = User(_no_cache=True, name='<CONSOLE>'); CONSOLE.uuid=User._console_uuid; User.CONSOLE = CONSOLE

    def __init__(self):
        self.logger = RS.logger.getChild('UM')
        self.users = {}
        # FileBackedDict
        path = Path(Config['users/fbd/path'])
        path.mkdir(parents=True, exist_ok=True)
        self.fbd = JSONBackedDict(path, Config['users/fbd/sync_time'])
        Bootstrapper.register_onclose(self.close)
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
            lambda m,p,t: self[m.group('username')](ip=m.group('ip'), port=int(m.group('port')), origin=m.group('origin'), login_coords=(float(m.group('x')), float(m.group('y')), float(m.group('z')))))

    def __getitem__(self, username: str) -> User:
        if username in self.users: return self.users[username]
        else: return self.User(username)

    def close(self):
        self.fbd.stop_autosync()
        self.fbd.sync()
