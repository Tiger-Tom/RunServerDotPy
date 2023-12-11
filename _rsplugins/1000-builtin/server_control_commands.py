#!/bin/python3

#> Imports
import time
import RS
from RS import Flags, TellRaw, UserManager
#</Imports

#> Header >/
this.c.mass_set_default('commands/', {
    'stop/permission': 'ADMIN',
    'restart/permission': 'TRUSTED',
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
    
@RS.CC(permission=UserManager.User.perm_from_value(this.c('commands/stop/permission')), help_section=('Server Control',))
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
