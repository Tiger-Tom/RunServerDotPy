#!/bin/python3

#> Imports
import json
import time
import typing
import traceback
from pathlib import Path
from hashlib import sha1
from io import BytesIO
from zipfile import ZipFile
#</Imports

# RunServer Module
import RS
from RS import Config
from RS.ShaeLib.net import fetch
from RS.ShaeLib.types.shaespace import SlottedSpaceType

#> Header >/
class MinecraftManager:
    __slots__ = ('logger', 'versions', 'version_load_time')
    VersionsType = SlottedSpaceType('latest', 'latest_bleeding', 'versions', 'releases', 'snapshots', 'other', name='VersionsType')

    # Setup config
    Config.mass_set_default('minecraft/path/', base='./minecraft/', server_jar='server.jar')
    Config.mass_set_default('minecraft/manager/',
        auto_fetch_if_missing=True, prompt_before_autofetch_missing=False,
        auto_update=True, unattended_autoupdate=False)
    Config.mass_set_default('minecraft/manager/download/',
        bleeding_edge=False,
        backup_replaced_jar=True,
        version_manifest_url='https://launchermeta.mojang.com/mc/game/version_manifest.json',
        verify=('hash', 'size', 'zipf'), prompt_on_fail_verify=True,
        time_fmt='%%Y-%%m-%%dT%%H:%%M:%%S%%z')

    def __init__(self):
        self.logger = RS.logger.getChild('MC')
        self.version_load_time = -1
    def init2(self):
        if self.jarpath.exists():
            if not Config['minecraft/manager/auto_update']: return
            try:
                self.refresh()
                self.auto_update()
            except Exception as e:
                self.logger.error(f'An exception occured whilst trying to auto-update:\n{"".join(traceback.format_exception(e))}')
            return
        if not Config['minecraft/manager/auto_fetch_if_missing']:
            self.logger.fatal('The server JAr is missing, and downloads are disabled (config `minecraft/manager/auto_fetch_if_missing`). Will try to continue anyway...')
            return
        if Config['minecraft/manager/prompt_before_autofetch_missing'] and input('The server JAr is missing. Download the latest version? (Y/n) >').lower().startswith('n'):
            self.logger.fatal('The server JAr is missing, and download was denied per user request. Will try to continue anyway...')
            return
        try:
            self.refresh()
            self.install_version(self.latest)
        except Exception as e:
            self.logger.fatal(f'An exception occured whilst trying to fetch missing JAr:\n{"".join(traceback.format_exception(e))}')

    @property
    def jarpath(self) -> Path:
        return Path(Config['minecraft/path/base'], Config['minecraft/path/server_jar'])
    def jarvers(self) -> str | None:
        if not self.jarpath.exists(): return None
        with ZipFile(self.jarpath) as zf, zf.open('version.json') as f:
            return json.load(f)['id']

    @property
    def latest(self) -> dict:
        return self.versions.latest_bleeding if Config['minecraft/manager/download/bleeding_edge'] else self.versions.latest
    def jar_is_latest(self) -> bool:
        return self.jarvers() == self.latest['id']

    def fetch_versions(self) -> 'VersionsType':
        '''Fetches the upstream versions manifest'''
        self.logger.info(f'Fetching {Config["minecraft/manager/download/version_manifest_url"]}')
        data = json.loads(fetch.fetch(Config['minecraft/manager/download/version_manifest_url']))
        tfmt = Config['minecraft/manager/download/time_fmt']
        versions = {v['id']: v | {
                'time': time.strptime(v['time'], tfmt), '_time': v['time'],
                'releaseTime': time.strptime(v['releaseTime'], tfmt), '_releaseTime': v['releaseTime'],
            } for v in data['versions']}
        vt = self.VersionsType()
        vt.versions = versions
        vt.latest = versions[data['latest']['release']]
        vt.latest_bleeding = versions[data['latest']['snapshot']]
        vt.releases = {}; vt.snapshots = {}; vt.other = {'*': {}}
        for i,v in versions.items():
            if v['type'] == 'release': vt.releases[i] = v
            elif v['type'] == 'snapshot': vt.snapshots[i] = v
            else:
                vt.other['*'][i] = v
                if v['type'] not in vt.other: vt.other[v['type']] = {}
                vt.other[v['type']][v['id']] = v
        return vt
    def refresh(self):
        '''Update internal versions manifest'''
        self.versions = self.fetch_versions()
        self.version_load_time = int(time.time())

    def upon_version(self, ver: str | dict):
        '''Returns the upstream manifest for the specified version ID or dictionary'''
        return json.loads(fetch.fetch((ver if isinstance(ver, dict) else self.versions.versions[ver])['url']).decode())
    def install_version(self, ver: str | dict, chunk_notify: typing.Callable[[str], None] | None = None):
        '''(Verifies and) installs the specified version'''
        v = self.upon_version(ver)
        self.logger.infop(f'Installing version {v["id"]}')
        if self.jarpath.exists():
            self.logger.warning('Instructed to fetch server JAr, but it already exists')
            if Config['minecraft/manager/download/backup_replaced_jar']:
                self.jarpath.with_suffix(f'{self.jarpath.suffix}.old').write_bytes(self.jarpath.read_bytes())
                self.logger.warning('Backed up JAr')
        self.logger.warning(f'Fetching server JAr of target version {v["id"]}')
        vs = v['downloads']['server']
        data = fetch.foreach_chunk_fetch(vs['url'],
                                         lambda c: (lambda c: (self.logger.infop(c), (None if chunk_notify is None else chunk_notify(c))))(
                                             f'Downloading {c.target}: chunk {int(c.obtained/c.chunk_size+0.5)}'
                                             f' of {int((c.remain+c.obtained)/c.chunk_size+1)}'))
        self.verify(data, vs['sha1'], vs['size'])
        self.logger.warning('Writing new JAr')
        self.jarpath.parent.mkdir(parents=True, exist_ok=True)
        self.jarpath.write_bytes(data)
    def verify(self, data: bytes, target_hash: str, target_size: int):
        '''Checks the data against a variety of configurable verifications'''
        v = Config['minecraft/manager/download/verify']
        exc = []
        hash_failed = ('hash' in v) and (target_hash != sha1(data).hexdigest())
        size_failed = ('size' in v) and (diff := (target_size - len(data)))
        if 'zipf' in v:
            try:
                with ZipFile(BytesIO(data)) as zf:
                    zipf_failed = zf.testzip() is not None
            except Exception as e:  zipf_failed = True
        else: zipf_failed = False
        failed = hash_failed + size_failed + zipf_failed
        failstr = ('hash' if hash_failed else '') + ('size' if size_failed else '') + ('ZipF' if zipf_failed else '')
        if failed: raise ValueError(f'{failstr[0].upper()}{failstr[1:4]}'
                                    f'{f", {failstr[4:8]}, and {failstr[8:]}" if (failed == 3) \
                                        else f" and {failstr[4:]}" if failed == 2 else ""} verification failed')

    def auto_update(self, force: bool = False):
        '''Automatically update to the latest version'''
        if not force:
            if not Config['minecraft/manager/auto_update']:
                self.logger.warning('Skipping auto update (config minecraft/manager/auto_update)')
                return
            if self.jar_is_latest():
                self.logger.infop(f'No need to update: {self.latest["id"]} is the latest viable version')
                return
            if not (Config['minecraft/manager/unattended_autoupdate'] or input('Check and update server JAr to latest version? (y/N) >').lower().startswith('y')):
                self.logger.warning('Skipping auto update (user request)')
                return
        self.install_version(self.latest)
