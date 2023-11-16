#!/bin/python3

#> Imports
# Parsing
import re
import json
import inspect
# Types
import time # struct_time
import dataclasses
import typing
from pathlib import Path
from enum import Flag, IntEnum
#</Imports

# RunServer Module
import RS
from RS import Bootstrapper, Config, MCLang, LineParser
from RS.Util import FileBackedDict

#> Header >/
class UserManager:
    __slots__ = ('logger', 'users', 'fbd')

    # Permissions
    ## Insert comments
    Config['permissions/levels/__comments'] = ( # S+ tier JSON commenting
        ('Lower permession numbers are more \'powerful\'.',
         'In the config `users/[uuid]/permissions`, permissions can be given as strings (corresponding to keys in the config `permissions/levels/`), or as integers.'),
        ('Permission level names are always given as, or converted to, uppercase',
         'Permission level values are always positive integers, being silently set to 255 if they are not and cannot be converted'),
        ('The excessive number of permissions are more for example/documentational use than for real use, but are put in anyway.',
         'The large gaps in the default are to allow modification if, somehow, finer control is needed.'),
    )
    ## Insert defaults
    Config.mass_set_default('permissions/levels',
        LIMITED = 100, USER    = 80,
        KNOWN   =  60, TRUSTED = 40,
        ADMIN   =  20, OWNER   =  0,
    )

    ## Enum
    Permission = Perm = IntEnum('Perm', {
        n.upper(): (v if v >= 0 else 255) if isinstance(v, int) else (int(v) if v.isdigit() else 255) if isinstance(v, str) else 255
        for n,v in Config.get_item('permissions/levels', unsafe_allow_get_subkey=True).items()
        if not n.startswith('_')
    })
    
    @dataclasses.dataclass(slots=True)
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

    
        @staticmethod
        @property
        def default_perm_str(cls) -> str:
            return Config('permissions/default_level', 'USER').upper()
        @classmethod
        def perm_from_value(cls, val: str | int | typing.ForwardRef('Perm') | ...):
            if isinstance(val, Perm): return val
            if not isinstance(val, (str, int)):
                return cls.perm_from_value(cls.default_perm_str)
            try:
                if isinstance(val, int): return Perm(p)
                return Perm[p.upper()]
            except ValueError: return cls.perm_from_value(cls.default_perm_str)
        @property
        def permission(self) -> 'Perm':
            return perm_from_value(RS.UserManager.fbd(f'{self.uuid}/ChatCommand Permission Level'), self.default_perm_str)
        @permission.setter
        def permission(self, val: 'Perm'):
            RS.UserManager.fbd[f'{self.uuid}/ChatCommand Permission Level'] = int(val)

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
        self.logger = RS.logger.getChild('UM')
        self.users = {}
        # FileBackedDict
        path = Path(Config('users/fbd/path', './_rsusers/'))
        path.mkdir(parents=True, exist_ok=True)
        self.fbd = FileBackedDict(path, Config('users/fbd/sync_time', 60.0))
        Bootstrapper.register_onclose(self.close)
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

    def close(self):
        self.fbd.stop_autosync()
        self.fbd.sync_all()

class TellRaw(list):
    '''
        Generates a TellRaw JSON
            Praise be to https://www.minecraftjson.com !
        Who doesn't want object-oriented TellRaws???
    '''
    __slots__ = ()
    
    @dataclasses.dataclass(slots=True)
    class TextFormat:
        color: str | typing.Literal[False] = False
        bold: bool = False
        italic: bool = False
        underlined: bool = False
        strikethrough: bool = False
        obfuscated: bool = False
        def __call__(self):
            return {k: v for k,v in dataclasses.asdict(self).items() if v is not False}

    def render(self):
        return json.dumps(self)

    click_events = {'open_url', 'run_command', 'suggest_command', 'copy'}
    hover_events = {'show_text', 'show_item', 'show_entity'}
    text_types = {'text', 'selector', 'score', 'keybind'}
    def text(self, text: str, fmt: TextFormat | dict = TextFormat(), *,
             insertion: str | None = None,
             type: typing.Literal[*text_types] = 'text', objective: None | str = None,
             click_event: typing.Literal[None, *click_events] = None, click_contents: None | str = None,
             hover_event: typing.Literal[None, *hover_events] = None, hover_contents: None | typing.Union['TellRaw', tuple] | typing.Union[dict, tuple] | typing.Union[dict, tuple] = None):
        '''
            Appends a tellraw text to self
                text is the text to show unless type is:
                    selector, in which case text is the selector type
                    score, in which case text is the name of the player
                    keybind, in which case text is the ID of the keybind
                fmt is the format to formatting to apply to the text
                insertion is text that is entered into the user's chat-box when the text is shift-clicked
                type is one of text_types, which should be self-explanitory
                objective is None unless type is "score", in which case objective is the scoreboard objective
                click_event is one of click_events (or None for nothing), they should be self-explanatory
                    click_contents is the text to use for the click_event (the URL to open, text to copy, etc.)
                hover_event is one of hover_events (or None for nothing), they should be self-explanatory
                    hover_contents is the data to use for the hover_event (the entity to display, the TellRaw to show [as text])
        '''
        # type, text, objective
        assert type in {'text', 'selector', 'score'}
        assert isinstance(text, str)
        assert not ((type == 'score') ^ isinstance(objective, str))
        obj = {'score': {'name': text, 'objective': objective}} if (type == 'score') else {type: text}
        # fmt
        if fmt is not None:
            assert isinstance(fmt, (self.TextFormat, dict))
            if isinstance(fmt, self.TextFormat): obj |= fmt()
            else: obj |= fmt
        # insertion
        if insertion is not None:
            assert isinstance(insertion, str)
            obj['insertion'] = insertion
        # click_event, click_contents
        if click_event is not None:
            assert click_event in self.click_events
            assert isinstance(click_contents, str)
            obj['clickEvent'] = {'action': click_event, 'value': click_contents}
        # hover_event, hover_contents
        if hover_event is not None:
            assert hover_event in self.hover_events
            obj['hoverEvent'] = {'action': hover_event}
            if hover_event == 'show_text':
                if isinstance(hover_value, self.__class__): obj['hoverEvent']['contents'] = hover_value.render()
                else:
                    assert isinstance(hover_value, tuple, list)
                    obj['hoverEvent']['contents'] = hover_value
            else:
                assert isinstance(hover_value, (dict, tuple, list))
                obj['hoverEvent']['contents'] = hover_value
        # finish
        self.append(obj); return self
    def line_break(self, count: int = 1):
        '''Append n newlines to self (where n >= 0)'''
        if count < 0: raise ValueError('Cannot append a negative amount of newlines')
        for _ in range(count): self.append('\n')
        return self
    
class ChatCommands:
    __slots__ = ('logger', 'commands', 'aliases')

    class ParamParser:
        raise NotImplementedError # token-based args are more trouble than benefit
    class ParamParser__:
        def __init__(self): raise TypeError(f'{self.__class__} should not be initialized')

        ParamTok = Flag('Params', ('ParamTok', 'ERROR',
                         'OPTIONAL', 'VARIADIC',             # argument
                         'NONE', 'STRING', 'TYPE', 'UNION')) # annotation
        @classmethod
        def tokenify_args(cls, args: tuple[inspect.Parameter]) -> typing.Generator[tuple[ParamTok, tuple[str, ...]], None, None]:
            for p in args:
                argument = (ParamTok.VARIADIC,) if (p.kind == p.VAR_POSITITONAL) else (0,) if (p.default is p.empty) else (ParamTok.OPTIONAL, p.default)
                     
                annotation = (paramTok.NONE,)                if (p.annotation is p.empty)                  \
                        else (ParamTok.STRING, p.annotation) if (isinstance(p.annotation, str))            \
                        else (ParamTok.TYPE,   p.annotation) if (isinstance(p.annotation, str))            \
                        else (ParamTok.UNION,  p.__args__)   if (isinstance(p.annotation, typing.Literal)) \
                        else (ParamTok.ERROR,) # <--bad

                yield (argument[0]|annotation[0], (p.name,)+argument[1:]+annot[1:])
        #@classmethod
        #def render_annotation_part(ann: type | str | typing.Literal | typing.Any) -> str:
        #    if isinstance(ann, str): return ann
        #    if isinstance(ann, type): return ann.__qualname__
        @classmethod
        def render_token(cls, token: ParamTok, args: tuple[str, ...]):
            assert not (token & ParamTok.ERROR)
            args = iter(args)
            name = next(args)
            braks = Config('chat_commands/help/formatter/argument/brackets/optional', '[{argstr}]')    if (token & ParamTok.OPTIONAL) \
               else Config('chat_commands/help/formatter/argument/brackets/variadic', '({argstr}...)') if (token & ParamTok.VARIADIC) \
               else Config('chat_commands/help/formatter/argument/brackets/required', '{argstr}')
            build = [name]
            # annotations
            if not (token & ParamTok.NONE):
                build.append(Config('chat_commands/help/formatter/argument/joiners/type', ':'))
            if token & ParamTok.STRING: build.append(next(args))
            elif token & ParamTok.TYPE: build.append(next(args).__qualname__)
            elif token & ParamTok.UNION:
                build.append(Config('chat_commands/help/formatter/argument/joiners/union', '|').join(next(args)))
            # default
            if token & ParamTok.OPTIONAL:
                if (n := next(args)) is not None:
                    build.append(Config('chat_commands/help/formatter/argument/joiners/default', '='))
                    build.append(repr(n))
        @classmethod
        def render_args(cls, args: tuple[inspect.Parameter]) -> str:
            return Config('chat_commands/help/formatter/argument/joiners/argsep', ' ').join(map(cls.render_token, cls.tokenify_args(args)))
    
    class ChatCommand:
        '''
            Help for the command is specified by the doc-string of the target function
            The target function must have at least an argument for the object of the calling user
            The command-line string (A.E. "test|t [arg0:int] [arg1_1|arg1_2] {arg1:str='abc'} {arg2} {arg3:int} (varargs...)") is generated automatically using the target function's arguments
                That command-line string would be generated from a function such as: `def test(user: 'User', arg0: int, arg1: typing.Literal['arg1_1', 'arg1_2'], arg2: str = 'abc', arg3=None, arg4: int = None, *varargs)`
                Annotations of multiple possible literal arguments should be given as `typing.Literal[literal0, literal1, ...]`, which results in `[literal0|literal1|...]`
                Annotations and default values are detected from the function signature, as in: `arg: int = 0`, which results in `{arg:int=0}`
                    A default value of "None" indicates the argument as optional without hinting the default, as in: `arg=None`, which results in `{arg}`
                Keyword-only args and varargs are ignored
            When arguments are provided by users, they are split via shlex.split
        '''
        __slots__ = ('target', 'permission', 'help_section')        

        def __init__(self, target: typing.Callable[['User', ...], None], permission: UserManager.Perm, help_section: str | None = None):
            self.target = self.__call__ = target
            self.permission = permission
            self.help_section = help_section
            
        def __call__(self, user: UserManager.User, *args):
            # Validate permissions
            if user.permission > self.permission:
                raise PermissionError('{user} not allowed to run ChatCommand, insufficent permission: have {user.permission.name), need {self.permission.name}')
            # Validate arguments
            ...
            # Call command
            #RS.CC

    def __call__(self, func: typing.Callable):
        ...

    def __init__(self):
        self.logger = RS.logger.getChild('CC')
        self.commands = {}
        self.aliases = {}
    def register(self, cmd: 'ChatCommand') -> bool:
        ...
