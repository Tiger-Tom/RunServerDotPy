#!/bin/python3

#> Imports
import json
import traceback
from pathlib import Path
from urllib import request
from collections import namedtuple
from time import strptime
#</Imports

# RunServer Module
import RS
from RS import Bootstrapper, Config

#> Header >/
class MinecraftManager:
    __Slots__ = ('logger', 'has_manifest', 'versions', 'current_version')
    VersionsType = namedtuple('Versions', ('latest', 'latest_release', 'latest_snapshot', 'versions', 'releases', 'snapshots'))

    # Setup config
    Config.mass_set_default('minecraft/path/', base='./minecraft/', server_jar='server.jar')
    Config.mass_set_default('minecraft/manager/',
                            auto_fetch_if_missing=True, auto_update=True,
                            version_manifest_url='https://launchermeta.mojang.com/mc/game/version_manifest.json',
                            bleeding_edge=False, only_snapshot=False,
                            verify_download=True, fast_verify_download=False,
                            time_fmt='%%Y-%%m-%%dT%%H:%%M:%%S%%z')

    def __init__(self):
        self.logger = RS.logger.getChild('MC')
        super().__init__()
        if Config['minecraft/manager/auto_fetch_if_missing'] or Config['minecraft/manager/auto_update']:
            try: self.setup_manifest()
            except Exception as e:
                self.logger.fatal(f'Could not setup Minecraft version manifest:\n{"".join(traceback.format_exception(e))}')
                self.has_manifest = False
            else: self.has_manifest = True
        if not (p := Path(Config['minecraft/path/base'], Config['minecraft/path/server_jar'])).exists():
            self.logger.warning(f'{p} does not exist!')
            if not self.has_manifest:
                self.logger.irrec('Minecraft version manifest failed earlier; cannot continue')
                raise FileNotFoundError(str(p))
            if not Config['minecraft/manager/auto_fetch_if_missing']:
                self.logger.irrec('Config minecraft/manager/auto_fetch_if_missing is false, cannot download!')
                raise FileNotFoundError(str(p))
            self.missing_fetch()

    def setup_manifest(self):
        self.logger.info(f'Fetching {Config["minecraft/manager/version_manifest_url"]}')
        with request.urlopen(Config['minecraft/manager/version_manifest_url']) as r:
            data = json.load(r)
        tfmt = Config['minecraft/manager/time_fmt']
        versions = {v['id']: v | {
                'time': strptime(v['time'], tfmt), '_time': v['time'],
                'releaseTime': strptime(v['releaseTime'], tfmt), '_releaseTime': v['releaseTime']
            } for v in data['versions']}
        self.versions = self.VersionsType(versions=versions,
            latest=max((versions[data['latest']['release']], versions[data['latest']['snapshot']]), key=lambda v: v['time']),
            latest_release=versions[data['latest']['release']],
            latest_snapshot=versions[data['latest']['snapshot']],
            releases = {k: v for k,v in versions.items() if v['type'] == 'release'},
            snapshots = {k: v for k,v in versions.items() if v['type'] == 'snapshot'},
        )
    def missing_fetch(self):
        ...
