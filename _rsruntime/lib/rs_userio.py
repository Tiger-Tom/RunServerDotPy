#!/bin/python3

#> Imports
import inspect
from functools import wraps
import traceback
# Parsing
import re
import json
import shlex
# Types
import typing
from types import UnionType
from pathlib import Path
from enum import Enum, IntFlag
#</Imports

# RunServer Module
import RS
from RS import Config, LineParser, MCLang, UserManager

#> Header >/
class TellRaw(list):
    '''
        Generates a TellRaw JSON
            Praise be to https://www.minecraftjson.com !
        Who doesn't want object-oriented TellRaws???
    '''
    __slots__ = ()

    TextFormat = TF = IntFlag('TextFormat', ('BOLD', 'ITALIC', 'UNDERLINED', 'STRIKETHROUGH', 'OBFUSCATED'))
    TF.B = TF.BOLD; TF.I = TF.ITALIC; TF.U = TF.UNDERLINED; TF.S = TF.STRIKETHROUGH; TF.O = TF.OBFUSCATED
    TextFormat.NONE = TextFormat.BOLD ^ TextFormat.BOLD
    TextFormat.ALL = TextFormat.BOLD | ~TextFormat.BOLD
    TextFormat.render = lambda self: {fmt.name: True for fmt in self}

    def render(self):
        return json.dumps(self)

    TextType = Enum('TextType', {'TEXT': 'text', 'SELECTOR': 'selector', 'SCORE': 'score', 'KEYBIND': 'keybind'})
    ClickEvent = Enum('ClickEvent', {'OPEN_URL': 'open_url', 'RUN_COMMAND': 'run_command', 'SUGGEST_COMMAND': 'suggest_command', 'COPY': 'copy'})
    HoverEvent = Enum('HoverEvent', {'TEXT': 'show_text', 'ITEM': 'show_item', 'ENTITY': 'show_entity'})
    def text(self, text: str, color: str | None = None, fmt: TextFormat | dict = TextFormat.NONE, *,
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
                fmt is the formatting to apply to the text
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
        assert not ((type is self.TextType.SCORE) ^ isinstance(objective, str)) # ensure that objective is a string if, and only if, type is TextType.SCORE
        obj = {'score': {'name': text, 'objective': objective}} if (type is self.TextType.SCORE) else {type.value: text}
        # color
        if color is not None:
            assert isinstance(color, str)
            obj['color'] = color
        # fmt
        if fmt is not None:
            assert isinstance(fmt, (self.TextFormat, dict))
            obj |= (fmt.render() if isinstance(fmt, self.TextFormat) else fmt)
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
                if isinstance(hover_contents, self.__class__): obj['hoverEvent']['contents'] = hover_contents.render()
                else:
                    assert isinstance(hover_contents, tuple, list)
                    obj['hoverEvent']['contents'] = hover_contents
            else:
                assert isinstance(hover_contents, (dict, tuple, list))
                obj['hoverEvent']['contents'] = hover_contents
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

    @classmethod
    def itell(cls, user: UserManager.User, *args, **kwargs):
        '''Convenience method for `user.tell(RS.TR().text(*args, **kwargs))`'''
        user.tell(cls().text(*args, **kwargs))

TellRaw.NEWLINE = TellRaw().line_break()

class ChatCommands:
    __slots__ = ('logger', 'commands', 'command_patt', 'aliases', 'help_sections')

    class Params:
        __slots__ = ('params', 'args_line')

        # Setup config
        Config.mass_set_default('chat_commands/help/formatter/argument/brackets/',
            required         = '<{argstr}>',
            required_literal = '({argstr})',
            optional         = '[{argstr}]',
            variadic         = '[{argstr}...]',
        )
        Config.mass_set_default('chat_commands/help/formatter/argument/joiners/',
            type = ':',
            default = '=',
            literals = '|',
            union = '|',
            tokens = '',
        )
        Config.mass_set_default('chat_commands/help/formatter/special_literal/',
            true_yes = 'yes',
            false_no = 'no',
        )

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
                if p.kind == p.VAR_POSITIONAL: yield (a, *(ea for ei,ea in eargs))
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
        def render_args(cls, args: tuple[inspect.Parameter, ...]) -> str:
            return ' '.join(map(cls.render_arg, args))
        @classmethod
        def render_arg(cls, arg: inspect.Parameter) -> str:
            if (arg.kind == inspect.Parameter.KEYWORD_ONLY) or (arg.kind == arg.VAR_KEYWORD):
                raise TypeError(f'Cannot handle param kind {arg.kind} (parameter {arg})')
            braks = Config['chat_commands/help/formatter/argument/brackets/variadic']              if (arg.kind == arg.VAR_POSITIONAL) \
                    else Config['chat_commands/help/formatter/argument/brackets/optional']         if (arg.default is not arg.empty) \
                    else Config['chat_commands/help/formatter/argument/brackets/required_literal'] if (getattr(arg.annotation, '__origin__', None) is typing.Literal) \
                    else Config['chat_commands/help/formatter/argument/brackets/required']
            build = [arg.name]
            if (a := arg.annotation) is not arg.empty:
                build.append(Config['chat_commands/help/formatter/argument/joiners/type'])
                build.append(cls.render_annotation(a))
            if (arg.default is not arg.empty) and (arg.default is not None):
                build.append(Config['chat_commands/help/formatter/argument/joiners/default'])
                build.append(str(arg.default))
            return braks.format(argstr=Config['chat_commands/help/formatter/argument/joiners/tokens'].join(build))
        @classmethod
        def render_annotation(cls, ann: typing.Any) -> str:
            if ann in {None, type(None)}: return 'None'
            elif getattr(ann, '__origin__', None) is typing.Literal:
                return Config['chat_commands/help/formatter/argument/joiners/literals'].join(cls.render_annotation(aa) for aa in ann.__args__ if aa not in {None, type(None)})
            elif (getattr(ann, '__origin__', None) is typing.Union) or isinstance(ann, UnionType):
                return Config['chat_commands/help/formatter/argument/joiners/union'].join(cls.render_annotation(aa) for aa in ann.__args__ if aa not in {None, type(None)})
            elif isinstance(ann, str): return ann
            else: return ann.__qualname__

    class ChatCommand:
        '''
            Help for the command is specified by the doc-string of the target function
            The target function must have at least an argument for the object of the calling user
            The command-line string (A.E. "<arg0:int> (arg1:arg1_1|arg1_2) [arg2:str=abc] [arg3] [arg4:int] [varargs...]") is generated automatically using the target function's arguments
                That command-line string would be generated from a function such as: `def test(user: UserManager.User, arg0: int, arg1: typing.Literal['arg1_1', 'arg1_2'], arg2: str = 'abc', arg3=None, arg4: int = None, *varargs)`
                Annotations of multiple possible literal arguments should be given as `typing.Literal[literal0, literal1, ...]`, which results in `(literal0|literal1|...)`
                Annotations and default values are detected from the function signature, as in: `arg: int = 0`, which results in `[arg:int=0]`
                    A default value of "None" indicates the argument as optional without hinting the default, as in: `arg=None`, which results in `[arg]`
                Keyword-only args and varargs are ignored
            When arguments are provided by users, they are split via shlex.split
            help_section is the help section, with sub-sections delimited by '/'
        '''
        __slots__ = ('target', 'permission', 'help_section', 'params', 'aliases', '_help')

        # Setup config
        Config.mass_set_default('chat_commands/', {
            'patterns/command': r'[\w\d]+',
            'help/no_help': '<no help supplied>'
        })


        def __init__(self, target: typing.Callable[[UserManager.User, ...], None], *, permission: UserManager.Perm = UserManager.Perm.USER, help_section: str | tuple[str, ...] = ()):
            self.target = target
            assert re.fullmatch(Config['chat_commands/patterns/command'], self.name) is not None, f'Illegal command name {self.name}'
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

        def split_args(self, args: str) -> tuple[str, ...]:
            return shlex.split(args)

        @property
        def name(self) -> str: return self.target.__name__
        @property
        def help(self) -> str:
            if getattr(self, '_help', None) is not None: return self._help
            if self.target.__doc__ is None: return Config['chat_commands/help/no_help']
            doc = self.target.__doc__.lstrip('\n').rstrip()
            lspace = len(min(re.finditer(r'^([ \t]+)[^ \t\n].*$', doc, re.MULTILINE), key=lambda m: len(m.group(1))).group(1))
            self._help = ('\n'.join(
                line[lspace:]
                for line in doc.split('\n'))) or Config['chat_commands/help/no_help']
            return self._help

    # Setup config
    Config.mass_set_default('chat_commands/errors/',
        error_msg='A failure occured whilst running the command:\n {excmsg}',
        long_excmsg=True,
        reverse_frames=True,
        header_forward='Traceback (most recent call last):',
        header_reverse='Frame cascade (most recent call first):',
    )
    Config.mass_set_default('chat_commands/patterns/',
        char='>',
        line='{char}{command}{argsep}{args}',
        line_outer='^{line}$'
    )
    Config.mass_set_default('chat_commands/help/', {
        'command': 'help',
        'formatter/aliassep': '|',
    })
    Config.mass_set_default('chat_commands/help/section/',
        subcommand = 'section',
        list_item  = '- Section "{sect}"',
        hover      = 'Shift-click for more information on this section',
        top        = 'Top-level sections (shift-click a section for more help)',
        subtop     = 'Help for subsection "{sect}"',
        skip_list  = (),
    )
    Config.mass_set_default('chat_commands/help/command/',
        top        = 'Commands in section',
        list_item  = '- Command "{cmd}"',
        hover_cmd  = 'Shift-click to insert command',
        hover_help = 'Shift-click for more information on command',
    )


    HELP_SUBSECTIONS = 0
    def __init__(self):
        self.logger = RS.logger.getChild('CC')
        self.commands = {}
        self.aliases = {}
        self.help_sections = {self.HELP_SUBSECTIONS: {}}
        # Precompile command pattern
        self.command_patt = re.compile(Config['chat_commands/patterns/line_outer'].format(
            line=Config['chat_commands/patterns/line'].format(
                char=re.escape(Config['chat_commands/patterns/char']),
                command=f'(?P<cmd>{Config["chat_commands/patterns/command"]})',
                argsep=f'(?: )*',
                args='(?P<args>.*)')))
    def init2(self):
        # Register hooks
        LineParser.register_chat_callback(self.run_command)
        # Register help command
        self.register_func(self.help, {'?',})
    def __call__(self, func: typing.Callable[[UserManager.User, ...], None] | None = None, **kwargs):
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
        def wrapper(func: typing.Callable[[UserManager.User, ...], None]):
            self.register_func(func, **kwargs)
            return func
        if (func is not None):
            if not callable(func):
                raise TypeError(f'{func!r} must be a callable')
            return wrapper(func)
        return wrapper
    def __getitem__(self, cmd_or_alias: str) -> 'ChatCommands.ChatCommand':
        if (c := self.commands.get(cmd_or_alias, None)) is not None: return c
        elif (c := self.aliases.get(cmd_or_alias, None)) is not None: return c
        raise KeyError(cmd_or_alias)
    def __contains__(self, cmd_or_alias: str) -> bool:
        return (cmd_or_alias in self.commands) or (cmd_or_alias in self.aliases)

    def compose_command(self, cmd: str, args: str | None = None) -> str:
        '''Compiles cmd and args together using various configuration to compose a command string'''
        return Config['chat_commands/patterns/line'].format(
            char=Config['chat_commands/patterns/char'], command=cmd,
            argsep=('' if args is None else ' '),
            args=('' if args is None else (args if isinstance(args, str) else ' '.join(args))))
    def parse_command(self, line: str) -> tuple[bool, ChatCommand | str, str]:
        '''
            Returns:
              - a (True, ChatCommand, args) tuple if the line is a ChatCommand
              - a (False, command, args) tuple if the line matches as a ChatCommand, but the command in question hasn't been registered
              - None if the line doesn't match as a ChatCommand
        '''
        if m := self.command_patt.fullmatch(line):
            is_cmd = m.group('cmd') in self
            return (is_cmd, self[m.group('cmd')] if is_cmd else m.group('cmd'), m.group('args'))
        return None
    def run_command(self, user: UserManager.User, line: str, not_secure: bool = False):
        mat = self.parse_command(line)
        if mat is None: return # not a ChatCommand
        try:
            if not mat[0]:
                raise KeyError(f'ChatCommand {mat[1]} was not found, perhaps try {self.helpcmd_for()}?')
            mat[1](user, *mat[1].params.parse_args(*mat[1].split_args(mat[2])))
        except Exception as e:
            framet = ''.join(
                traceback.format_list(reversed(traceback.extract_tb(e.__traceback__)) if Config['chat_commands/errors/reverse_frames']
                                      else traceback.extract_tb(e.__traceback__))).rstrip()
            msg = Config['chat_commands/errors/error_msg'].format(excmsg=''.join(traceback.format_exception_only(e)).strip() if Config['chat_commands/errors/long_excmsg'] else repr(e))
            if user is user.CONSOLE:
                print(f'{msg}\n{Config[f"""chat_commands/errors/header_{"reverse" if Config["chat_commands/errors/reverse_frames"] else "forward"}"""]}\n{"".join(framet)}')
                return
            TellRaw.itell(user, msg, '#FF0000', TellRaw.TextFormat.BOLD | TellRaw.TextFormat.UNDERLINED,
                          click_event=TellRaw.ClickEvent.COPY, click_contents=framet,
                          hover_event=TellRaw.HoverEvent.TEXT, hover_contents=TellRaw().text(framet, color='#FF0000'))

    def register_func(self, func: typing.Callable[[UserManager.User, ...], None], aliases: set = set(), *, permission: UserManager.Perm = UserManager.Perm.USER, help_section: str | tuple[str, ...] = ()) -> 'ChatCommands.ChatCommand':
        cc = self.ChatCommand(func, permission=permission, help_section=help_section)
        self.register(cc, aliases)
        return cc
    def register(self, cmd: 'ChatCommands.ChatCommand', aliases: set = set()) -> 'ChatCommands.ChatCommand':
        if cmd.name in self.commands:
            raise ValueError(f'Command name {cmd.name} is already taken')
        if cmd.name in self.aliases:
            raise ValueError(f'Command name {cmd.name} is already taken as an alias')
        self.commands[cmd.name] = cmd
        for a in aliases:
            if a in self.commands:
                self.logger.error(f'Cannot register alias {a} -> {cmd.name} as it is already taken by {self.commands[a].name}')
                continue
            if a in self.aliases:
                self.logger.error(f'Cannot register alias {a} -> {cmd.name} as it is already taken by {self.aliases[a].name} (alias)')
                continue
            self.logger.info(f'Registered alias: {a} -> {cmd.name}')
            self.aliases[a] = cmd
            cmd.aliases.add(a)
        self._register_helpsect(cmd.help_section, cmd)
        self.logger.infop(f'Registered command {cmd.name}{" <- " if cmd.aliases else ""}{" | ".join(cmd.aliases)}')
        return cmd

    def _register_helpsect(self, section: tuple[str, ...], cmd: 'ChatCommands.ChatCommand'):
        self._get_helpsubsect(self.help_sections, section, True)[cmd.name] = cmd
    def _get_helpsubsect(self, container: dict, section: tuple[str, ...], create: bool) -> dict | None:
        if not len(section): return container
        elif section[0] not in container[self.HELP_SUBSECTIONS]:
            if not create: return None
            container[self.HELP_SUBSECTIONS][section[0]] = {self.HELP_SUBSECTIONS: {}}
        return self._get_helpsubsect(container[self.HELP_SUBSECTIONS][section[0]], section[1:], create)
    def help(self, user: UserManager.User, on: str | typing.Literal[Config['chat_commands/help/section/subcommand']] | None = None, section: None | str = None, force_console: bool | None = None):
        '''Docstring supplied later'''
        is_console = (user == UserManager.CONSOLE) if (force_console is None) else force_console
        # No-arg mode
        if on is None:
            # top-level section
            if is_console:
                for sect in sorted(self.help_sections[self.HELP_SUBSECTIONS].keys(), key=str):
                    if sect is self.HELP_SUBSECTIONS: continue
                    print(f'- {sect}')
                return
            tr = TellRaw().text(Config['chat_commands/help/section/top'], fmt=TellRaw.TF.BOLD)
            for sect in sorted(self.help_sections[self.HELP_SUBSECTIONS].keys(), key=str):
                if sect is self.HELP_SUBSECTIONS: continue
                tr.line_break() \
                  .text(Config['chat_commands/help/section/list_item'].format(sect=sect), fmt=TellRaw.TF.UNDERLINED,
                        insertion=self.helpcmd_for(sect, for_section=True),
                        hover_event=TellRaw.HoverEvent.TEXT, hover_contents=Config['chat_commands/help/section/hover'])
            user.tell(tr)
            return
        # Sub-section mode
        elif on == Config['chat_commands/help/section/subcommand']:
            if section is None:
                raise TypeError('Command missing an argument <section>')
            elif (sectc := self._get_helpsubsect(self.help_sections, section.split('/'), False)) is not None:
                if is_console:
                    for sect in sorted(sectc.get(self.HELP_SUBSECTIONS, {}).keys(), key=str):
                        if sect is self.HELP_SUBSECTIONS: continue
                        print(f'- Section {sect}')
                    for cmd in sorted(sectc.keys(), key=str):
                        if cmd is self.HELP_SUBSECTIONS: continue
                        print(f'- Command {cmd}')
                    return
                tr = TellRaw()
                nn = False
                if (subsects := sorted(sect for sect in sect.get(self.HELP_SUBSECTIONS, {}).keys() if sect is not self.HELP_SUBSECTIONS)):
                    tr.text(Config['chat_commands/help/section/subtop'].format(sect=section), fmt=TellRaw.TF.BOLD)
                    for sect in subsects:
                        tr.line_break() \
                          .text(Config['chat_commands/help/section/list_item'].format(sect=sect), fmt=TellRaw.TF.UNDERLINED,
                                insertion=self.helpcmd_for('/'.join((section, sect)), for_section=True),
                                hover_event=TellRaw.HoverEvent.TEXT, hover_contents=Config['chat_commands/help/section/hover'])
                    nn = True
                if (subcmds := sorted(cmd for cmd in sect.keys() if cmd is not self.HELP_SUBSECTIONS)):
                    if nn: tr.line_break()
                    tr.text(Config['chat_commands/help/command/top'], fmt=TellRaw.TR.BOLD)
                    for cmd in subcmds:
                        tr.line_break() \
                          .text(Config['chat_commands/help/command/list_item'].format(cmd=cmd), fmt=TellRaw.TF.UNDERLINED,
                                insertion=self.helpcmd_for(cmd),
                                hover_event=TellRaw.HoverEvent.TEXT, hover_contents=Config['chat_commands/help/command/hover_help'])
                user.tell(tr)
                return
            else: raise KeyError(f'Help for section {section!r} not found')
        # Command mode
        try: cmd = self[on]
        except KeyError: raise KeyError(f'Help for command/alias "{on}" not found')
        cmdline = self.compose_command(Config['chat_commands/help/formatter/aliassep'].join((cmd.name, *cmd.aliases)), cmd.params.args_line or None)
        if is_console:
            print(cmdline)
            print(cmd.help)
        else:
            user.tell(TellRaw().text(cmdline, fmt=TellRaw.TF.UNDERLINED,
                                     insertion=self.compose_command(cmd.name),
                                     hover_event=TellRaw.HoverEvent.TEXT, hover_contents=Config['chat_commands/help/command/hover_cmd']) \
                               .line_break() \
                               .text(cmd.help, fmt=TellRaw.TF.ITALIC))
    help.__doc__ = f'''
        Shows help on commands or sections.
            If on is "{Config['chat_commands/help/section/subcommand']}", then shows help on the section specified by "section"
            If on is a command, then shows help on that command
            If on is not supplied, then shows a list of top-level sections
    '''
    def helpcmd_for(self, item: str | None = None, for_section: bool = False):
        '''Composes a help command for the item'''
        if item is None:
            assert not for_section, 'item should be None only if for_section is False'
            return self.compose_command('help')
        elif for_section:
            return self.compose_command('help', ('section', item))
        return self.compose_command('help', item)
