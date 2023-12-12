#!/bin/python3

#> Imports
# Parsing
import re
import json
# Files
import zipfile
from pathlib import Path
# Types
import time
import typing
#</Imports

# RunServer Module
import RS
from RS import Bootstrapper, Config
from RS.ShaeLib.types import Hooks
from RS.ShaeLib.timing import PerfCounter

#> Header >/
class MCLang:
    __slots__ = ('logger', 'lang', 'version_info')
    prefix = re.compile(r'^\[(?P<time>[0-9:]{8})\] \[(?P<thread>[^/]+)/(?P<level>[A-Z]+)\]: (?P<line>.*?)$')

    # Setup config
    Config.mass_set_default('minecraft/lang_parser', version=None, lang='en_us')

    def __init__(self):
        self.logger = RS.logger.getChild('L')
    def init2(self):
        self.extract_lang()

    # Lang interaction
    ## Lines
    def strip_prefix(self, line: str) -> tuple[tuple[re.Match, time.struct_time] | None, str]:
        line = line.strip()
        if (m := self.prefix.fullmatch(line)) is not None:
            # almost as bad as my first idea: `time.strptime(f'{m.time}|{time.strftime("%x")}', '%H:%M:%S|%x')`
            return ((m, time.struct_time(time.localtime()[:3] + time.strptime(m.group('time'), '%H:%M:%S')[3:6] + time.localtime()[6:])), m.group('line'))
        return (None, line)
    ## Patterns
    def lang_to_pattern(self, lang: str, group_names: tuple[str, ...] | None = None, *, prefix_suffix: str = '^{}$') -> re.Pattern:
        l = enumerate(lang)
        patt = []; held_groups = set(); next_group = 1
        pattern_gen = lambda t: f'{r"\d+" if t == "d" else ".+"}?'
        capture_gen = lambda n,t: f'(?P<{group_names[n-1] if (group_names is not None) and (len(group_names) >= n) else f"l{n}"}>{pattern_gen(t)})'
        for i,c in l:
            # Normal chars #
            if c != '%':
                patt.append(re.escape(c))
                continue
            # %-chars #
            n = next(l)[1]
            # Escaped % (%%)
            if n == '%':
                patt.append('%')
                continue
            # Simple capture (%s, %d)
            if n in {'s', 'd'}:
                patt.append(pattern_gen(n) if next_group in held_groups else capture_gen(next_group, n))
                held_groups.add(next_group)
                next_group += 1
                continue
            # Error checking
            if not n.isdigit(): raise SyntaxError(f'Malformed pattern: {lang} at {i+1} ({n})')
            # Complex capture (%[n]$[s|d])
            n = int(n)
            if next(l)[1] != '$': raise SyntaxError(f'Malformed pattern: {lang} at {i+2}')
            t = next(l)[1]
            if n in held_groups:
                patt.append(pattern_gen(t))
                continue
            held_groups.add(n)
            patt.append(capture_gen(n, t))
        self.logger.debug(f'{lang!r} -> {patt}')
        return re.compile(prefix_suffix.format(''.join(patt)))
    # Lang extraction
    def extract_lang(self) -> dict[str, str]:
        '''Extracts the language file from a server JAR file, sets and returns self.lang'''
        self.logger.debug('Extracting lang')
        if Bootstrapper.is_dry_run:
            self.logger.error('Is a dry-run')
            from collections import defaultdict
            self.lang = defaultdict(str)
            return self.lang
        pc = PerfCounter()
        jzp = zipfile.Path(Path(Config['minecraft/path/base'], Config['minecraft/path/server_jar']))
        vers = Config['minecraft/lang_parser/version']
        self.version_info = None
        with (jzp / 'version.json').open('r') as vf:
            self.version_info = json.load(vf)
        if vers is None: vers = self.version_info['id']
        with ((jzp / f'META-INF/versions/{vers}/server-{vers}.jar').open('rb') as vzf,
              zipfile.Path(vzf, f'assets/minecraft/lang/{Config["minecraft/lang_parser/lang"]}.json').open('r') as lf):
            self.lang = json.load(lf)
            self.logger.infop(f'Loaded lang in {pc}')
            return self.lang

class LineParser:
    __slots__ = ('logger', 'hooks_prefix', 'hooks_no_prefix', 'hooks_chat', 'chat_patt')

    def __init__(self):
        self.logger = RS.logger.getChild('LP')
        self.hooks_prefix = Hooks.ReHooks('fullmatch')
        self.hooks_no_prefix = Hooks.ReHooks('fullmatch')
        self.hooks_chat = Hooks.SingleHook()
    def init2(self):
        self.chat_patt = RS.MCLang.lang_to_pattern(RS.MCLang.lang['chat.type.text'], ('username', 'message'), prefix_suffix=r'^(?P<not_secure>(?:\[Not Secure\] )?){}$')
    def register_callback(self, patt: re.Pattern, callback: typing.Callable[[re.Match, re.Match, time.struct_time], None] | typing.Callable[[re.Match], None], with_prefix: bool = True):
        '''
            Registers a callback
                If keep_prefix, then lines that have the prefix are passed. callback should have the signature: `callback(line: re.Match, prefix: re.Match, time: time.struct_time)`
                Otherwise, lines that don't have a prefix are passed; the callback should have the signature: `callback(line: re.Match)`
        '''
        (self.hooks_prefix if with_prefix else self.hooks_no_prefix).register(patt, callback)
    def register_chat_callback(self, callback: typing.Callable[[typing.ForwardRef('RS.UM.User'), str, bool], None]):
        '''
            Registers a callback for when chat is recieved
                The callback should have the signature `callback(user: RS.UserManager.User, message: str, insecure: bool)`
        '''
        self.hooks_chat.register(callback)
    def handle_line(self, line: str):
        pfx, lin = RS.MCLang.strip_prefix(line)
        if pfx is None: return self.hooks_no_prefix(lin) # returns nothing!
        self.hooks_prefix(lin, *pfx)
        if (m := self.chat_patt.fullmatch(lin)) is not None:
            self.hooks_chat(RS.UserManager[m.group('username')], m.group('message'), bool(m.group('not_secure')))
