#!/bin/python3

#> Imports
import json
import traceback
from pathlib import Path
from urllib import request
from collections import namedtuple
from time import strptime
from functools import cache
from hashlib import sha1
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
    Config.mass_set_default('minecraft/manager/dl',
                            auto_fetch_if_missing=True, auto_update=True,
                            backup_replaced_jar=True,
                            version_manifest_url='https://launchermeta.mojang.com/mc/game/version_manifest.json',
                            bleeding_edge=False, only_snapshot=False,
                            hash_verify=True, size_verify=True, prompt_on_fail_verify=True,
                            time_fmt='%%Y-%%m-%%dT%%H:%%M:%%S%%z')

    def __init__(self):
        self.logger = RS.logger.getChild('MC')
    def init2(self):
        if Config['minecraft/manager/dl/auto_fetch_if_missing'] or Config['minecraft/manager/dl/auto_update']:
            try: self.versions = self.setup_manifest()
            except Exception as e:
                self.logger.fatal(f'Could not setup Minecraft version manifest:\n{"".join(traceback.format_exception(e))}')
                self.has_manifest = False
            else: self.has_manifest = True
        if not (p := Path(Config['minecraft/path/base'], Config['minecraft/path/server_jar'])).exists():
            self.logger.warning(f'{p} does not exist!')
            if not self.has_manifest:
                self.logger.irrec('Minecraft version manifest failed earlier; cannot continue')
                raise FileNotFoundError(str(p))
            if not Config['minecraft/manager/dl/auto_fetch_if_missing']:
                self.logger.irrec('Config minecraft/manager/dl/auto_fetch_if_missing is false, cannot download!')
                raise FileNotFoundError(str(p))
            if not self.install_update():
                raise ExceptionGroup('The server JAr couldn\'t be found, and the downloaded version failed verification. Cannot possibly continue', FileNotFoundError(p), ValueError('Verification failed'))

    @staticmethod
    def _fetch_url(url: str) -> bytes:
        with request.urlopen(url) as r: return r.read()
    @staticmethod
    @cache
    def _cached_fetch_url(url: str) -> bytes:
        with request.urlopen(url) as r: return r.read()

    def setup_manifest(self) -> 'VersionsType':
        self.logger.info(f'Fetching {Config["minecraft/manager/dl/version_manifest_url"]}')
        data = json.loads(self._fetch_url(Config['minecraft/manager/dl/version_manifest_url']).decode())
        tfmt = Config['minecraft/manager/dl/time_fmt']
        versions = {v['id']: v | {
                'time': strptime(v['time'], tfmt), '_time': v['time'],
                'releaseTime': strptime(v['releaseTime'], tfmt), '_releaseTime': v['releaseTime']
            } for v in data['versions']}
        return self.VersionsType(versions=versions,
            latest=max((versions[data['latest']['release']], versions[data['latest']['snapshot']]), key=lambda v: v['time']),
            latest_release=versions[data['latest']['release']],
            latest_snapshot=versions[data['latest']['snapshot']],
            releases = {k: v for k,v in versions.items() if v['type'] == 'release'},
            snapshots = {k: v for k,v in versions.items() if v['type'] == 'snapshot'},
        )

    @property
    def target(self) -> str:
        return self.versions.latest if Config['minecraft/manager/dl/bleeding_edge'] else \
               self.versions.latest_snapshot if Config['minecraft/manager/dl/only_snapshot'] else self.versions.latest_release
    @property
    def target_metadata(self) -> dict:
        return json.loads(self._cached_fetch_url(self.target['url']).decode())

    def install_update(self) -> bool:
        jp = Path(Config['minecraft/path/base'], Config['minecraft/path/server_jar'])
        if jp.exists():
            self.logger.warning(f'Instructed to fetch server JAr, but it already exists at {jp}')
            if Config['minecraft/manager/dl/backup_replaced_jar']:
                op = jp.with_suffix(f'{jp.suffix}.old')
                self.logger.warning(f'Copying {jp} to {op}')
                op.write_bytes(jp.read_bytes())
        tserver = self.target_metadata['downloads']['server']
        self.logger.warning(f'Fetching server JAr of target version ID {self.target["id"]}')
        data = self._fetch_url(tserver['url'])
        if not self.verify_update(data, tserver['sha1'], tserver['size']):
            return False
        jp.parent.mkdir(parents=True, exist_ok=True)
        self.logger.infop(f'Server JAr fetched, writing {len(data)} byte(s) to {jp}')
        jp.write_bytes(data)
        return True
    def verify_update(self, data: bytes, target_hash: str, target_size: int) -> bool:
        failed_hash, failed_size = False, False
        if Config['minecraft/manager/dl/hash_verify'] and (target_hash != (actual_hash := sha1(data).hexdigest())):
            self.logger.fatal(f'The Minecraft server JAr failed hash verification:\n{target_hash=}\n{actual_hash=}')
            failed_hash = True
        if Config['minecraft/manager/dl/size_verify'] and (target_size != (actual_size := len(data))):
            self.logger.fatal(f'The Minecraft server JAr failed size verification:\n{target_size=}\n{actual_size=}')
            failed_size = True
        if failed_hash or failed_size:
            if (not Config['minecraft/manager/dl/prompt_on_fail_verify']) or \
               (input(f'The Minecraft server JAr failed '
                      f'{"hash" if failed_hash else ""}{" and " if (failed_hash and failed_size) else ""}{"size" if failed_size else ""} '
                      f'verification. Install it anyway? (y/N) >').lower() != 'y'):
                self.logger.error('Not installing')
                return False
            self.logger.warning('Installing anyway, proceed with caution')
        return True
