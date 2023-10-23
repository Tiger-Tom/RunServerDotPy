#!/bin/python

version = (2, 0, 0)

#> Imports
import shutil, os, sys
import threading, subprocess
import json
from collections.abc import Callable
import select
from mcrcon import MCRcon
import warnings
import time
# Custom imports
from RS_Deps.ParseMCOutput import MCParser
from RS_Deps.RSModuleHandler import ModuleHandler
from RS_Deps.RSLoggingHandler import Logger
#</Imports

#> Set uptime
uptime = time.time()

#> Check if running in IDLE
if 'idlelib' in sys.modules:
    raise RuntimeWarning('This should not run in IDLE, as it can (and probably will) cause massive output errors')
#</Check if running in IDLE

#> Ensure EULA
print('Checking EULA...')
if eula := os.path.exists('./eula.txt'):
    with open('./eula.txt') as f:
        if eula := 'eula=true' in f.read():
            print('EULA accepted, continuing')
        else:
            eula = False
if not eula:
    if input('Mojang EULA not accepted. Accept? (y/N) >')[0].lower() != 'y':
        exit()
    else:
        with open('./eula.txt', 'w') as f:
            f.write('eula=true')
del eula
#</Ensure EULA

#> Helper functions/objects
# Printing
term_print_codes = {k: f'\033[{v}m' for k,v in {
    'end': 0,
    'bold': 1,
    'italic': 3,
    'underline': 4,
    'slow_blink': 5,
    'rapid_blink': 6,
    'swap_fg_bg': 7,
}.items()}
def print_color(colors: tuple[int, int, str] | str, *to_print: tuple[...], print_func=print, reset_after=True, reset_before=True, **kwargs):
    if reset_before: clear_color(print_func)
    if type(colors) is str:
        colors = globalConfig['terminal_colors'][colors]
    if colors[0] is not None: print_func(f'\033[38;5;{colors[0]}m', end='', **kwargs)
    if colors[1] is not None: print_func(f'\033[48;5;{colors[1]}m', end='', **kwargs)
    if colors[2] is not None: print_func(colors[2], end='', **kwargs)
    print_func(*to_print, **kwargs)
    if reset_after: clear_color(print_func)
def clear_color(print_func=print, **kwargs):
    print_func(term_print_codes['end'], end='', **kwargs)
clear_color() # Ensure consistancy
#</Helper functions/objects

#> Setup Config
def retrieveConfig() -> dict:
    default_config = {
        'ram_mb': lambda: int(ares) if (ares := input('Enter amount of RAM to allocate (in MB) (default 2048) >')) and ares.isdigit() else 2048,
        'autorestart-after': lambda: int(ares) if (ares := input('Enter time in hours between automatic restarts (0 for never automatically restarting, 12 by default) >')) and ares.isdigit() else 12,
        'rcon': {
            'port': lambda: int(ares) if (ares := input('Enter given RCon port (default 25575) >')) and ares.isdigit() else 25575,
            'password': lambda: input('Enter RCon password >'),
        },
        'motds': lambda: input('Enter server MOTDs to randomly select between, seperated by a " , " (space comma space) (strftime components will be replaced by the time at the server\'s last restart)\n').split(' , '),
        'cc_prefix': lambda: input('Enter prefix to be used for ChatCommands (cannot be "/", recommended one of "~", "!", "@", "#", "$", "%", "^" (example !help, @help, etc.)) (commands entered in chat) >'),
        'join_message': lambda: input('Enter user join message ("$user" will be replaced with their username, "$ccprefix" will be replaced with the ChatCommand prefix chosen earlier, and any strftime components will be replaced with time) >'),
        'terminal_colors': {
            'fail': (16, 198, '\033[1m'),
            'error': (198, 16, None),
            'warn': (11, None, None),
            'ok': (None, None, None),
            'attention': (None, None, '\033[1m'),
        },
        'attention_types': ('chat', 'join_leave', 'entity_death', 'rcon', 'server', 'command', 'death'),
        'ignored_logs': (),
        'log_format': '[%Y-%m-%d %H:%M:%S] {message}\n',
    }
    if not os.path.exists('./RS_Deps/RSConfig.json'):
        print('Performing first-time configuration')
        with open('./RS_Deps/RSConfig.json', 'w') as f:
            json.dump({k: v for k, v in default_config.items()}, f, indent=4, sort_keys=True, default=lambda x: repr(x) if not callable(x) else x())
    print('Retrieving configuration')
    with open('./RS_Deps/RSConfig.json') as f:
        conf = json.load(f)
        dirty = False
        for k, v in default_config.items():
            if not k in conf:
                conf[k] = v if not callable(v) else v()
                dirty = True
    if dirty:
        with open('./RS_Deps/RSConfig.json', 'w') as f:
            print('Updating configuration')
            json.dump(conf, f, indent=4, sort_keys=True)
    term_color_merge = {}
    for n,c in conf['terminal_colors'].items():
        if n == 'attention': continue
        term_color_merge[f'!{n}'] = tuple(j if j is not None else c[i] for i,j in enumerate(conf['terminal_colors']['attention']))
    conf['terminal_colors'].update(term_color_merge)
    print('Edit "./RS_Deps/RSConfig.json" to reconfigure settings')
    return conf
globalConfig = retrieveConfig()
#</Setup Server Config

#> Server IO Manager
class ServerIO:
    def __init__(self, popen: subprocess.Popen, rcon: dict):
        self.proc = popen
        self.stdout = popen.stdout
        self.stderr = popen.stderr
        self.stdin = popen.stdin
        self.rconcon = rcon
        self.keepalive = False
        self.stdoutd = None
        self.stderrd = None
        self.rcon = None
        os.set_blocking(self.stdout.fileno(), False)
        os.set_blocking(self.stderr.fileno(), False)
    def write(self, data: str, flush=True):
        self.stdin.write(bytes(data, 'UTF-8'))
        if flush: self.stdin.flush()
    def command(self, data: str) -> str:
        if not data: return
        if not self.rcon:
            self.rcon = MCRcon('127.0.0.1', self.rconcon['password'], self.rconcon['port'])
        self.rcon.connect()
        out = self.rcon.command(data)
        self.rcon.disconnect()
        return out
    def tellraw(self, user='@a', text=''):
        try: json.loads(text)
        except json.JSONDecodeError:
            text = f'"{text}"'.replace('\n', '\\n')
        self.write(f'tellraw {user} {text}\n')
    def startEventLoop(self, callbackOut: Callable[[...], ...], callbackErr: Callable[[...], ...]):
        self.keepalive = True
        self.stdoutd = threading.Thread(target=self._threaded_loop, args=(self._chkeepalive, self.stdout.readline, callbackOut), daemon=True)
        self.stderrd = threading.Thread(target=self._threaded_loop, args=(self._chkeepalive, self.stderr.readline, callbackErr), daemon=True)
        self.stdoutd.start()
        self.stderrd.start()
    def stopEventLoop(self):
        self.keepalive = False
        self.stdoutd = None
        self.stderrd = None
    def kill(self):
        if self.rcon:
            self.rcon.disconnect()
            self.rcon = None
        self.stopEventLoop()
    def _chkeepalive(self) -> bool:
        return self.keepalive and (self.proc.poll() is None)
    @staticmethod
    def _threaded_loop(check: Callable[[], bool], function: Callable[[], ...], callback: Callable[[...], ...]): # Repeatadly runs "callback" with output of "function" as arg until output of "check" resolves false
        while check():
            callback(function())
#</Server IO Manager

#> Server IO Parser/Wrapper
class ServerWrapper:
    def __init__(self, srvIO: ServerIO, parser: MCParser, mHandler: ModuleHandler, logger: Logger, onSTDerr=None):
        self.server = srvIO
        self.logger = logger
        self.parser = parser
        self.mHandler = mHandler
        self.err_callback = onSTDerr
        self.stop = self.server.kill
        self.command = self.server.command
    def write(self, data: str):
        self.server.write(data.strip()+'\n')
    def parse_stdout(self, line: bytes):
        line = line.decode().strip()
        if not line: return
        if not (lP := self.parser.parse_line(line)):
            print_color('ok', line)
            return
        if not lP[0]: # Is not unusual
            (thread,level) = lP[2]
            color = ('fail' if level == 'FAIL' else ('error' if level == 'ERROR' else ('warn' if level == 'WARN' else 'ok')))
            if lP[3]:
                ((category,mtype),match) = lP[3]
                if category in globalConfig['attention_types']: color = f'!{color}'
                if category == 'join_leave':
                    if mtype in {'joined', 'left'}:
                        self.logger.log('player_event', f'Player {match["player"]} {mtype}')
                    elif mtype == 'lost_connection':
                        self.logger.log('player_event', f'Player {match["player"]} lost connection (reason: {match["reason"]})')
                    elif mtype == 'uuid_assignment':
                        self.logger.log('player_event', f'Player {match["player"]} on UUID join stage. UUID is {match["uuid"]}')
                    elif mtype == 'entity_assignment':
                        self.logger.log('player_event', f'Player {match["player"]} is being assigned an entity\n Origin: {match["origin"]}\n Entity ID {match["entity_id"]} at ({match["x"]}, {match["y"]}, {match["z"]})')
                elif category in {'chat', 'chat_insecure'}:
                    if mtype == 'text':
                        if match['message'].startswith(globalConfig['cc_prefix']):
                            ln = match['message'][len(globalConfig['cc_prefix']):].split(' ')
                            self.mHandler.run_ccommand(match['player'], ln[0], ln[1:], (0 if category == 'chat_insecure' else None))
                            return
                    self.logger.log('player_chat', f'{match["player"]}{"?" if category == "chat_insecure" else ""}/{mtype}: {match["message"]}')
                elif category in {'death', 'advancement'}:
                    self.logger.log('player_event', lP[1])
                elif category == 'rcon':
                    if mtype == 'disable':
                        print('RCon stopped, disconnecting')
                        self.stop()
                        raise StopIteration('_exit')
                    elif (mtype in ('connect', 'disconnect')) and ((match['ip'] == '127.0.0.1')): # Prevents output console spam, since RCon from 127.0.0.1 (localhost) is used for input sometimes
                        return
                elif category == 'command':
                    self.logger.log('command', lP[1])
            print_color(color, line)
            return
        # Is unusual
        else:
            if (lP := self.parser.check_unusual_line(line)):
                (key,match) = lP
                color = 'warn'
                if key == 'unpack_version':
                    self.logger.log('main', line)
                    color = '!ok'
                elif key == 'start_java_class':
                    self.logger.log('main', f'Starting Java class {match["class"]}')
                    color = '!ok'
                else:
                    self.logger.log('unusual', line)
                print_color(color, line)
    def parse_stderr(self, line: str):
        line = line.decode()
        if not line: return
        print_color('fail', line)
        if callable(self.onSTDerr): self.onSTDerr(line)
        self.logger.log('Error', line)
#</Server IO Parser/Wrapper

#> Main >/
def main(jArgs=(), sArgs=('nogui',)):
    print('Initializing process')
    pop = subprocess.Popen(('java', *jArgs, '-jar', 'server.jar', *sArgs), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    print('Initializing IO manager')
    sio = ServerIO(pop, globalConfig['rcon'])
    print('Initializing logger')
    log = Logger(globalConfig['log_format'], 'RS_Deps/Logs/', globalConfig['ignored_logs'])
    print('Initializing output parser')
    parser = MCParser('./server.jar')
    print('Initializing module manager')
    handler = ModuleHandler('./RS_Deps/RSModules', {}, globalConfig['cc_prefix'], sio.tellraw, sio.command, log, parser, globalConfig, uptime, time.time(), version)
    print('Initializing outwards wrapper')
    wrap = ServerWrapper(sio, parser, handler, log)
    return pop, wrap, log
def restart(pop, wrap, log): # Restarts everything, but keeps as much old data as it safely can (logger, output parser, etc) to facilitate a faster restart
    print('Terminating old server instance if it exists')
    pop.terminate() # Make sure to kill it
    print('Stopping scheduled functions')
    wrap.mHandler.schedulerKA = False
    print('Starting a new server instance')
    pop = subprocess.Popen(pop.args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    print('Initializing new IO manager')
    sio = ServerIO(pop, globalConfig['rcon'])
    print('Pulling old output parser')
    parser = wrap.parser
    print('Initializing new module manager')
    handler = ModuleHandler('./RS_Deps/RSModules', {}, globalConfig['cc_prefix'], sio.tellraw, sio.command, log, parser, globalConfig, uptime, time.time(), version)
    print('Initializing new outwards wrapper')
    wrap = ServerWrapper(sio, parser, handler, log)
    print('Flushing log')
    log.flush()
    return pop, wrap, log

if __name__ == '__main__':
    pop,wrap,log = main((f'-Xmx{globalConfig["ram_mb"]}M', f'-Xms{globalConfig["ram_mb"]}M'), ('nogui',))
    log.log('main', 'Server started')
    while True:
        while True:
            try:
                out = select.select((sys.stdin.fileno(), pop.stdout.fileno(), pop.stderr.fileno()), (), (), 8)[0]
                if (c := pop.poll()) is not None:
                    print_color(('!fail' if c != 0 else '!warn'), f'The Java server process completed with return code {c}, flushing output buffers...')
                    if o := pop.stdout.readlines(): print('\n'.join(o))
                    if o := pop.stdout.readlines():
                        print_color('!error', '\n'.join(o))
                        log.log('error', f'Server exited with non-zero code {c}')
                    break
                while len(out):
                    if out[0] == sys.stdin.fileno():
                        line = sys.stdin.readline()
                        if line.startswith(globalConfig['cc_prefix']):
                            wrap.mHandler.run_ccommand(wrap.mHandler.server_identifier, line.split()[0][len(globalConfig['cc_prefix']):], line.split()[1:])
                        else:
                            wrap.write(line)
                    elif out[0] == pop.stdout.fileno():
                        while line := pop.stdout.readline():
                            wrap.parse_stdout(line)
                            sys.stdout.flush()
                    elif out[0] == pop.stderr.fileno():
                        while line := pop.stderr.readline():
                            wrap.parse_stderr(line)
                            sys.stdout.flush()
                    out.pop(0)
            except StopIteration as e:
                if e.args[0] == '_exit':
                    print('Exit signal recieved, server closed')
                    log.log('main', 'Recieved exit signal from line parser')
                    break
                raise e
            except Exception as e:
                print_color('!fail', str(e).strip())
                traceback.print_exc()
                log.log('error', traceback.print_exc())
        log.log('main', 'Server closed')
        try:
            for i in range(5, 0, -1):
                print_color('!warn', f'Restarting server in {i} second(s), press CTRL+C to cancel')
                time.sleep(1)
            log.log('main', 'Server automatically restarted')
            pop,wrap,log = restart(pop, wrap, log)
        except KeyboardInterrupt:
            print_color('!fail', 'Server restart cancelled, exiting')
            log.log('main', 'Server restart cancelled by user')
            break
    log.close()
