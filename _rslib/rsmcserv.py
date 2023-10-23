#!/bin/python3

# Handles language parsing and user control #

#> Imports
import logging
import functools
import time
# Types
import typing
from dataclasses import dataclass, field
from collections import defaultdict
# Files
import zipfile
from pathlib import Path
# Parsing
import re
import json
# general_helpers.py
from _rslib import general_helpers as helpers
#</Imports

#> Header >/
# CLI Arg Manager
class MCServerCLI:
    __slots__ = ('rs',)

    @property
    def jar_path(self):
        return Path(self.rs.C('minecraft/path', './minecraft'), self.rs.C('minecraft/server_jar_filename', 'server.jar'))
    #@property
    #def 
# Server Jar
class MCServerLang:
    __slots__ = ('rs', 'logger', 'jar_file', 'raw_lang', 'l', 'r')
    lang_keeps = (
        'chat.type.',
        'commands.debug.',
        'multiplayer.player.joined',
        'multiplayer.player.left',
    )

    def __init__(self, rs):
        self.rs = rs
        self.jar_path = self.SCLI.jar_file = Path(self.rs.C('minecraft/path', './minecraft') / Path(self.rs.C('minecraft/server_jar_filename', 'server.jar')))
        self.logger = rs.logger.getChild('MCLang')
        self.logger.info(f'Extracting lang from {jfile} ...')
        self.raw_lang = self.open_and_extract_lang(self.jar_file)
        self.assign_lang(self.raw_lang)
        self.logger.debug(f'Initialized: {self}')
        self.compile_expressions()
    def assign_lang(self, lang: dict[str, str]):
        self.l = {
            k:re.escape(v) for k,v in lang.items() if any(k.startswith(lk) for lk in self.lang_keeps)
        }
    def compile_expressions(self):
        self.logger.debug('Compiling regular expressions...')
        reg = lambda t: re.compile(f'^{t}$')
        self.r = {
            'chat': {
                'chat': reg(self.l['chat.type.text'].replace('%s', '(?P<user>\w+)', 1).replace('%s', '(?P<message>.*)', 1)),
            },
            'commands': {
                'debug': {
                    'already_running': reg(self.l['commands.debug.alreadyRunning']),
                    'not_running': reg(self.l['commands.debug.notRunning']),
                    'started': reg(self.l['commands.debug.started']),
                    'stopped': reg(self.l['commands.debug.stopped'].replace('%s', '(?P<seconds>[\d.]+)', 1).replace('%s', '(?P<ticks>[\d.]+)', 1).replace('%s', '(?P<tps>[\d.]+)', 1)),
                },
            },
            'multiplayer': {
                'player': {
                    'joined_renamed': reg(self.l['multiplayer.player.joined.renamed'].replace('%s', r'(?P<name>\w+)', 1).replace('%s', r'(?P<old_name>\w+)')),
                    'joined': reg(self.l['multiplayer.player.joined'].replace('%s', r'(?P<name>\w+)', 1)),
                    'left': reg(self.l['multiplayer.player.left'].replace('%s', r'(?P<name>\w+)')),
                },
                'server': {
                    'assigned_uuid': reg(r'UUID of player (?P<name>\w+) is (?P<uuid>[a-z0-6\-]+)'),
                    'assigned_entity': reg(r'(?P<name>\w+)\[\/?P<origin>(?P<ip>[\d.]+):(?P<port>[\d]+))\] logged in with entity id (?P<entity_id>[\d]+) at \((?P<coordinates>(?P<x>\-?[\d.]+), (?P<y>\-?[\d.]+), (?P<z>\-?[\d.]+)\)'),
                },
            },
            '_prefix': re.compile(r'^\[(?P<time>[0-9:]{8})\] \[(?P<thread>[^/]+)/(?P<level>[A-Z]+)\]: (?P<line>.*?)$'),
        }
    def lang_key_to_expression(self, key: str, prefix: bool = True):
        lt = lambda n,t: '({}{})'.format(f'?P<{n}>' if n else '', r'\d+?' if t == 'd' else '.+?')
        return re.sub(r'%(\d+)\$(s|d)', lambda m: lt(int(m.group(1)), m.group(2)),
               re.sub(r'%(s|d)', lambda m: lt(None, m.group(1)), self.raw_lang[key]))
    def strip_prefix(self, line: str) -> [re.Match | None, str]:
        m = self.r['_prefix'].match(line)
        return (m, line if m is None else m.group('line'))
    def _parse_line(self, line: str, patterns: dict[str, dict | re.Pattern], level=()) -> tuple[tuple[str], dict] | None:
        for k,v in patterns.items():
            if k.startswith('_'): continue
            if isinstance(v, dict):
                if (p := self._parse_line(line, v, level+(k,))) is not None: return p
                else: continue
            if (m := v.match(line)) is not None: return (level+(k,), m.groupdict())
        return None
    def parse_line(self, line: str) -> [str, [tuple[str] | None], dict | None]:
        return self._parse_line(line, self.r) or (line, None, None)
        
    @staticmethod
    def extract_jar_version(zf: zipfile.ZipFile):
        with zf.open('version.json') as f:
            return json.load(f)
    @staticmethod
    def extract_lang(zf: zipfile.ZipFile, version_id: str):
        with zipfile.ZipFile(zf.open(f'META-INF/versions/{version_id}/server-{version_id}.jar')) as zfzf:
            with zfzf.open('assets/minecraft/lang/en_us.json') as f:
                return json.load(f)
    @classmethod
    def open_and_extract_lang(cls, jfile: Path):
        with zipfile.ZipFile(jfile) as zf:
            return cls.extract_lang(zf, cls.extract_jar_version(zf)['id'])
# Server output parser
class MCServerOutputParser:
    __slots__ = ('rs', 'logger', 'waiting_buffer', 'waiting_buffer_wprefix', 'waiting_buffer_match', 'waiting_buffer_mclang', 'lang')

    def __init__(self, rs):
        self.rs = rs
        self.waiting_buffer = helpers.ReHooks(); self.waiting_buffer_wprefix = helpers.ReHooks(); self.waiting_buffer_match = helpers.GenericHooks(); self.waiting_buffer_mclang = helpers.ReHooks()
        self.lang = rs.Lang
        self.logger = rs.logger.getChild('MCParser')
        self.logger.debug(f'Initialized: {self}')
    def register_line_callback(self, patt: re.Pattern, callback: typing.Callable[[re.Match], int | None], keep_prefix = False):
        (self.waiting_buffer_wprefix if keep_prefix else self.waiting_buffer).register(patt, callback)
    def register_match_callback(self, key: tuple[str], callback: typing.Callable[[dict], int | None]):
        self.waiting_buffer_match.register(key, callback)
    def register_mclang_callback(self, key: str, vars: tuple[str], callback: typing.Callable[[dict], int | None]):
        l = self.lang.raw_lang[key]
        #self.waiting_buffer_rawlang.register(self.lang.raw_lang.key
    def handle_line(self, line: str) -> [str, [tuple[str] | None], dict | None]:
        self.waiting_buffer_wprefix.match(line)
        # Strip prefix
        pfx,line = self.lang.strip_prefix(line)
        # Execute callbacks in buffer
        self.waiting_buffer.match(line)
        # Check for matches to lang
        _,key,groups = self.lang.parse_line(line)
        self.waiting_buffer_match.exec_hooks(key, groups)
        return (line, key, groups)
# User and priveledge manager
class UserManager(dict):
    __slots__ = ('rs', 'logger', 'users', 'CONSOLE')
    actions = ('joined', 'left', 'joined_renamed', 'assigned_uuid', 'assigned_entity')
    actions_player = ('joined', 'left', 'joined_renamed')
    actions_server = ('assigned_uuid', 'assigned_entity')

    PERMISSION_USER  = 0
    PERMISSION_ADMIN = 1
    PERMISSION_SUPER = 2
    PERMISSION_ROOT  = 3

    @dataclass
    class User:
        name: str = None
        old_name: str | None = None
        uuid: str = None
        connected: bool = None
        ip: str = None
        port: int = None
        origin: str = None
        login_coords: tuple[float] = None

        last_connected: time.struct_time | None = None
        last_disconnected: time.struct_time | None = None
        
        def __call__(self, **kwargs):
            for k,v in kwargs.items(): setattr(self, k, v)
            return self
        def connect(self):
            self.connected = True
            self.last_connected = time.localtime()
        def disconnect(self):
            self.connected = False
            self.last_disconnected = time.localtime()
    
    
    def __init__(self, rs: 'RunServer'):
        self.rs = rs
        self.users = defaultdict(self.User)
        self.hooks_actions = helpers.SubHooks() # hooks for join, leave, etc.
        self.hooks_users = helpers.SubHooks() # hooks for each user
        self.CONSOLE = self[object()](name='CONSOLE')
        self.logger = rs.logger.getChild('UserMgr')
        self.register_handlers()
        self.logger.debug(f'Initialized: {self}')
    def __missing__(self, key):
        self[key] = self.User(name=key)
        return self[key]
    def register_hooks(self):
        self.logger.info(f'Creating hooks for player {actions}...')
        self.hookS_actions.add_hooks(*self.actions)
    def register_user_subhooks(self, user: str):
        if user in self.hooks_user: return
        self.logger.info(f'Creating hooks for {user} {actions}...')
        self.hooks_user.add_subhooks(user, *self.actions)
    def register_handlers(self):
        self.logger.info(f'Registering handle for player {actions}...')
        nonbasic_hooks = {
            'joined': lambda g: self.users[g.name].connect(),
            'joined_renamed': lambda g: self.users[g.name](old_name=g.old_name).connect(),
            'left': lambda g: self.users[g.name].disconnect(),
            'assigned_uuid': lambda g: self.users[g.name](uuid=g.uuid),
            'assigned_entity': lambda g: self[g.name](
                origin=g.origin, ip=g.ip, port=int(g.port),
                login_coords=(float(g.x), float(g.y), float(g.z)),
            ),
            
        }
        def basic_hook(action_name, groups):
            nonbasic_hooks[action_name](groups)
            self.register_user_subhooks(groups.name)
            self.hooks_actions.exec_hooks(action_name, groups.name, groups)
            self.hooks_users.exec_hooks(groups.name, action_name, groups)
        for a in self.actions_player:
            self.rs.Pa.register_match_callback(('multiplayer', 'player', a), functools.partial(basic_hook, (a,)))
        for a in self.actions_server:
            self.rs.Pa.register_match_callback(('multiplayer', 'server', a), functools.partial(basic_hook, (a,)))
    def register(self, trigger: typing.Union['action', 'user'], key: str, subkey: str, callback: typing.Callable[[dict], int | None]):
        if self.trigger not in {'action', 'user'}: raise NotImplementedError(f'Trigger {trigger} does not exist')
        (self.hooks_users if trigger == 'user' else self.hooks_actions).register(key, subkey, callback)
    def priveledge(self, user: str | User):
        if user == self.CONSOLE: return 255
        if isinstance(user, str): user = User[user] # user user user
        return self.C.get('users/priveledge', {}).get(self.users[user]["uuid"], self.PERMISSION_USER)
# Tellraw helper
class Tellraw(list):
    '''
        Thank you https://www.minecraftjson.com/ !
    '''
    __slots__ = ('rs', 'logger')

    @dataclass(slots=True)
    class TextFormat:
        color: str | typing.Literal[False] = False
        bold: bool = False
        italic: bool = False
        underlined: bool = False
        strikethrough: bool = False
        obfuscated: bool = False
        def to_dict(self):
            obj = {}
            for f in self.__slots__:
                if getattr(self, f) is False: continue
                obj[f] = getattr(self, f)
            return obj
    
    def __init__(self, rs):
        print(self, rs)
        self.rs = rs
        self.logger = rs.logger.getChild('Tellraw')
        self.logger.debug('Initialized')
    def __call__(self): return json.dumps(self)
    def __repr__(self):
        return f'{self.__class__.__name__}({list.__repr__(self)})'

    click_events = ('open_url', 'run_command', 'suggest_command', 'copy')
    hover_events = ('show_text', 'show_item', 'show_entity')
    def text(self, text: str, fmt: TextFormat | dict = TextFormat(), *,
             insertion: str | None = None,
             type: typing.Literal['text', 'selector', 'score'] = 'text', objective: None | str = None,
             click_event: typing.Literal[None, *click_events] = None, click_contents: None | str = None,
             hover_event: typing.Literal[None, *hover_events] = None, hover_contents: None | typing.Union[typing.ForwardRef('TellRaw') | typing.Any] | typing.Union[dict, tuple]| typing.Union[dict, tuple] = None,
             I_KNOW_WHAT_IM_DOIN: bool = False):
        '''
            If the type is "score", then "text" is the name of the player, and "objective" is the scoreboard objective
        '''
        if not I_KNOW_WHAT_IM_DOIN:
            assert type in {'text', 'selector', 'score'}
            assert isinstance(text, str)
            assert not ((type == 'score') ^ isinstance(objective, str)), 'Objective should be a string when type == \'score\'' if (type == score) else 'Objective should be unset when type != \'score\''
        if type == 'score':
            if not I_KNOW_WHAT_IM_DOIN: assert isinstance(objective, str)
            obj = {'score': {}}
        else: obj = {type: text}
        if fmt is not None:
            if not I_KNOW_WHAT_IM_DOIN: assert isinstance(fmt, (self.TextFormat, dict))
            if isinstance(fmt, self.TextFormat): obj |= fmt.to_dict()
            else: obj |= fmt
        if insertion is not None:
            if not I_KNOW_WHAT_IM_DOIN: assert isinstance(insertion, str)
            obj['insertion'] = insertion
        if click_event is not None:
            if not I_KNOW_WHAT_IM_DOIN:
                assert click_event in self.click_events
                assert isinstance(click_contents, str)
            obj['clickEvent'] = {'action': click_event, 'value': click_contents}
        if hover_event is not None:
            if not I_KNOW_WHAT_IM_DOIN: assert hover_event in self.hover_events
            obj['hoverEvent'] = {'action': hover_event}
            if hover_event == 'show_text':
                if isinstance(hover_value, self.__class__):
                    obj['hoverEvent']['contents'] = hover_value()
                else:
                    if not I_KNOW_WHAT_IM_DOIN:
                        self.logger.warning(f'It is recommended to use {self.__class__} for hover_value with hover_type of show_text')
                    obj['hoverEvent']['contents'] = hover_value
            else:
                if not I_KNOW_WHAT_IM_DOIN: assert isinstance(hover_value, (dict, tuple))
                obj['hoverEvent']['contents'] = hover_value
        self.append(obj)
        return self
    def line_break(self, count: int = 1):
        if count <= 0: raise ValueError('Count is too low')
        for _ in range(count): self.append('\n')
        return self
