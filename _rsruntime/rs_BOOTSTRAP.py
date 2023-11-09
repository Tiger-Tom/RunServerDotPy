#!/bin/python3

#> Imports
import sys
from pathlib import Path
import logging
import logging.handlers
import json
from urllib import request
import traceback
# Typing
import typing
import types
# Cryptography
import hashlib
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey as PubKey
#</Imports

#> Header >/
class Bootstrapper:
    __slots__ = ('root_logger', 'logger', 'Manifest')
    # Remotes
    #dl_man = 'https://gist.githubusercontent.com/Tiger-Tom/85a2e52d7f8550a70a65b749f65bc303/raw/8a922bb83e9cb724e1913082113168f4e3ccc99e/manifest.json'
    dl_man = 'http://0.0.0.0:8000/manifest.json'
    dl_timeout = 10
    # Logger formats
    log_fmt_short = '[$asctime] [$name/$threadName/$levelname] $message'
    log_fmt_long = '[$asctime] [$name/$processName:$threadName<$module.$funcName[$lineno]>/$levelname] $message'
    date_fmt_short = '%H:%M:%S'
    date_fmt_long = '%Y-%m-%d %H:%M:%S'
    # Misc. config
    algorithm = hashlib.sha1
    minimum_vers = (3, 12, 0)

    def __init__(self):
        self.logger = self.setup_logger().getChild('BS')
        self.Manifest = types.MethodType(self._Manifest, self)

    # Pre-bootstrap setup
    ## Check Python version
    def ensure_python_version(self):
        if sys.version_info > self.minimum_vers:
            raise NotImplementedError(f'Python version {".".join(sys.version_info[:3])} doesn\'t meet the minimum requirements, needs {".".join(minimum_vers)}')
    ## Setup logging
    def setup_logger(self) -> logging.Logger:
        log_path = (Path.cwd() / '_rslog')
        log_path.mkdir(exist_ok=True)
        # Setup formatters
        stream_fmt = logging.Formatter(
            self.log_fmt_long if '--verbose-log-headers' in sys.argv[1:] else self.log_fmt_short,
            self.date_fmt_long if '--verbose-log-headers' in sys.argv[1:] else self.date_fmt_short,
            style='$')
        file_fmt = logging.Formatter(self.log_fmt_long, self.date_fmt_long, style='$')
        # Configure logger
        logger = logging.getLogger('RS')
        logger.setLevel(logging.DEBUG if '--debug' in sys.argv[1:] \
                        else logging.INFO if '--verbose' in sys.argv[1:] \
                        else logging.WARNING)
        logger.propogate = False
        ## Add handlers
        ### Stream handler
        stream_h = logging.StreamHandler()
        stream_h.setFormatter(stream_fmt)
        logger.addHandler(stream_h)
        ### File handler
        file_h = logging.handlers.TimedRotatingFileHandler(log_path / 'RunServer.log', when='H', interval=2, backupCount=24) # keeps logs for 48 hours
        file_h.setFormatter(file_fmt)
        # Set loglevel names
        logging.addLevelName(logging.DEBUG, 'DBG')
        logging.addLevelName(logging.INFO, 'INF')
        logging.addLevelName(logging.WARNING, 'WRN')
        logging.addLevelName(logging.ERROR, 'ERR')
        logging.addLevelName(logging.CRITICAL, 'CRT')
        # Finish up
        self.root_logger = logger
        return logger
    
    # Bootstrapping
    ## Base function
    def bootstrap(self):
        mp = Path('_rsruntime/MANIFEST.json')
        if not mp.exists():
            self.logger.error(f'Manifest at {mp} does not exist, attempting to download')
            try: request.urlretrieve(self.dl_man, mp)
            except Exception as e:
                self.logger.fatal(f'Could not fetch manifest from {self.dl_man}:\n{"".join(traceback.format_exception(e))}')
                raise FileNotFoundError(f'Cannot continue without {mp} which could not be retrieved from {self.dl_man}') from None
        self.logger.info(f'Loading in {mp}')
        man = self.Manifest(mp)
        man.execute()

    # Manifest
    class _Manifest:
        __slots__ = ('bs', 'path', 'manif', 'meta')
        def __init__(self, bs, path: Path, manif: dict | None = None):
            self.bs = bs
            self.path = path
            if manif is None:
                with self.path.open('r') as f:
                    self.manif = json.load(f)
            else: self.manif = manif
            self.meta = self.manif['_metadata']
        def __getattr__(self, attr: str):
            if not attr.startswith('m_'):
                return super().__getattribute__(attr)
            elif (attr[2:] not in self.meta): raise AttributeError(attr[2:])
            return self.meta[attr[2:]]
        @staticmethod
        def _decode(val: str | tuple[int] | list[int]) -> bytes:
            return base64.b85decode(val) if isinstance(val, str) else bytes(val)
        @property
        def key(self) -> PubKey:
            '''The public key stored in this manifest'''
            return PubKey.from_public_bytes(self._decode(self.m_public_key))
        @property
        def sig(self) -> bytes:
            '''The signature stored in this manifest'''
            return self._decode(self.m_signature)
        @staticmethod
        def _compile(datas_heads: tuple[tuple[str | None]], datas_body: tuple[tuple[str, bytes]]) -> bytes:
            '''Joins data, just like compile() in the devel mkmanifest.py script'''
            ba = bytearray()
            byte_me = lambda n: bytes((*(byte_me(n // 256) if n >= 256 else b''), n % 256))
            for dh in datas_heads:
                for d in dh:
                    if d is None: ba.append(255)
                    elif isinstance(d, int):
                        if d < 0: raise ValueError(f'Cannot compile negative numbers ({d})')
                        ba.extend(byte_me(d))
                    elif isinstance(d, str): ba.extend(d.encode())
                    else: raise TypeError(f'Cannot compile {d!r} (type {type(d)})')
                    ba.append(0)
                ba.append(0)
            ba.append(0)
            for d0,d1 in datas_body:
                ba.extend(d0.encode())
                ba.append(255)
                ba.extend(d1)
                ba.append(0)
            return bytes(ba)
        def compile(self) -> bytearray:
            '''
                Join all important parts of the manifest, useful for hashing or signing
                    works the same as the similar part of the mkmanifest.py devel utility
            '''
            return self._compile(
                (
                    (self.m_name, self.m_manifest_upstream, self.m_file_upstream),
                    tuple(v for v in self.m_creation.values() if not isinstance(v, dict)),
                    ((None,) if self.m_creation['system'] is None else self.m_creation['system'].values()),
                ),
                (tuple(((f, self._decode(h)) for f,h in self.manif.items() if not f.startswith('_')))),
            )
        def verify(self, k: PubKey):
            '''Compile this manifest (using self.compile()) and verify it with the given public key'''
            self.bs.logger.warning(f'Compiling {self.m_name} for verification')
            dat = bytes(self.compile())
            self.bs.logger.debug(f'Compiled:\n {dat}')
            self.bs.logger.warning(f'Verifying {self.m_name} ({self.m_signature})')
            self.bs.logger.debug(f'Key:\n {k.public_bytes_raw()}')
            k.verify(self.sig, dat)
            self.bs.logger.info(f'{self.m_name} passed verification')
        def upstream_manif(self, verify: bool = True) -> typing.Self | None:
            '''Fetches the upstream manifest from the manifest_upstream metadata field of this manifest'''
            self.bs.logger.warning(f'Fetching {self.m_name} upstream from {self.m_manifest_upstream}')
            with request.urlopen(self.m_manifest_upstream, timeout=self.bs.dl_timeout) as r:
                newmanif = self.__class__(self.bs, self.path, json.load(r))
            if verify:
                try: newmanif.verify(self.key)
                except Exception as e:
                    self.bs.logger.fatal(f'Upstream manifest {self.m_name} fetched from {self.m_manifest_upstream} failed verification! ({e})')
                    if input('Use anyway? (y/N) >').lower().startswith('y'): return newmanif
                    else: return None
            return newmanif
        def update(self, new_manif: typing.Self, override: bool = False) -> typing.Self | None:
            '''
                This function does three things:
                - Prints out debug information
                - Fetches and writes the new manifest
                - Creates and returns the new manifest object to be executed, or None if this manifest wishes to be ignored
            '''
            self.bs.logger.warning(f'Updating manifest {self.m_name}')
            if self.meta.get('ignore', False):
                self.bs.logger.error(f'{self.m.name} would like to be ignored, skipping')
                return self
            for f in self.manif.keys() - new_manif.keys():
                if f.startswith('_'): continue
            stale = tuple(f for f in self.manif.keys() - new_manif.keys() if not f.startswith('_'))
            if stale:
                self.bs.logger.error(f'The following stale file(s) no longer exist in the new manifest:\n- {"\n- ".join(stale)}')
            else: self.bs.logger.info('No stale files found')
            new = tuple(f for f in new_manif.keys() - self.manif.keys() if not f.startswith('_'))
            if new: self.bs.logger.warning(f'The following new file(s) will need to be created:\n- {"\n- ".join(new)}')
            else: self.bs.logger.info('No new files found')
            with open(self.path, 'w') as f:
                json.dump(new_manif.manif, f)
            return new_manif
        def execute(self):
            self.bs.logger.warning(f'Executing manifest {self.m_name}')
            try: self.verify(self.key)
            except Exception as e: self.bs.logger.fatal(f'Local manifest {self.m_name} failed verification ({e}), continuing anyway')
            to_install = []
            to_replace = []
            for f,h in self.manif.items():
                if f.startswith('_'): continue
                if not (self.path.parent / f).exists():
                    self.bs.logger.error(f'Local {f} does not exist, redownloading')
                    to_install.append(f)
                    continue
                self.bs.logger.info(f'Checking {f}')
                self.bs.logger.debug(self.path.parent / f)
                with open(self.path.parent / f, 'rb') as fd:
                    dig = hashlib.file_digest(fd, self.bs.algorithm).digest()
                    fh = base64.b85encode(dig).decode() if isinstance(h, str) else tuple(dig)
                self.bs.logger.debug(f'manif: {h}')
                self.bs.logger.debug(f'local: {fh}')
                if h == fh:
                    self.bs.logger.info(f'Local {f} matches manifest')
                    continue
                self.bs.logger.warning(f'Local {f} does not match manifest, need to redownload!')
                to_replace.append(f)
            changes = set()
            if to_install:
                print('Files to install:')
                for f in to_install:
                    print(f'{Path(self.m_file_upstream, f)} -> {self.path.parent / f}')
                if ('--unattended' in sys.argv[1:]) or ('--unattended-install' in sys.argv[1:]) or not input('Install okay? (Y/n) >').lower().startswith('n'):
                    for f in to_install:
                        self.download_file(f)
                        changes.add(f)
            if to_replace:
                print('Files to replace:')
                for f in to_replace: print(f'- {f}')
                if ('--unattended' in sys.argv[1:]) or ('--unattended-replace' in sys.argv[1:]) or input('Replace okay? (y/N) >').lower().startswith('y'):
                    for f in to_replace:
                        self.download_file(f)
                        changes.add(f)
            if changes:
                print(f'{len(to_install+to_replace)} files were downloaded')
                for f in changes: print(f'- {f}')
                if ('--unattended' in sys.argv[1:]) or not input('Filesystem changes were made; rerun execute to verify checksums? (Y/n) >').lower().startswith('n'):
                    execute()
        def download_file(self, f: str):
            self.bs.logger.warning(f'Downloading {Path(self.m_file_upstream, f)} to {self.path.parent / f}...')
            request.urlretrieve(Path(self.m_file_upstream, f), self.path.parent / f)
