#!/bin/python3

#> Imports
# Parsing
import re
import json
# Files
import zipfile
from pathlib import Path
# Types
import typing
#</Imports

# RunServer Module
import RS
from RS import Config
from RS.Types import Hooks

#> Header >/
class MCLang:
    __slots__ = ('logger', 'lang', 'version_info')

    prefix = re.compile(r'^\[(?P<time>[0-9:]{8})\] \[(?P<thread>[^/]+)/(?P<level>[A-Z]+)\]: (?P<line>.*?)$')
    
    def __init__(self):
        self.logger = RS.logger.getChild('Lang')
        self.extract_lang()

    # Lang interaction
    ## Lines
    def strip_prefix(self, line: str) -> tuple[re.Match | None, str]:
        if (m := self.prefix.fullmatch(line)) is not None: return (m, m.group('line'))
        return (None, line)
    ## Patterns
    def lang_to_pattern(self, lang: str, group_names: tuple[str] | None = None, *, prefix_suffix: str = '^{}$') -> re.Pattern:
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
        with zipfile.ZipFile(Path(Config('minecraft/path/base', './minecraft'), Config('minecraft/path/server_jar', 'server.jar'))) as jzf:
            vers = Config('minecraft/lang_parser/version', None, on_missing=Config.on_missing.SET_RETURN_DEFAULT)
            self.version_info = None
            with jzf.open('version.json') as vf:
                self.version_info = json.load(vf)
            if vers is None: vers = self.version_info['id']
            with zipfile.ZipFile(jzf.open(f'META-INF/versions/{vers}/server-{vers}.jar')) as szf:
                with szf.open(f'assets/minecraft/lang/{Config("minecraft/lang_parser/lang", "en_us")}.json') as lf:
                    self.lang = json.load(lf)
                    return self.lang
            
class LineParser:
    __slots__ = ('logger', 'hooks_prefix', 'hooks_no_prefix', 'hooks_chat', 'chat_patt')

    def __init__(self):
        self.logger = RS.logger.getChild('LineParser')
        self.hooks_prefix = Hooks.ReHooks('fullmatch')
        self.hooks_no_prefix = Hooks.ReHooks('fullmatch')
        self.hooks_chat = Hooks.SingleHook()
        self.chat_patt = RS.MCLang.lang_to_pattern(RS.MCLang.lang['chat.type.text'], ('username', 'message'), prefix_suffix=r'^(?P<not_secure>(?:\[Not Secure\] )?){}$')
    def register_callback(self, patt: re.Pattern, callback: typing.Callable[[re.Match, re.Match], None] | typing.Callable[[re.Match], None], with_prefix: bool = True):
        '''
            Registers a callback
                If keep_prefix, then lines that have the prefix are passed along with the prefix (the match is the first argument, followed by the prefix)
                Otherwise, lines that don't have a prefix are passed
        '''
        (self.hooks_prefix if with_prefix else self.hooks_no_prefix).register(patt, callback)
    def register_chat_callback(self, callback: typing.Callable[['User', str, bool], None]):
        '''
            Registers a callback for when chat is recieved
                The callback should have the signature `callback(user: RS.UserManager.User, message: str, insecure: bool)`
        '''
        self.hooks_chat.register(callback)
    def handle_line(self, line: str):
        pfx, lin = RS.MCLang.strip_prefix(line)
        if pfx is None: return self.hooks_no_prefix(lin) # returns nothing!
        self.hooks_prefix(lin, pfx)
        if (m := self.chat_patt) is not None:
            self.hooks_chat(RS.UserManager[m.group('username')], m.group('message'), bool(m.group('not_secure')))
