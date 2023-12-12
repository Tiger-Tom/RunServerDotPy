#!/bin/python3

#> Imports
import typing
import functools
#</Imports

# RunServer module
import RS

#> Header >/
# Internal utils
def _user_from_(user: RS.UM.User | str):
    if isinstance(user, RS.UM.User): return user
    return RS.UM.User[user]

# Command writing
def command(*commands: str) -> None | typing.Any:
    '''
        Writes a command to the server
            Equivelant to RS.SM.command(*commands)
    '''
    return RS.SM.command(*commands)
## Chat writing
@functools.wraps(RS.UM.User, ('__annotations__', '__type_params__'))
def tellraw(self, user: RS.UM.User | str, *args, **kwargs):
    '''
        Tells a user something. See RS.TR.text for more advanced usage
            This function uses RS.TR.itell
    '''
    RS.TR.itell(_user_from_(user), *args, **kwargs)
def tell(user: RS.UM.User | str, text: str):
    if '\n' in text:
        raise ValueError('Cannot tell with newlines, use tellraw instead')
    command(f'tell {user.name} {text}')
def say(text: str):
    if '\n' in text:
        raise ValueError('Cannot say with newlines, use tellraw with @a')
    command(f'say {text}')

# LineParser interaction
def inject_line(line: str):
    '''
        Injects a line into LineParser, as if it was read from the ServerManager
            Equivelant to RS.LP.handle_line(line)
    '''
    RS.LP.handle_line(line)
def listen_chat(callback: typing.Callable[[RS.UM.User, str, bool], None]):
    '''
        Registers a callback for when LineParser reads a chat message
            The callback should have three arguments:
            - the user (RS.UM.User object)
            - the line (str)
            - if the message was "not secure" (bool)
    '''
    RS.LP.register_chat_callback(callback)


# All
__all__ = tuple(n for n in dir() if callable(globals()[n]) and (not n.startswith('_')) and (n != 'RS'))
