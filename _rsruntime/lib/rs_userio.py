#!/bin/python3

#> Imports
# Parsing
import re
import json
import inspect
from functools import wraps
import traceback
# Types
import time # struct_time
import dataclasses
import typing
from types import UnionType
from pathlib import Path
from enum import Enum, IntFlag, IntEnum
#</Imports

# RunServer Module
import RS
from RS import Bootstrapper, Config, MCLang, LineParser
from RS.Util import JSONBackedDict

#> Header >/
class UserManager:
    __slots__ = ('logger', 'users', 'fbd')

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

    @dataclasses.dataclass(slots=True)
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
        last_connected: time.struct_time | None = None
        last_disconnected: time.struct_time | None = None

        _no_cache: bool = False

        _console_uuid: typing.ClassVar[object] = object()

        @classmethod
        @property
        def default_perm_str(cls) -> str:
            return Config('permissions/default_level', 'USER').upper()
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
            return getattr(self, 'name', None).startswith('@')
        
        @property
        def permission(self) -> 'Perm':
            if self.is_console: return RS.UM.Perm.OWNER
            return self.perm_from_value(RS.UM.fbd(f'{self.uuid}/ChatCommand Permission Level', self.default_perm_str))
        @permission.setter
        def permission(self, val: 'Perm'):
            if self.is_console: raise AttributeError('Cannot set permission of console')
            RS.UserManager.fbd[f'{self.uuid}/ChatCommand Permission Level'] = int(val)

        def tell(self, text: typing.ForwardRef('TellRaw') | tuple[str | dict] | str):
            if not (hasattr(self, 'name') or self.is_console):
                raise TypeError(f'User {self} has no name; cannot tell')
            if isinstance(text, TellRaw): text = text.render()
            if self.is_console: print(f'CONSOLE.tell: {text if isinstance(text, str) else json.dumps(text, indent=4)}')
            else: RS.SM.write(f'tellraw {self.name} {json.dumps(text)}')

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
                   f'"{getattr(self, "name", "[NAME UNKNOWN]")}" ({user.uuid})'
        def __repr__(self):
            return '<User CONSOLE>' if self.is_console else f'<User "{getattr(self, "name", "[NAME UNKNOWN]")}" {user.uuid}>'
    CONSOLE = User(_no_cache=True, name='<CONSOLE>'); CONSOLE.uuid=User._console_uuid
    User.CONSOLE = CONSOLE

    def __init__(self):
        self.logger = RS.logger.getChild('UM')
        self.users = {}
        # FileBackedDict
        path = Path(Config('users/fbd/path', './_rsusers/'))
        path.mkdir(parents=True, exist_ok=True)
        self.fbd = JSONBackedDict(path, Config('users/fbd/sync_time', 60.0))
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
        self.fbd.sync()

class TellRaw(list):
    '''
        Generates a TellRaw JSON
            Praise be to https://www.minecraftjson.com !
        Who doesn't want object-oriented TellRaws???
    '''
    __slots__ = ()

    class TextFormat(IntFlag):
        _NONE         =     0b00000
        BOLD          = B = 0b00001 
        ITALIC        = I = 0b00010
        UNDERLINED    = U = 0b00100
        STRIKETHROUGH = S = 0b01000
        OBFUSCATED    = U = 0b10000

        def render(self): ...
            
    TextFormat = IntFlag('TextFormat', ('BOLD', 'ITALIC', 'UNDERLINE', 'STRIKETHROUGH', 'OBFUSCATE'))
    TextFormat.render = lambda self: ...
    #class TextFormat(Enum):
        #color: str | typing.Literal[False] = False
    #    def __call__(self):
    #        return {k: v for k,v in dataclasses.asdict(self).items() if v is not False}

    def render(self):
        return json.dumps(self)

    TextType = Enum('TextType', {'TEXT': 'text', 'SELECTOR': 'selector', 'SCORE': 'score', 'KEYBIND': 'keybind'})
    ClickEvent = Enum('ClickEvent', {'OPEN_URL': 'open_url', 'RUN_COMMAND': 'run_command', 'SUGGEST_COMMAND': 'suggest_command', 'COPY': 'copy'})
    HoverEvent = Enum('HoverEvent', {'TEXT': 'show_text', 'ITEM': 'show_item', 'ENTITY': 'show_entity'})
    def text(self, text: str, fmt: TextFormat | dict = TextFormat, *,
             insertion: str | None = None,
             type: TextType = TextType.TEXT, objective: None | str = None,
             click_event: ClickEvent | None = None, click_contents: None | str = None,
             hover_event: HoverEvent | None = None, hover_contents: None | typing.Union['TellRaw', tuple] | typing.Union[dict, tuple] | typing.Union[dict, tuple] = None):
        '''
            Appends a tellraw text to self
                text is the text to show unless type is:
                    SELECTOR, in which case text is the selector type
                    SCORE, in which case text is the name of the player
                    KEYBIND, in which case text is the ID of the keybind
                fmt is the format to formatting to apply to the text
                insertion is text that is entered into the user's chat-box when the text is shift-clicked
                type should be self-explanatory
                objective is None unless type is SCORE, in which case objective is the scoreboard objective
                click_event is either a ClickEvent or None for nothing
                    click_contents is the text to use for the click_event (the URL to open, text to copy, etc.)
                hover_event is either a HoverEvent or None for nothing
                    hover_contents is the data to use for the hover_event (the entity to display, the TellRaw to show [as text])
        '''
        # type, text, objective
        assert isinstance(type, self.TextType)
        assert isinstance(text, str)
        assert not ((type is self.TextType.SCORE) ^ isinstance(objective, str)) # ensure that objective is a string if type is TextType.SCORE
        obj = {'score': {'name': text, 'objective': objective}} if (type is self.TextType.SCORE) else {type.value: text}
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
            assert isinstance(click_event, self.ClickEvent)
            assert isinstance(click_contents, str)
            obj['clickEvent'] = {'action': click_event.value, 'value': click_contents}
        # hover_event, hover_contents
        if hover_event is not None:
            assert isinstance(hover_event, self.HoverEvent)
            obj['hoverEvent'] = {'action': hover_event.value}
            if hover_event is self.HoverEvent.TEXT:
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
        for _ in range(count): self.append(r'\n')
        return self

    def ijoin(self, tellraws: tuple[typing.Self | str | dict]) -> typing.Generator[[typing.Self], None, None]:
        for i,tr in enumerate(tellraws):
            yield tr
            if i < len(tellraws)-1:
                yield self
    def join(self, tellraws: tuple[typing.Self | str | dict]) -> typing.Self:
        return self.__class__(self.ijoin(tellraws))
    __mmul__ = join
    
TellRaw.NEWLINE = TellRaw().line_break()
    
class ChatCommands:
    __slots__ = ('logger', 'commands', 'aliases', 'help_sections')

    class Params:
        __slots__ = ('params', 'args_line')
        def __init__(self, func: typing.Callable):
            self.params = tuple(inspect.signature(func).parameters.values())[1:]
            self.args_line = self.render_args(self.params)
        def parse_args(self, *args) -> typing.Generator[typing.Any, None, None]:
            eargs = enumerate(args)
            prms = iter(self.params)
            for i,a in eargs:
                try: p = next(prms)
                except StopIteration:
                    raise TypeError(f'Too many arguments, expected at most {len(self.params)}')
                if p.kind == p.VAR_POSITIONAL: yield (a, *(a for ei,ea in eargs))
                elif p.annotation is p.empty: yield a
                elif getattr(p.annotation, '__origin__', None) is typing.Literal:
                    if a not in p.annotation.__args__:
                        raise ValueError(f'Expected one of {p.annotation.__args__}, not {a}')
                    yield a
                elif isinstance(p.annotation, type): yield p.annotation(a)
                else: yield a
            for p in prms:
                if p.kind == p.VAR_POSITIONAL: yield ()
                elif p.default is p.empty:
                    raise TypeError(f'Not enough arguments, expected at least {len(tuple(p for p in self.params if p.default is p.empty))-1}')
                else: yield p.default

        @classmethod
        def render_args(cls, args: tuple[inspect.Parameter]) -> str:
            return Config('chat_commands/arguments/argsep', ' ').join(map(cls.render_arg, args))

        @classmethod
        def render_arg(cls, arg: inspect.Parameter) -> str:
            if (arg.kind == inspect.Parameter.KEYWORD_ONLY) or (arg.kind == arg.VAR_KEYWORD):
                raise TypeError(f'Cannot handle param kind {arg.kind} (parameter {arg})')
            braks = Config('chat_commands/help/formatter/argument/brackets/variadic', '[{argstr}...]')           if (arg.kind == arg.VAR_POSITIONAL) \
                    else Config('chat_commands/help/formatter/argument/brackets/optional', '[{argstr}]')         if (arg.default is not arg.empty) \
                    else Config('chat_commands/help/formatter/argument/brackets/required_literal', '({argstr})') if (getattr(arg.annotation, '__origin__', None) is typing.Literal) \
                    else Config('chat_commands/help/formatter/argument/brackets/required', '<{argstr}>')
            build = [arg.name]
            if (a := arg.annotation) is not arg.empty:
                build.append(Config('chat_commands/help/formatter/argument/joiners/type', ':'))
                build.append(cls.render_annotation(a))
            if (arg.default is not arg.empty) and (arg.default is not None):
                build.append(Config('chat_commands/help/formatter/argument/joiners/default', '='))
                build.append(str(arg.default))
            return braks.format(argstr=Config('chat_commands/help/formatter/argument/joiners/tokens', '').join(build))
        @classmethod
        def render_annotation(cls, ann: typing.Any) -> str:
            if ann in {None, type(None)}: return 'None'
            elif getattr(ann, '__origin__', None) is typing.Literal:
                return Config('chat_commands/help/formatter/argument/joiners/literals', '|').join(cls.render_annotation(aa) for aa in ann.__args__ if aa not in {None, type(None)})
            elif (getattr(ann, '__origin__', None) is typing.Union) or isinstance(ann, UnionType):
                return Config('chat_commands/help/formatter/argument/joiners/union', '|').join(cls.render_annotation(aa) for aa in ann.__args__ if aa not in {None, type(None)})
            elif isinstance(ann, str): return ann
            else: return ann.__qualname__
            
    
    class ChatCommand:
        '''
            Help for the command is specified by the doc-string of the target function
            The target function must have at least an argument for the object of the calling user
            The command-line string (A.E. "<arg0:int> (arg1:arg1_1|arg1_2) [arg2:str=abc] [arg3] [arg4:int] [varargs...]") is generated automatically using the target function's arguments
                That command-line string would be generated from a function such as: `def test(user: 'User', arg0: int, arg1: typing.Literal['arg1_1', 'arg1_2'], arg2: str = 'abc', arg3=None, arg4: int = None, *varargs)`
                Annotations of multiple possible literal arguments should be given as `typing.Literal[literal0, literal1, ...]`, which results in `(literal0|literal1|...)`
                Annotations and default values are detected from the function signature, as in: `arg: int = 0`, which results in `[arg:int=0]`
                    A default value of "None" indicates the argument as optional without hinting the default, as in: `arg=None`, which results in `[arg]`
                Keyword-only args and varargs are ignored
            When arguments are provided by users, they are split via shlex.split
            help_section is the help section, with sub-sections delimited by '/'
        '''
        __slots__ = ('target', 'permission', 'help_section', 'params', 'aliases', '_help')

        def __init__(self, target: typing.Callable[['User', ...], None], *, permission: UserManager.Perm = UserManager.Perm.USER, help_section: str | tuple[str] = ()):
            self.target = target
            assert re.fullmatch(Config('chat_commands/patterns/command', r'[\w\d]+'), self.name) is not None, f'Illegal command name {self.name}'
            self.permission = permission
            self.help_section = help_section.split(self.HELP_SUBSECTIONS) if isinstance(help_section, str) else help_section
            self.params = RS.CC.Params(target)
            self.aliases = set()
        def __call__(self, user: UserManager.User, *args):
            # Validate permissions
            if user.permission > self.permission:
                raise PermissionError(f'{user} not allowed to run ChatCommand, insufficent permission: have {user.permission.name}, need {self.permission.name}')
            # Validate arguments and call command
            self.target(user, *self.params.parse_args(*args))

        @property
        def name(self) -> str: return self.target.__name__
        @property
        def help(self) -> str:
            if getattr(self, '_help', None) is not None: return self._help
            doc = self.target.__doc__.lstrip('\n').rstrip()
            lspace = len(min(re.finditer(r'^([ \t]+)[^ \t\n].*$', doc, re.MULTILINE), key=lambda m: len(m.group(1))).group(1))
            self._help = ('\n'.join(
                line[lspace:]
                for line in doc.split('\n'))) or Config('chat_commands/help/no_help', '<no help supplied>')
            return self._help

    HELP_SUBSECTIONS = 0
    def __init__(self):
        self.logger = RS.logger.getChild('CC')
        self.commands = {}
        self.aliases = {}
        self.help_sections = {self.HELP_SUBSECTIONS: {}}
        # Register hooks
        LineParser.register_chat_callback(self.run_command)
    def __call__(self, func: typing.Callable[['User', ...], None] | None = None, **kwargs):
        '''
            Decorator to use register_func
            Can be used as a decorator in two ways:
              - No-arguments mode
                @ChatCommands
                def command(user: UserManager.User, ...): ...
              - With arguments:
                @ChatCommands(aliases={'cmd', 'c'}, permission=UserManager.Perm.ADMIN, help_section=('help section',))
                def command(user: UserManager.User, ...): ...
        '''
        def wrapper(func: typing.Callable[['User', ...], None]):
            self.register_func(func, **kwargs)
            return func
        if (func is not None):
            if not callable(func):
                raise TypeError(f'{func!r} must be a callable')
            return wrapper(func)
        return wrapper
    def __getitem__(self, cmd_or_alias: str) -> ChatCommand:
        if (c := self.commands.get(cmd_or_alias, None)) is not None: return c
        elif (c := self.aliases.get(cmd_or_alias, None)) is not None: return c
        raise KeyError(cmd_or_alias)

    def run_command(self, user: UserManager.User, line: str, not_secure: bool):
        try:
            ...
        except Exception as e:
            if user is user.CONSOLE:
                print(f'Failure whilst running command {line!r}:\n{"".join(traceback.format_exception(e))}')
                return
            exc = ''.join(traceback.format_exception(e))
            user.tell(TellRaw.text(f'A failure occured whilst running command {line!r}:', TellRaw.TextFormat(color='#FF0000')).line_break() \
                             .text(repr(e), TellRaw.TextFormat(color='#FF0000')).line_break() \
                             .text('Click to copy full error message', red,
                                   click_event=TellRaw.ClickEvent.COPY, click_contents=exc,
                                   hover_event=TellRaw.HoverEvent.TEXT, hover_contents=TellRaw().text(exc, TellRaw.TextFormat(color='#FF0000', underlined=True))))
    
    def register_func(self, func: typing.Callable[['User', ...], None], aliases: set = set(), *, permission: UserManager.Perm = UserManager.Perm.USER, help_section: str | tuple[str] = ()) -> ChatCommand:
        cc = self.ChatCommand(func, permission=permission, help_section=help_section)
        self.register(cc, aliases)
        return cc
    def register(self, cmd: ChatCommand, aliases: set = set()) -> bool:
        if cmd.name in self.commands:
            raise ValueError(f'Command name {cmd.name} is already taken')
        if cmd.name in self.aliases:
            raise ValueError(f'Command name {cmd.name} is already taken as an alias')
        self.commands[cmd.name] = cmd
        self.logger.infop(f'Registered {cmd.name}')
        for a in aliases:
            if a in self.commands:
                self.logger.error(f'Cannot register alias {a} -> {cmd.name} as it is already taken by {self.commands[a].name}')
                continue
            if a in self.aliases:
                self.logger.error(f'Cannot register alias {a} -> {cmd.name} as it is already taken by {self.aliases[a].name}')
                continue
            self.logger.info(f'Registered alias: {a} -> {cmd.name}')
            self.aliases[a] = cmd
            cmd.aliases.add(a)
        self._register_helpsect(cmd.help_section, cmd)

    def _register_helpsect(self, section: tuple[str], cmd: ChatCommand):
        self._get_helpsubsect(self.help_sections, section, True)[cmd.name] = cmd
    def _get_helpsubsect(self, container: dict, section: tuple[str], create: bool) -> dict | None:
        if not len(section): return container[self.HELP_SUBSECTIONS]
        elif section[0] not in container[self.HELP_SUBSECTIONS]:
            if not create: return None
            container[self.HELP_SUBSECTIONS][section[0]] = {self.HELP_SUBSECTIONS: {}}
        return self._get_helpsubsect(container[self.HELP_SUBSECTIONS][section[0]], section[1:], create)
    def _help_section(self, sections: tuple[str], to_console: bool = False) -> typing.Iterator[TellRaw | str]:
        secttexts = ((sect, Config('chat_commands/help/section/list_item', '- Section "{sect}"').format(sect=sect)) for sect in sections if sect is not self.HELP_SUBSECTIONS)
        if to_console: return (secttext[1] for secttext in secttexts if secttext not in Config('chat_commands/help/section/skip_list', ()))
        return (TellRaw().text(text,
                               insertion=Config('chat_commands/patterns/line', '{char}{command}{argsep}{args}').format(
                                   char=Config('chat_commands/patterns/char', '>'),
                                   argsep=Config('chat_commands/arguments/argsep', ' '),
                                   command=Config['chat_commands/arguments/argsep'].join((
                                       Config('chat_commands/help/command', 'help'),
                                       Config['chat_commands/help/section/subcommand'],
                                       sect)), args=''),
                               hover_event=TellRaw.HoverEvent.TEXT,
                               hover_contents=(Config('chat_commands/help/section/hover', 'Shift-click for more information on this section'),))
                for sect, text in secttexts)
    def help(self, user: UserManager.User, on: str | typing.Literal[Config('chat_commands/help/section/subcommand', 'section')] | None = None, section: None | str = None):
        '''Docstring supplied later'''
        is_console = user == UserManager.CONSOLE
        if on is None:
            Config('chat_commands/help/section/top', 'Top-level sections (shift-click a section for more help)')
            help_vals = self._help_section(sorted(self.help_sections.keys()), is_console)
        elif on == Config('chat_commands/help/section/subcommand', 'section'):
            if section is None:
                raise TypeError('Command missing an argument <section>')
            elif (sectc := self._get_helpsubsect(self.help_sections, section.split('/'), False)) is not None:
                help_vals = self._help_section(sectc.keys(), is_console)
            else: raise KeyError(f'Help for section {section} not found')
        else:
            try: cmd = self[on]
            except KeyError: raise KeyError(f'Help for command/alias {on} not found')
            help_vals = (
                    Config('chat_commands/patterns/line', '{char}{command}{args}').format(
                        char=Config['chat_commands/patterns/char'],
                        command=Config('chat_commands/help/formatter/aliassep', '|').join((cmd.name, *cmd.aliases)),
                        args=f' {cmd.params.args_line}'),
                    cmd.help,
                ) if is_console else (
                    TellRaw() \
                        .text(Config('chat_commands/patterns/line', '{char}{command}{args}').format(
                                  char=Config['chat_commands/patterns/char'],
                                  command=Config('chat_commands/help/formatter/aliassep', '|').join((cmd.name, *cmd.aliases)),
                                  args=f' {cmd.params.render_args()}'),
                              insertion=Config['chat_commands/patterns/line'].format(
                                  char=Config['chat_commands/patterns/char'],
                                  command=cmd.name, args=''),
                              hover_event=TellRaw.HoverEvent.TEXT,
                              hover_contents=(Config('chat_commands/help/command/hover', 'Shift-click to insert command'),)),
                    TellRaw.text(cmd.help))
        if is_console: print('\n'.join(help_vals))
        else: user.tell(TellRaw.NEWLINE@help_vals)
    help.__doc__ = f'''
        Shows help on commands or sections.
            If on is "{Config['chat_commands/help/section/subcommand']}", then shows help on the section specified by "section"
            If on is a command, then shows help on that command
            If on is not supplied, then shows a list of top-level sections
    '''
