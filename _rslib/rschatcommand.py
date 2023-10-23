#!/bin/python3

#> Imports
import inspect
# Types
import typing
from dataclasses import dataclass
#</Imports

#> Header >/
class ChatCommands:
    __slots__ = ('rs', 'logger', 'commands', 'registered_aliases')

    class ChatCommand:
        '''
            Help for the command is specified by the doc-string of the target function
            The command-line string (A.E. "test|t [arg0:int] [arg1_1|arg1_2] {arg1:str='abc'} {arg2} {arg3:int} (varargs...)") is generated automatically using the target function's arguments
                That command-line string would be generated from a function such as: `def test(arg0: int, arg1: typing.Literal['arg1_1', 'arg1_2'], arg2: str = 'abc', arg3=None, arg4: int = None, *varargs)`
                Annotations of multiple possible literal arguments should be given as `typing.Literal[literal0, literal1, ...]`, which results in `[literal0|literal1|...]`
                Annotations and default values are detected from the function signature, as in: `arg: int = 0`, which results in `{arg:int=0}`
                    A default value of "None" indicates the argument as optional without hinting the default, as in: `arg=None`, which results in `{arg}`
                Keyword-only args and varargs are ignored
        '''
        __slots__ = ('name', 'aliases', 'function', 'permission', 'section', 'help_text', 'cmd_line')
    
        def __init__(self, command: str | tuple[str], target: typing.Callable, permission: typing.Literal['USER', 'ADMIN', 'SUPER', 'ROOT'] | int, section: str = '(unset)'):
            if isinstance(command, str):
                self.name = command
                self.aliases = set()
            else:
                self.name = command[0]
                self.aliases = set(command[1:])
            self.function = target
            self.permission = permission
            self.section = section
            self.help_text = self._func_to_help(target)
            self.cmd_line = self._sig_to_cmdline(inspect.signature(target))

        @classmethod
        def _sig_to_cmdline(cls, sig: inspect.Signature):
            return ' '.join(cline for cline in (cls._arg_to_cmdline(arg) for arg in sig.parameters.values()) if cline is not None)
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

        def help(self, symbol: str):
            return f'{symbol}{self.name}{"" if not self.aliases else "|"+("|".join(self.aliases))} {self.cmd_line}\n{self.help_text}'
    def __call__(self, command: str | tuple[str], permission: typing.Literal['USER', 'ADMIN', 'SUPER', 'ROOT'] | int, section: str = '(unset)'):
        '''
            Offers a quicker way to creat a ChatCommand class from a function and register it immediately via a decorator
        '''
        def real_wrapper(func: typing.Callable):
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
    def find_command(self, cmd: str) -> ChatCommand | None:
        if cmd in self.commands: return self.commands[cmd]
        if cmd not in self.registered_aliases: return
        for c in self.commands.values():
            if cmd in c.aliases: return c
    #def command(self, user: typing.Union[str, 'CONSOLE'], cmd: ChatCommand):
    #    self.rs.U.self.rs.U.priveledge(user)
    def help(self, target_command: ChatCommand | None = None) -> str | None:
        symbol = self.rs.C('chat_commands/symbol', '>')
        if target_command is not None:
            return target_command.help(symbol)
        
