#!/bin/python3

#> Imports
import time
import typing
import RS
from RS import Flags, MinecraftManager, TellRaw, UserManager
#</Imports

#> Header >/
this.c.mass_set_default('commands/', {
    'stop/permission': 'ADMIN',
    'restart/permission': 'TRUSTED',
    'version/permission': 'OWNER',
})
this.c.set_default('functions/shutdown/default_delay', 5)
this.c.mass_set_default('functions/shutdown/warning/',
    message     = 'SERVER GOING DOWN {for_}{timefmt}',
    in_secs     = 'IN {secs} SECONDS',
    in_sec      = 'IN 1 SECOND',
    now         = 'NOW!',
    for_stop    = '',
    for_restart = 'FOR A RESTART ',
)
def _shutdown(tell: RS.UM.User, for_: str, delay: int):
    if not RS.SM.cap_stoppable:
        raise NotImplementedError(f'Current server manager implementation ({RS.SM.name}) cannot be stopped')
    for s in range(delay, 0, -1):
        one = s == 1
    for s in range(delay, 0, -1):
        one = s == 1
        _.tellraw(tell, this.c['shutdown/warning/message'].format(for_=for_, timefmt=this.c['shutdown/warning/in_sec{"" if one else "s"}'].format(s)),
                  '#FF0000', TellRaw.TF.BOLD if one else TellRaw.TF.NONE)
        time.sleep(1)
    _.tellraw(tell,
              this.c['shutdown/warning/message'].format(for_=for_, timefmt=this.c['/shutdown/warning/now']),
              '#FF0000', TellRaw.TF.BOLD|TellRaw.TF.UNDERLINED)
    time.sleep(1)

@RS.CC(permission=UserManager.User.perm_from_value(this.c['commands/stop/permission']), help_section=('Server Control',))
def stop(user: RS.UM.User, delay: int = this.c['functions/shutdown/default_delay'], announce: bool = True):
    if not RS.SM.cap_stoppable:
        raise NotImplementedError(f'Current server manager implementation ({RS.SM.name}) cannot be stopped')
    Flags.force_no_restart = True
    _shutdown((RS.UM.User@'a' if announce else user), this.c['shutdown/warning/for_stop'], delay)
@RS.CC(permission=UserManager.User.perm_from_value(this.c('commands/restart/permission')), help_section=('Server Control',))
def restart(user: RS.UM.User, delay: int = this.c['functions/shutdown/default_delay'], announce: bool = True):
    if not RS.SM.cap_restartable:
        raise NotImplementedError(f'Current server manager implementation ({RS.SM.name}) cannot be restarted')
    Flags.force_restart = True
    _shutdown((RS.UM.User@'a' if announce else user), this.c['shutdown/warning/for_restart'], delay)

@RS.CC(permission=UserManager.User.perm_from_value(this.c['commands/version/permission']), help_section=('Server Control',))
def version(user: RS.UM.User, mode: typing.Literal['list', 'query', 'set', 'refresh'], target: str | None = None):
    '''
        mode 'list': Lists available version IDs (least to most recent) of a specific type (run without `target` to see types)
        mode 'query': Prints the current version
        mode 'set': Downloads and installs the version with ID `target` (or latest version if target is unset)
        mode 'refresh': Refresh the manifest database
    '''
    if mode == 'refresh':
        MinecraftManager.refresh()
        user.tell(f'Refreshed manifest database, know of {len(MinecraftManager.versions.versions)} version(s)')
        return
    elif mode == 'query':
        user.tell(f'Known server JAr contains version ID {MinecraftManager.jarvers()}')
        return

    if MinecraftManager.version_load_time < 0:
        raise RuntimeError(f'The versions manifest database has not been initialized yet, perhaps run {RS.CC.compose_command("version", "refresh")}')

    if mode == 'list':
        if target is None:
            user.tell('Add a target (one of "releases", "snapshots", "other", or "all")')
            return
        target = target.lower()
        if target not in {'releases', 'snapshots', 'other', 'all'}:
            raise ValueError(f'target must be one of "releases", "snapshots", "other", or "all", not "{target}"')
        user.tell(f'Versions[{target}] known as of {time.ctime(MinecraftManager.version_load_time)}')
        if target in {'releases', 'snapshots'}:
            vers = getattr(MinecraftManager.versions, target)
        elif target == 'other':
            vers = MinecraftManager.versions.other['*']
        else: # all
            vers = MinecraftManager.versions.versions
        user.tell(', '.join(reversed(vers.keys())))
    elif mode == 'set':
        if target is None:
            raise TypeError('target must be a version, not None')
        elif target not in MinecraftManager.versions.versions:
            raise KeyError(f'"{target}" is not a known version')
        MinecraftManager.install_version(target, chunk_notify=user.tell)
    else:
        raise RuntimeError(f'The program reached a state that should not be possible under normal conditions, debug: {user=!r} {mode=!r} {target=!r}')
