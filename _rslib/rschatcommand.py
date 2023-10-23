#!/bin/python3

#> Imports
import inspect
import functools
# Parsing
import shlex
import re
# Types
import typing
from dataclasses import dataclass
#</Imports

#> Header >/
class ChatCommands:
    __slots__ = ('rs', 'logger', 'commands', 'registered_aliases')

    strict_cmd_name = re.compile(r'[\w\d][\w\d\-\.]*')
    lenient_cmd_name = re.compile(r'[\w\d][^\s]*')

    class ChatCommandException(Exception):
        '''
            Generic base class for ChatCommand errors
        '''
        __slots__ = ('command',)
        
        def __init__(self, cmd: 'ChatCommand', *args):
            self.command = cmd
            super().__init__(cmd, *args)
    class ChatCommandPermissionError(ChatCommandException):
        'Exception for when a user does not have the necessary permissions to run a ChatCommand'
    class ChatCommandNotFound(ChatCommandException):
        'Exception for when a ChatCommand does not exist'

    class _ChatCommand:
        '''
            Help for the command is specified by the doc-string of the target function
            The target function must have at least an argument for RunServer and for the object of the calling user
            The command-line string (A.E. "test|t [arg0:int] [arg1_1|arg1_2] {arg1:str='abc'} {arg2} {arg3:int} (varargs...)") is generated automatically using the target function's arguments
                That command-line string would be generated from a function such as: `def test(rs: 'RunServer', user: 'User', arg0: int, arg1: typing.Literal['arg1_1', 'arg1_2'], arg2: str = 'abc', arg3=None, arg4: int = None, *varargs)`
                Annotations of multiple possible literal arguments should be given as `typing.Literal[literal0, literal1, ...]`, which results in `[literal0|literal1|...]`
                Annotations and default values are detected from the function signature, as in: `arg: int = 0`, which results in `{arg:int=0}`
                    A default value of "None" indicates the argument as optional without hinting the default, as in: `arg=None`, which results in `{arg}`
                Keyword-only args and varargs are ignored
            When arguments are provided by users, they are split via shlex.split
            
        '''
        __slots__ = ('outer', 'name', 'aliases', 'function', 'permission', 'section', 'help_text', 'cmd_line', '__call__')
    
        def __init__(self, outer: 'ChatCommands', command: str | tuple[str], target: typing.Callable[['RunServer', 'User', ...], None], *, permission: typing.Literal['USER', 'ADMIN', 'SUPER', 'ROOT'] | int = 'USER', section: str = '(unset)', ):
            self.outer = outer
            if isinstance(command, str):
                self.name = command
                self.aliases = set()
            else:
                self.name = command[0]
                self.aliases = set(command[1:])
            if not self.name in self.outer.rs.C.get('chat_commands/override/unsafe_names_allowed', ()):
                
                (self.outer.strict_cmd_name if self.outer.rs.C('chat_commands/strict_names', False) else self.outer.lenient_cmd_name)
            self.function = target
            self.__call__ = staticmethod(target)
            self.permission = permission
            self.section = section
            self.help_text = self._func_to_help(target)
            self.cmd_line = self._params_to_cmdline(tuple(inspect.signature(target).parameters.values())[2:])

        @property
        def safe_name(self):
            '''
                Same as self.name, but escapes '/' by replacing it with '|'
            '''
            return self.name.replace('/', '|')

        @classmethod
        def _params_to_cmdline(cls, params: tuple):
            return ' '.join(cline for cline in (cls._arg_to_cmdline(arg) for arg in params) if cline is not None)
        @classmethod
        def _arg_to_cmdline(cls, a: inspect.Parameter) -> str | None:
            if a.kind == a.VAR_POSITIONAL: return cls._varg_to_cmdline(a.name)
            if a.kind not in {a.POSITIONAL_OR_KEYWORD, a.POSITIONAL_ONLY}: return None
            optional = a.default is not a.empty
            brackets = '{{{}{}{}}}' if optional else '[{}{}{}]'
            default = '' if (not optional) or (a.default is None) else f'={a.default}'
            annotation = '' if (a.annotation is a.empty) else f':{cls._arg_annotation_to_cmdline(a.annotation)}'
            return brackets.format(a.name, annotation, default)
        @classmethod
        def _arg_annotation_to_cmdline(cls, a: type):
            if getattr(a, '__qualname__', None) == 'Literal':
                return '|'.join(cls._arg_annotation_to_cmdline(aa) for aa in a.__args__)
            return getattr(a, '__qualname__', str(a))
        @staticmethod
        def _varg_to_cmdline(argument: str):
            return f'({argument}...)'
        @staticmethod
        def _func_to_help(function: typing.Callable):
            return inspect.getdoc(function) or '<help not supplied, perhaps contact the author of the plugin?>'

        def help(self):
            return f'{self.outer.rs.C("chat_commands/symbol", ">")}{self.name}{"" if not self.aliases else "|"+("|".join(self.aliases))} {self.cmd_line}\n{self.help_text}'

        def __repr__(self):
            return f'ChatCommand<{self.name}>[{self.target}]'
    @functools.wraps(_ChatCommand)
    def ChatCommand(self, *args, **kwargs):
        return self._ChatCommand(self, *args, **kwargs)
        
    def __call__(self, command: str | tuple[str], *, permission: typing.Literal['USER', 'ADMIN', 'SUPER', 'ROOT'] | int = 'USER', section: str = '(unset)'):
        '''
            Offers a quicker way to creat a ChatCommand class from a function and register it immediately via a decorator
        '''
        def real_wrapper(func: typing.Callable[['RunServer', 'User', ...], None]):
            self.register(self.ChatCommand(command, permission if isinstance(permission, int) else self.rs.U.PERMISSIONS[permission], section))
            return func
        return real_wrapper
    
    def __init__(self, rs: 'RunServer'):
        self.rs = rs
        self.sections = {}
        self.commands = {}
        self.registered_aliases = set()
        self.logger = self.rs.logger.getChild('ChatCommand')
        self.logger.debug(f'Initialized: {self}')
    def register(self, cmd: ChatCommand) -> bool:
        if self.rs.C.get(f'chat_commands/override/{cmd.safe_name}/mask', False):
            self.logger.error(f'Could not register ChatCommand {cmd.name}, as it is masked (see config _override_/chat_commands/{cmd.name}/mask)')
            return False
        if cmd.name in self.commands:
            self.logger.fatal(f'Could not register ChatCommand {cmd.name}, as a command already exists with this name')
            return False
        if cmd.name in self.registered_aliases:
            self.logger.fatal(f'Could not register ChatCommand {cmd.name}, as a command already exists with this alias')
            return False
        if i := self.registered_aliases.intersection(cmd.aliases):
            self.logger.fatal(f'Could not register ChatCommand {cmd.name}, as some of its aliases have aleady been registered: {i}')
            return False
        self.logger.info(f'Registered ChatCommand: {cmd.name}, under section: {cmd.section}')
        self.commands[cmd.name] = cmd
        self.registered_aliases += cmd.aliases
        return True
    def find_command(self, cmd: str) -> _ChatCommand | None:
        if cmd in self.commands: return self.commands[cmd]
        if cmd not in self.registered_aliases: return
        for c in self.commands.values():
            if cmd in c.aliases: return c
    def command(self, user: typing.Union[str, 'User'], cmd: _ChatCommand, args: tuple[str]):
        if isinstance(user, str): user = self.rs.U[user]
        if self.rs.C.get(f'chat_commands/override/{cmd.safe_name}/permission', self.rs.U.to_permission(cmd.permission)) > self.rs.U.priveledge(user):
            raise ChatCommandPermissionError(f'User {user.name} does not have permission for command "{cmd.name}"')
        cmd(self.rs, user, *args)
    def command_line(self, user: typing.Union[str, 'User'], line: str, *, perm_lvl=0):
        '''
            Parses the command line with shlex.split, finds the command, and evaluates it
            Assumes that the command line has the ChatCommand prefix removed
        '''
        if line[0] == self.rs.C(f'chat_commands/elevate_shortcut', '^'):
            if self.rs.U
            perm_lvl += 1
        l = shlex.split(line)
        cmd = self.find_command(l[0])
        if cmd is None: raise self.ChatCommandNotFound(l[0])
        self.command(l[1:])
    def help(self, target_command: _ChatCommand | None = None) -> str | None:
        if target_command is not None:
            return target_command.help()
        
