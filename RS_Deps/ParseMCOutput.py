#!/bin/python

#> Imports
import re
import zipfile
import json
import os
import ast
import warnings
#</Imports

#> Main >/
class MCParser:
    '''If assume_stderr_seperated is false, then we cannot assume that the stderr is seperated (A.E. for parsing server logs and not live output), so any unusual line that does not match any other pattern should be marked "assumed_error" and should return a "line"'''
    evalPrefix = 'EVAL_'
    regularize_death_vars = lambda x: x.replace('%1\\$s', '(?P<victim>.*)', 1).replace('%2\\$s', '(?P<culprit>.*)', 1).replace('%3\\$s', '(?P<using>.*)', 1).replace('%s', '(?P<unknown_field>.*)')
    def __init__(self, jarpath='server.jar', lang_code='en_us', *, assume_stderr_seperated=False, custom_lang: None | tuple[dict[str, dict[str, re.Pattern]], tuple[dict[str, dict[str, re.Pattern]]], dict[str, re.Pattern], re.Pattern, dict[str, str]] =None):
        # Get variables
        ## Set .jar path
        self.jarpath = jarpath
        ## Set language settings
        self.assume_stderr_seperated = assume_stderr_seperated
        # Fetch and compile language (unless custom_lang)
        if custom_lang is not None:
            self.lang, self.lang_unusual, self._search, self.commands = custom_lang
        else:
            self.lang,self.lang_unusual,self._search, self.commands = self.compile_lang(jarpath, lang_code)
    def compile_lang(self, jarpath: str, lcode='en_us') -> tuple[dict[str, dict[str, re.Pattern]], tuple[dict[str, dict[str, re.Pattern]]], dict[str, re.Pattern], dict[str, str]]:
        raw, rawDeath, commands, self.version = self.fetch_and_preprocess_lang(jarpath, lcode)
        lang_unusual = {
            'unpack_version': re.compile('^Unpacking (?P<packed>[0-9\w\.\-\/ ]+) \(versions:(?P<versions>.+)\) to (?P<file>[0-9\w\.\-\/ ]+)$'),
            'start_java_class': re.compile('^Starting (?P<class>[0-9\w\.]+)$'),
        }
        if not self.assume_stderr_seperated:
            lang_unusual['assumed_error'] = re.compile('(?P<line>.*)')
        print(f'Compiled {len(lang_unusual)} RegEx for lang_unusual (STDERR Mode: {"assume ignore" if self.assume_stderr_seperated else "do check"})\n{tuple(lang_unusual)}')
        regularize_death_vars = lambda x: x.replace('%1\\$s', '(?P<victim>.*)', 1).replace('%2\\$s', '(?P<culprit>.*)', 1).replace('%3\\$s', '(?P<using>.*)', 1).replace('%s', '(?P<unknown_field>.*)')
        lang = {
            'chat_insecure': {
                i.split('.')[-1]: re.compile('^\[Not Secure\] '+raw[f'chat.type.{i}'][1:].replace('%s', '(?P<player>\w+)', 1).replace('%s', '(?P<message>.*)', 1)) for i in ('text', 'emote', 'text.narrate', 'announcement', 'admin')
            }, 'chat': { # Pull any "chat.type.(text|emote|text.narrate|announcement|admin)"
                i.split('.')[-1]: re.compile(raw[f'chat.type.{i}'].replace('%s', '(?P<player>\w+)', 1).replace('%s', '(?P<message>.*)', 1)) for i in ('text', 'emote', 'text.narrate', 'announcement', 'admin')
            }, 'advancement': { # Pull any "chat.type.advancement.(task|challenge|goal)"
                i: re.compile(raw[f'chat.type.advancement.{i}'].replace('%s', '(?P<player>\w+)', 1).replace('%s', '(?P<advancement>.*)', 1)) for i in ('task', 'challenge', 'goal')
            }, 'join_leave': { # Pull any "multiplayer.player.joined*", "multiplayer.player.left"
                'joined': re.compile(raw['multiplayer.player.joined'].replace('%s', '(?P<player>\w+)', 1)),
                'renamed': re.compile(raw['multiplayer.player.joined.renamed'].replace('%s', '(?P<player>\w+)', 1).replace('%s', '(?P<old_name>\\w+)', 1)),
                'left': re.compile(raw['multiplayer.player.left'].replace('%s', '(?P<player>\w+)', 1)),
                'lost_connection': re.compile('^(?P<player>\w+) lost connection: (?P<reason>.*)$'),
                'uuid_assignment': re.compile('^UUID of player (?P<player>\\w+) is (?P<uuid>.*)$'),
                'entity_assignment': re.compile(f'^(?P<player>\w+)\[\/(?P<origin>(?P<ip>[0-9\.]+):(?P<{self.evalPrefix}port>[0-9]+))\] logged in with entity id (?P<{self.evalPrefix}entity_id>[0-9]+) at \((?P<{self.evalPrefix}x>[0-9\-\.]+), (?P<{self.evalPrefix}y>[0-9\-\.]+), (?P<{self.evalPrefix}z>[0-9\-\.]+)\)$'),
            }, 'entity_death': {
                'death': re.compile(f'^(?P<entity_type>(?:Villager)|(?:Named Entity)) (?P<entity_class>\w+)\[\'(?P<entity_name>.*?)\'\/[0-9]+, l=\'(?P<level>.*?)\', x=(?P<{self.evalPrefix}x>[0-9\-\.]+?), y=(?P<{self.evalPrefix}y>[0-9\-\.]+?), z=(?P<{self.evalPrefix}z>[0-9\-\.]+?)\] died(?:, message)?: (?:\')?(?P<message>.*?)(?:\')?$'),
            }, 'rcon': {
                'enable': re.compile(f'^RCON running on (?P<origin>(?P<ip>[0-9\.]+):(?P<{self.evalPrefix}port>[0-9]+))$'),
                'disable': re.compile('^Thread RCON Listener stopped$'),
                'connect': re.compile('^Thread RCON Client \/(?P<ip>[0-9\.]+) started$'),
                'disconnect': re.compile('^Thread RCON Client \/(?P<ip>[0-9\.]+) (?P<status>(?:stopped)|(?:shutting down))$'),
            }, 'server': {
                'start': re.compile('^Starting minecraft server version (?P<version>.*)$'),
                'stopping': re.compile('^Stopping server$'),
                'overload': re.compile(f'^Can\'t keep up! Is the server overloaded? Running (?P<{self.evalPrefix}ms_behind>[0-9]+)ms or (?P<{self.evalPrefix}ticks_behind>[0-9]+) ticks behind$'),
            }, 'command': {
                'general': re.compile('^\[(?P<executor>.+): (?P<action>.*)\]$'),
            }, 'death': { i[6:]: re.compile('^'+(rawDeath[i].replace('%1\\$s', '(?P<victim>.*)', 1).replace('%2\\$s', '(?P<culprit>.*)', 1).replace('%3\\$s', '(?P<using>.*)', 1).replace('%s', '(?P<unknown>.*)', 1))) for i in rawDeath.keys() },
        }
        print(f'Compiled {sum(len(i) for i in lang.values())} RegEx for lang:')
        print('    '+('\n    '.join(f'{k}: {len(v)}' for k,v in lang.items())))
        # "{self.evalPrefix}" is stripped from the key by .check_line, and tells it to automatically cast the type using eval
        search = re.compile('^\[([0-9\:]+)\] \[(.+)\/(.+)\]: (.*)$', flags=re.MULTILINE)
        return lang, lang_unusual, search, commands
    def search_regex(self, pattern: re.Pattern, line: str, regexParentKey: str, regexSubKey: str) -> tuple[tuple[str, str], dict[str, ...]] | None:
        if mat := pattern.match(line):
            return (regexParentKey, regexSubKey), {
                k if not k.startswith(self.evalPrefix) else k[len(self.evalPrefix):]: v if not k.startswith(self.evalPrefix) else ast.literal_eval(v) for k, v in mat.groupdict().items()
            }
    def check_line(self, line: str) -> tuple[tuple[str, str], dict[str, ...]] | None:
        if not line: return
        for k0,v in self.lang.items():
            for k1 in v.keys():
                if res := self.search_regex(self.lang[k0][k1], line, k0, k1):
                    return res
    def check_unusual_line(self, line: str) -> tuple[str, dict[str, ...]] | None:
        if not line: return
        for key,reg in self.lang_unusual.items():
            if mat := reg.match(line):
                return key, {
                    k if not k.startswith(self.evalPrefix) else k[len(self.evalPrefix):]: v if not k.startswith(self.evalPrefix) else ast.literal_eval(v) for k, v in mat.groupdict().items()
                }
    def parse_command_output(self, line: str, command: str, groupKeys: tuple[str]) -> dict[...] | None:
        regx = f'^{self.commands[command]}$'
        assert len(groupKeys) == regx.count('%s'), f'Incorrect amount of keys to match (expected {regx.count("%s")}, got {len(groupKeys)})'
        if regx.count('%s') != 0:
            for k in groupKeys:
                regx = regx.replace('%s', k, 1)
        print(regx)
        if mat := re.match(regx, line):
            return mat.groupdict()
    @staticmethod
    def fetch_and_preprocess_lang(jarpath: str, lcode: str) -> tuple[dict[str, str], dict[str, str], dict[str, str], str]:
        with zipfile.ZipFile(jarpath) as sJarZip:
            with sJarZip.open('META-INF/versions.list') as v:
                version = v.read().decode().split('\n')[0].split('\t')[2]
            ver = f'META-INF/versions/{version}'
            with sJarZip.open(ver) as vf, zipfile.ZipFile(vf) as zfvf:
                if True:
                    print(f'Extracting {jarpath}://{ver}://assets/minecraft/lang/{lcode}.json')
                    jason = json.loads(zfvf.read(f'assets/minecraft/lang/{lcode}.json')).items()
                    return {
                        k: f'^{re.escape(v)}$' for k,v in jason if k.split('.')[0] in {'multiplayer', 'advancement', 'death', 'connect', 'disconnect', 'dataPack', 'datapackFailure', 'chat'}
                    }, {
                        k: re.escape(v) for k,v in jason if k.split('.')[0] == 'death'
                    }, {
                        k: f'^{re.escape(v)}$' for k,v in jason if k.split('.')[0] in {'command', 'commands'}
                    }, version.split('/')[0]
    def parse_line(self, line: str) -> tuple[bool, str, tuple[str, str], tuple[tuple[[str, str], dict[str, ...]]] | None] | None:
        if match := self._search.match(line):
            if len(match.groups()) < 4:
                return None
            return False, match.group(4), (match.group(2), match.group(3)), self.check_line(match.group(4))
        return True, self.check_unusual_line(line)
    def parse_lines(self, text: str) -> tuple[bool, str, tuple[str, str], tuple[tuple[[str, str], dict[str, ...]]]] | None:
        for i in text.split('\n'):
            yield self.parse_line(i)
