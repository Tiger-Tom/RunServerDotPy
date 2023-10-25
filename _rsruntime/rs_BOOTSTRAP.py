#!/bin/python3

# Bootstrapper and manifest manager #

#> Imports
import logging
import typing
from packaging import version
# File
from pathlib import Path
import json
import hashlib
import re
# Optimization
import multiprocessing
# Web
import requests
#</Imports

#> Header >/
class Bootstrapper:
    __slots__ = ('root_logger', 'logger')
    base_dirs = {'rsconf', 'rsplugins/builtin', 'rsruntime'}
    #dl_man_base = 'https://gist.githubusercontent.com/Tiger-Tom/85a2e52d7f8550a70a65b749f65bc303/raw/8a922bb83e9cb724e1913082113168f4e3ccc99e'
    dl_man_base = 'http://0.0.0.0:8000/manifests'
    dl_man_path = lambda self,n: f'{self.dl_man_base}/{n.replace("/", "_")}.json'
    version_extract = re.compile(r'^__version__\s*=\s*(.*)$')
    algorithm = hashlib.sha1
    
    def __init__(self):
        self.root_logger = logging.getLogger('RunServer')
        self.logger = self.root_logger.getChild('Bootstrapper')
        self.logger.info(f'Initialized: {self}')
    # Check for base directories
    def _bootstrap_basedir(self, name: str):
        self.logger.debug(f'Checking base directory: {name}')
        path = Path.cwd() / f'_{name}'
        man = path / 'MANIFEST.json'
        # Create it if it doesn't exist
        if path.exists(): self.logger.debug(f'[OKAY] {path} exists')
        else:
            self.logger.info(f'{path} does not exist, creating')
            path.mkdir(parents=True)
            self.logger.debug(f'[OKAY] {path} exists')
    def bootstrap(self):
        self.logger.info('Distributing threads for each directory')
        with multiprocessing.Pool() as p:
            self.logger.info(f'Distrubuting {p._processes} thread(s) to _bootstrap_basedir')
            p.map(self._bootstrap_basedir, self.base_dirs)
            self.logger.info(f'Distributing {p._processes} thread(s) to check_manifest')
            try:
                mans = p.starmap(self.check_manifest, ((name, Path.cwd() / f'_{name}', self.dl_man_path(name), self.dl_man_base) for name in self.base_dirs))
            except Exception as e:
                self.logger.fatal(f'check_manifest failed somewhere: caught {e}; dazed and confused, but trying to continue')
            self.logger.info(f'Distributing {p._processes} thread(s) to execute_manifest')
            try:
                p.starmap(self.execute_manifest, ((man, Path.cwd() / f'_{man["_metadata"]["name"]}') for man in mans))
            except Exception as e:
                self.logger.fatal(f'execute_manifest failed somewhere: caught {e}; dazed and confused, but trying to continue')
        self.logger.warning('BOOTSTRAPPING COMPLETE; ATTEMPTING TO ACCESS ENTRYPOINT...')
        from .rs_ENTRYPOINT import RunServer
        self.logger.warning(f'ENTRYPOINT ACCESSED, INITIALIZING ENTRYPOINT...')
        rs = RunServer(self)
        self.logger.warning('ENTRYPOINT INITIALIZED, EXECUTING ENTRYPOINT...')
        rs()
    # Manifest utilities
    def check_manifest(self, name: str, path: Path, man_upstream: str | None=None, man_upstream_base: str | None=None, known_differs=False, past_upstreams={}) -> None | dict:
        iman = {'_metadata': {'name': name, 'manifest_upstream': man_upstream, 'file_upstream': None}}
        # Get local manifest
        if (path / 'MANIFEST.json').exists():
            with open(path / 'MANIFEST.json') as mf:
                try: manif = json.load(mf)
                except json.JSONDecodeError as e:
                    self.logger.error(f'Local manifest for {name} is corrupted: {e}')
                    if man_upstream is None: return None
                    self.logger.warning(f'Attempting to refresh local manifest for {name}...')
                    manif = dict(iman)
            old_manif = dict(manif)
            if manif['_metadata'].get('ignore', False):
                self.logger.warning(f'Local manifest for {name} would like to be ignored, not checking')
                return manif
        else:
            if man_upstream is not None:
                self.logger.warning(f'Local manifest for {name} missing, will have to obtain later')
                manif = {'_metadata': {'name': name, 'manifest_upstream': man_upstream_base, 'file_upstream': None}}
            else:
                raise FileNotFoundError(f'Local manifest for {name} missing')
        # Get upstream manifest
        with requests.get(man_upstream or manif['_metadata']['manifest_upstream']) as r:
            if r.status_code != 200:
                self.logger.error(f'Could not fetch manifest for {name}, got HTTP status code: {r.status_code}')
                return None
            try:
                uman = r.json()
            except json.JSONDecodeError as e:
                self.logger.error(f'Upstream manifest for {name} appears to be corrupted: {e}')
                return None
        # Compare manifests
        if manif == uman:
            self.logger.debug(f'Upstream and local manifests for {name} match, no need to update')
            return manif
        ## Test for upstream manifest URL differences
        if manif['_metadata']['manifest_upstream'] != uman['_metadata']['manifest_upstream']:
            osource = manif['_metadata']['manifest_upstream']
            self.logger.error(f'Local manifest for {name} lists manifest upstream of {osource}, which differs from fetched manifest listing {uman["_metadata"]["manifest_upstream"]}. Updating local manifest to reflect new manifest upstream and resetting...')
            if uman['_metadata']['manifest_upstream'] in past_upstreams.get(name, set()):
                raise Exception(f'Circular manifest upstream cycle detected for manifest {name}, can not safely continue!')
            manif['_metadata']['manifest_upstream'] = uman['_metadata']['manifest_upstream']
            with open(path / 'MANIFEST.json', 'w') as f:
                json.dump(manif, f, indent=4)
            self.logger.info(f'Wrote new manifest for {name}, resetting...')
            past_upstreams[name] = (past_upstreams.get(name) or set()) | {osource, manif['_metadata']['manifest_upstream']}
            return self.check_manifest(name, path, known_differs=True, past_upstreams=past_upstreams)
        ## Test for upstream file URL differences
        if manif['_metadata']['file_upstream'] != uman['_metadata']['file_upstream']:
            self.logger.info(f'Local manifest for {name} lists file upstream of {manif["_metadata"]["file_upstream"]}, which differs from fetched manifest listing of {uman["_metadata"]["file_upstream"]}. Updating local manifest to reflect new file upstream')
            manif['_metadata']['file_upstream'] = uman['_metadata']['file_upstream']
            known_differs = True
        ## Update local manifest
        m = manif['_metadata'].get('method', 'hash')
        for f,h in uman.items():
            if f.startswith('_'): continue
            if f in manif:
                if manif[f] == 'SKIP':
                    self.logger.warning(f'Local manifest for {name} would like file {f} to be ignored ("SKIP"), not checking')
                    continue
                if manif[f] == h:
                    self.logger.info(f'Local manifest for {name} has up-to-date {m} for file {f}')
                    continue
                self.logger.info(f'Local manifest for {name} has an outdated {m} for file {f}')
            else: self.logger.warning(f'Local manifest for {name} is missing file {f}')
            self.logger.info(f'Updating file {f} in local manifest for {name}')
            manif[f] = h
        # Check for stale files
        stale = uman.keys() ^ manif.keys()
        if stale: self.logger.warning(f'Local manifest for {name} describes the following stale files: {", ".join(stale)}')
        # Write back to manifest
        if (manif == old_manif) and not known_differs: self.logger.info(f'Local manifest unchanged')
        else:
            self.logger.info(f'Local manifest for {name} updated, writing back to file')
            with open(path / 'MANIFEST.json', 'w') as f:
                json.dump(manif, f, indent=4)
            self.logger.debug(f'Wrote new manifest for {name}')
        return manif
    def execute_manifest(self, manif: dict, path: Path, verifyer_and_redownloader: typing.Callable[[dict, Path, str], None] | None = None):
        self.logger.info(f'Executing manifest {manif["_metadata"]["name"]}')
        assert manif['_metadata'].get('method', 'hash') in {'hash', 'version'}
        if manif['_metadata'].get('ignore', False):
            self.logger.warning(f'Manifest {manif["_metadata"]["name"]} would like to be ignored, not checking')
            return
        if not len(tuple(k for k in manif.keys() if not k.startswith('_'))):
            self.logger.warning(f'Manifest {manif["_metadata"]["name"]} seems to be empty?')
            return
        self.logger.info(f'Distributing threads to verify manifest {manif["_metadata"]["name"]}, checking by {manif["_metadata"].get("method", "hash")}')
        with multiprocessing.Pool() as p:
            p.starmap(verifyer_and_redownloader or self.verify_hash_or_redownload, ((manif, path, file) for file in manif if not file.startswith('_')))
    def verify_hash_or_redownload(self, manif: dict, base: Path, file: str):
        if manif[f] == 'SKIP':
            self.logger.warning(f'Manifest {manif["_metadata"]["name"]} would like file {file} to be ignored ("SKIP"), not checking')
            return
        self.logger.debug(f'Checking hash for {manif["_metadata"]["name"]}\'s {file} [{self.algorithm}]')
        if manif['_metadata'].get('method', 'hash') == 'hash':
            with (path / file).open('rb') as f:
                hd = hashlib.file_digest(f, self.algorithm).hexdigest()
        else:
            raise NotImplementedError('This function should only ever be for used for hash-based manifests!')
        self.logger.debug(f'{name} local {file}: {local}\n{name} manif {file}: {manif[file]}')
        if local == manif[f]:
            self.logger.info(f'{name} local {file} matches manifest')
            return
        self.logger.warning(f'{name} local {file} does not match manifest, downloading new file')
        self.download_file(base / file, f'{manif["_metadata"]["file_upstream"]}/{file}')
    def download_file(self, f: Path, u: str):
        self.logger.warning(f'Downloading {u} to {f}')
        
