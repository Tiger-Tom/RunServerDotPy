#!/bin/python3

from __future__ import annotations

#> Imports
import sys
from urllib import request
import argparse
import functools
# Files
from importlib.machinery import SourceFileLoader
from pathlib import Path
import gzip
import shutil
# Logging / info
import logging, logging.handlers
import traceback
# Typing
import typing
import types
# Manifest dependencies
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from collections import UserDict
from io import StringIO
## Parser/writers
from configparser import ConfigParser
from ast import literal_eval
import json
## Cryptography
import hashlib
import base64
try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as EdPrivK, Ed25519PublicKey as EdPubK
except ModuleNotFoundError:
    raise ModuleNotFoundError('Cannot find crytography module, perhaps you need to `pip install cryptography`?')
#</Imports

RS = NotImplemented

#> Header >/
class Bootstrapper:
    '''Does the necessary startup and take-down for RunServer'''

    __slots__ = ('args', 'args_unknown', 'is_dry_run', 'root_logger', 'logger', 'Manifest', 'base_manifest', 'shutdown_callbacks', 'is_closed', '__contained_RS_module', '__contained_RS')
    # Remotes
    dl_man = 'https://raw.githubusercontent.com/Tiger-Tom/RunServerDotPy/v3.x.x/_rsruntime/MANIFEST.ini'
    # Logger formats
    log_fmt_short = '[$asctime] [$name/$threadName/$levelname]: $message'
    log_fmt_long = '[$asctime] [$name/$processName:$threadName<$module.$funcName[$lineno]>/$levelname]: $message'
    date_fmt_short = '%H:%M:%S'
    date_fmt_long = '%Y-%m-%d %H:%M:%S'
    # Misc. config
    minimum_vers = (3, 12, 0)

    def __init__(self):
        self.ensure_python_version()
        self.parse_arguments()
        self.logger = self.setup_logger().getChild('BS')
        self.Manifest = Manifest
        self.shutdown_callbacks = set()
        self.is_closed = False

#pragma:makedoc:skip:@until

    # Pre-bootstrap setup
    ## Check Python version
    @classmethod
    def ensure_python_version(cls):
        '''Ensure that the Python version meets the minimum requirements'''
        if sys.version_info < cls.minimum_vers:
            raise NotImplementedError(f'Python version {".".join(map(str, sys.version_info[:3]))} doesn\'t meet the minimum requirements, needs {".".join(map(str, cls.minimum_vers))}')
    ## Argument parser
    def parse_arguments(self, args=None):
        '''Generate and ArgumentParser and parse (known) arguments'''
        p = argparse.ArgumentParser('RunServer.py')
        log_grp = p.add_argument_group('Logging')
        log_l_grp = log_grp.add_mutually_exclusive_group()
        log_l_grp.add_argument('--verbose', help='Show more information in stderr logging (loglvl=INFO)', action='store_true')
        log_l_grp.add_argument('--debug', help='Show even more information in stderr logging (loglvl=DEBUG)', action='store_true')
        log_l_grp.add_argument('--quiet', help='Show less information in stderr logging (loglvl=WARNING)', action='store_true')
        log_grp.add_argument('--verbose-headers', help='Show longer headers in stderr logs', action='store_true')
        log_grp.add_argument('--no-color', help='Don\'t color output to stderr', action='store_true')
        p.add_argument('--update-only', help='Only download/update and execute the bootstrapper manifest, don\'t start the server', action='store_true')
        unat_grp_ = p.add_argument_group('Unattended')
        unat_grp = unat_grp_.add_mutually_exclusive_group()
        unat_grp.add_argument('--unattended-install', help='When executing manifests, don\'t ask before installing new files', action='store_true')
        unat_grp.add_argument('--unattended-replace', help='When executing manifests, don\'t ask before replacing existing files', action='store_true')
        unat_grp.add_argument('--unattended', help='Combined effects of --unattended-install and --unattended-replace', action='store_true')
        p.add_argument('--dry-run', help='Indicate to the entrypoint that this should be a dry-run', action='store_true')
        self.args, self.args_unknown = p.parse_known_args(args)
        self.is_dry_run = self.args.dry_run
    ## Setup logging
    def setup_logger(self) -> logging.Logger:
        '''Sets up self.logger, as well as logging.INFOPLUS/IRRECOVERABLE and Logger.infop/irrec()'''
        log_path = (Path.cwd() / '_rslog')
        log_path.mkdir(exist_ok=True)
        # Create new logging levels
        ## INFO+ level
        logging.INFOPLUS = logging.INFO + ((logging.WARNING - logging.INFO) // 2)
        logging.getLoggerClass().infop = functools.partialmethod(logging.getLoggerClass().log, logging.INFOPLUS)
        ## Irrecoverable level
        logging.IRRECOVERABLE = logging.FATAL * 2
        logging.getLoggerClass().irrec = functools.partialmethod(logging.getLoggerClass().log, logging.IRRECOVERABLE)
        # Setup formatters
        class ColoredFormatter(logging.Formatter):
            FG_GRAY        = '\x1b[37m'
            FG_DGREEN      = '\x1b[32m'
            FG_LGREEN      = '\x1b[92m'
            FG_YELLOW      = '\x1b[93m'
            FG_LRED        = '\x1b[91m'
            FG_DRED        = '\x1b[31m'
            FG_GRAY_BG_RED = '\x1b[37;41m'
            RESET          = '\x1b[0m'

            _level_to_color = {
                logging.DEBUG:         FG_GRAY,
                logging.INFO:          FG_DGREEN,
                logging.INFOPLUS:      FG_LGREEN,
                logging.WARNING:       FG_YELLOW,
                logging.ERROR:         FG_LRED,
                logging.FATAL:         FG_DRED,
                logging.IRRECOVERABLE: FG_GRAY_BG_RED,
            }

            def format(self, record: logging.LogRecord) -> str:
                record.msg = f'{self._level_to_color[record.levelno]}{record.msg}{self.RESET}'
                return super().format(record)
        stream_fmt = (logging.Formatter if self.args.no_color else ColoredFormatter)(
            self.log_fmt_long if self.args.verbose_headers else self.log_fmt_short,
            self.date_fmt_long if self.args.verbose_headers else self.date_fmt_short,
            style='$')
        file_fmt = logging.Formatter(self.log_fmt_long, self.date_fmt_long, style='$')
        # Configure logger
        logger = logging.getLogger('RS')
        logger.setLevel(logging.DEBUG)
        logger.propogate = False
        ## Add handlers
        ### Stream handler
        stream_h = logging.StreamHandler()
        stream_h.setFormatter(stream_fmt)
        stream_h.setLevel(logging.DEBUG if self.args.debug else logging.INFO if self.args.verbose else logging.WARNING if self.args.quiet else logging.INFOPLUS)
        logger.addHandler(stream_h)
        ### Main file handler
        # stores verbose logs (level=INFO)
        # rotates logs when it reaches 1/2 MiB, keeps 12 previous logs
        # compresses logs with gzip
        mfile_h = logging.handlers.RotatingFileHandler(log_path / 'RunServer.log', maxBytes=1024**2 / 2, backupCount=12)
        mfile_h.setFormatter(file_fmt)
        mfile_h.setLevel(logging.INFO)
        def mfile_h_rotator(src, dst):
            with open(src, 'rb') as srcd, gzip.open(dst, 'wb') as dstd:
                shutil.copyfileobj(srcd, dstd)
            Path(src).unlink()
        mfile_h.namer = lambda n: f'{n}.log.gz'
        mfile_h.rotator = mfile_h_rotator
        logger.addHandler(mfile_h)
        ### Debug file handler
        # stores all logs (level=DEBUG)
        # overwrites upon startup
        # forcibly deletes itself if it ever manages to reach the ungodly size of 8 MiB
        dfile_h = logging.handlers.RotatingFileHandler(log_path / 'RunServer.VERBOSE.log', mode='w', maxBytes=8 * 1024**2, backupCount=1)
        dfile_h.setFormatter(file_fmt)
        dfile_h.setLevel(logging.DEBUG)
        dfile_h.rotator = lambda src,dst: Path(src).unlink()
        logger.addHandler(dfile_h)
        # Set loglevel names
        logging.addLevelName(logging.DEBUG,         'DEBG')
        logging.addLevelName(logging.INFO,          'INFO')
        logging.addLevelName(logging.INFOPLUS,      'INF+')
        logging.addLevelName(logging.WARNING,       'WARN')
        logging.addLevelName(logging.ERROR,         'ERRO')
        logging.addLevelName(logging.CRITICAL,      'CRIT')
        logging.addLevelName(logging.IRRECOVERABLE, 'IREC')
        # Finish up
        self.root_logger = logger
        return logger

    # Bootstrapping
    ## Base function
    def bootstrap(self, close_after: bool = True):
        '''Executes the base manifest, then accesses, assigns, and chainloads the entrypoint'''
        self.run_base_manifest()
        if self.args.update_only:
            self.logger.fatal('--update-only argument supplied, exiting')
            return
        self.__contained_RS_module = self.access_entrypoint('_rsruntime/rs_ENTRYPOINT.py')
        self.__contained_RS = self.stage_entrypoint(self.__contained_RS_module)
        global RS
        if RS != NotImplemented:
            self.logger.warning(f'Tried to set {__file__}-level RS, but it appears to have already been set?')
        else: RS = self.__contained_RS
        self.init_entrypoint(RS)
        self.chainload_entrypoint(RS)
        if close_after: self.close()
    ## Install and execute base manifest
    def run_base_manifest(self):
        '''Executes the base manifest (_rsruntime/MANIFEST.ini)'''
        mp = Path('_rsruntime/MANIFEST.ini')
        if not mp.exists():
            self.logger.error(f'Manifest at {mp} does not exist, attempting to download')
            try: request.urlretrieve(self.dl_man, mp)
            except Exception as e:
                self.logger.fatal(f'Could not fetch manifest from {self.dl_man}:\n{"".join(traceback.format_exception(e))}')
                return
        self.logger.info(f'Loading in {mp}')
        self.base_manifest = Manifest.from_file(mp)()
    ## Load entrypoint
    def access_entrypoint(self, ep: str) -> types.ModuleType:
        '''Loads the entrypoint's surrounding module'''
        fl = SourceFileLoader(f'{__package__}.RS', ep)
        self.logger.warning(f'ACCESSING ENTRYPOINT: {fl}')
        return fl.load_module()
    def stage_entrypoint(self, rs_outer: types.ModuleType) -> 'rs_outer.RunServer':
        '''Stages the entrypoint's class'''
        self.logger.warning(f'STAGING ENTRYPOINT: {rs_outer.RunServer.__new__}')
        return rs_outer.RunServer.__new__(rs_outer.RunServer)
    def init_entrypoint(self, rs: 'RS'):
        '''Initializes the entrypoint's class (with self as an argument)'''
        self.logger.warning(f'INITIALIZING ENTRYPOINT: {rs.__init__}')
        rs.__init__(self)
    def chainload_entrypoint(self, rs: 'RS'):
        '''Runs the entrypoint's __call__ method'''
        self.logger.warning(f'ENTERING ENTRYPOINT: {rs.__call__}')
        rs()
        self.logger.fatal('EXITED ENTRYPOINT')

#pragma:makedoc:skip:&until

    # Utility functions
    ## Shutdown functions
    def close(self, do_exit: bool | int = False):
        '''Executes all shutdown callbacks and closes logging (logging.shutdown()), and exits with exit code do_exit if it isn't False'''
        if self.is_closed: return
        self.logger.irrec('Instructed to perform orderly shutdown, executing shutdown callbacks...')
        for h in self.shutdown_callbacks: h()
        self.logger.irrec(f'Closing logger{f" and exiting with code {do_exit}" if do_exit is not False else ""}, goodbye!')
        logging.shutdown()
        if do_exit is False: self.is_closed = True
        else: exit(do_exit)
    def register_onclose(self, cb: typing.Callable[[], None]):
        '''Registers a function to run when self.close() is called'''
        self.shutdown_callbacks.add(cb)

# Manifests
## Manifest typing
ManifestDict__ = typing.TypedDict("ManifestDict['_']", {
    'encoding': str,
    'hash_algorithm': typing.Literal[*hashlib.algorithms_available],
    'pubkey': str,
    'signature': str,
})
ManifestDict_creation = typing.TypedDict("ManifestDict['creation']", {
    'created_at': int,
    'updated_at': int,
    'by': str,
    'aka': str | None,
    'contact': str | None,
    'nupdates': int,
})
ManifestDict_metadata = typing.TypedDict("ManifestDict['metadata']", {
    'name': str,
    'description': str | None,
    'manifest_upstream': str,
    'content_upstream': str,
    'meta_version': typing.NotRequired[str],
})
ManifestDict_system = typing.TypedDict("ManifestDict['system']", {
    'os_name': str | None,
    'platform': str | None,
    'architecture': str | None,
    'python_version': tuple[int, int, int, str, int] | tuple[int, int, int] | None,
    'python_implementation': str | None,
    'os_release': str | None,
    'os_version': str | None,
    'hostname': str | None,
    '_info_level': int,
})
ManifestDict_files = typing.Dict[str, str]
ManifestDict_ignore = typing.TypedDict("ManifestDict['ignore']", {
    'skip_upstream_upgrade': bool,
    'skip_all_files': bool,
    'skip_files': tuple[str, ...],
}, total=False)
ManifestDict_format = typing.TypedDict("ManifestDict['format']", {
    'terse': str,
    'normal': str,
    'verbose': str,
    'verbose+': str,
    'datefmt': str,
    'aliasfmt': tuple[str, str],
    'sysfmt': tuple[str, str, str],
})
ManifestDict = typing.TypedDict('ManifestDict', {
    '_': ManifestDict__,
    'creation': ManifestDict_creation,
    'metadata': ManifestDict_metadata,
    'system': ManifestDict_system,
    'files': ManifestDict_files,
    'ignore': typing.NotRequired[ManifestDict_ignore],
    'format': typing.NotRequired[ManifestDict_format],
})
## Manifest class
class Manifest(UserDict):
    __slots__ = ('own_path', 'own_type', 'base_path', 'logger')
    type_to_suffix = {
        'ini': '.ini',
        'json': '.json',
    }; suffix_to_type = {v: k for k,v in type_to_suffix.items()}
    DOWNLOAD_TIMEOUT = 5

    def __call__(self, *,
                 skip_verify_local: bool = False, skip_update: bool = False, skip_execute: bool = False,
                 ask_download: bool = True, ask_execute: bool = True) -> typing.Self:
        '''Verifies, upgrades, and executes this manifest'''
        self.logger.infop(f'Local manifest: {self._log_info()}')
        if not skip_verify_local:
            try: self.verify()
            except InvalidSignature:
                self.logger.fatal('Local manifest has an invalid signature! Will continue anyway, but keep in mind that upstream manifests may fail as well')
        self.upgrade(ask_download)
        self.logger.infop(f'(New) Local manifest: {self._log_info()}')
        self.execute(ask_execute)
        return self
    # Self-updating
    def upgrade(self, ask: bool = True, override: bool = False):
        '''Updates the local manifest, verifying it and notifying the user of modified and stale files'''
        if (not override) and self.get('ignore', {}).get('skip_upstream_upgrade', False):
            self.logger.fatal(f'Manifest {self.name} requested to not be upgraded, skipping')
            return
        owntype = getattr(self, 'own_type', self.suffix_to_type.get(self.own_path.suffix, None))
        if owntype is None:
            owntype = next(self.type_to_suffix.keys())
            self.logger.error(f'Could not automatically determine current type of manifest {self.name} at {self.own_path}, will write as {owntype}')
        self.logger.infop(f'Updating manifest {self.name}, upstream is {self["metadata"]["manifest_upstream"]}')
        try: newmanif = self.from_remote(self['metadata']['manifest_upstream'])
        except Exception as e:
            self.logger.fatal(f'Could not update manifest {self.name} (from {self["metadata"]["manifest_upstream"]}), got error:\n{"".join(traceback.format_exception(e))}')
            return
        if self.data == newmanif.data and False:
            self.logger.infop(f'Upstream manifest matches local manifest, no upgrade needed')
            return
        if self.d_pubkey != newmanif.d_pubkey:
            self.logger.warning(f'Local manifest {self.name} has a different public key than upstream manifest, it will likely fail verification:\n{self["_"]["pubkey"]}\n{newmanif["_"]["pubkey"]}')
        self.logger.info(f'Verifying {newmanif.name} on {self["_"]["pubkey"]}')
        try: self.verify(newmanif)
        except InvalidSignature:
            self.logger.fatal('Manifest {newmanif.name} failed verification')
            if (not ask) or input('Install manifest anyway? (y/N').lower().startswith('y'): return
        for f in (self.d_files.keys() - newmanif.d_files.keys()):
            self.logger.error(f'Stale file {f} is in local manifest {self.name} but not upstream manifest (may need to be removed manually)')
        for f in (newmanif.d_files.keys() - self.d_files.keys()):
            self.logger.warning(f'New file {f} needs to be downloaded according to upstream manifest {newmanif.name}')
        self |= newmanif
        self.logger.infop(f'New manifest {self.name} folded into local, writing back local at {self.own_path} as {owntype}')
        with self.own_path.open('w') as f: getattr(self, f'render_{owntype}')(f)
    # Execution
    def execute(self, ask: bool = True, override: bool = False):
        '''Executes the manifest, installing new files and replacing files that don't match the stored hashes'''
        self.logger.infop(f'Executing manifest {self.name} on {self.base_path}')
        if (not override) and self.get('ignore', {}).get('skip_all_files', False):
            self.logger.fatal(f'Manifest {self.name} requested that all files be skipped, not executing')
            return
        alg = self["_"]["hash_algorithm"]
        ignore = self.get('ignore', {}).get('skip_files', set())
        to_install = []; to_replace = []
        for fn,target_hash in self.i_d_files():
            self.logger.info(f'Checking file {fn} against {self["files"][fn]} via {alg}')
            if fn in ignore:
                self.logger.fatal(f'Manifest {self.name} requested that file {fn} be skipped')
                continue
            if not (self.base_path / fn).exists():
                to_install.append(fn)
                continue
            real_hash = hashlib.new(alg, (self.base_path / fn).read_bytes()).digest()
            self.logger.info(f'{fn}:\n target: {self["files"][fn]}\n actual: {base64.b85encode(real_hash).decode()}')
            if real_hash != target_hash:
                self.logger.warning(f'{fn} actual hash differs from target hash, will replace')
                to_replace.append(fn)
        fetch = set(); sep = '\n - '
        if to_install:
            self.logger.warning(f'The following new files will be installed:{sep}{sep.join(str(self.base_path / p) for p in to_install)}')
            if not (ask and input('Install files? (Y/n) >').lower().startswith('n')): fetch.update(to_install)
        if to_replace:
            self.logger.warning(f'The following local files will be replaced:{sep}{sep.join(str(self.base_path / p) for p in to_replace)}')
            if (not ask) or input('Replace files? (y/N) >').lower().startswith('y'): fetch.update(to_replace)
        if not fetch:
            self.logger.warning('Nothing to do')
            return
        self.logger.warning(f'Fetching {len(fetch)} file(s); dispatching {ThreadPoolExecutor.__qualname__}')
        with ThreadPoolExecutor(thread_name_prefix='ManifestFileDownloader') as tpe:
            tuple(tpe.map(self._install_file, fetch))
    ## Downloading
    def _install_file(self, filename: str):
        url = '/'.join((self['metadata']['content_upstream'].rstrip('/'), filename))
        path = self.base_path / filename
        bkppath = path.with_suffix('.'.join((path.suffix, 'old')))
        if path.exists():
            d = path.read_bytes()
            self.logger.infop(f'Copying {path} ({len(d)} byte(s)) to {bkppath}')
            bkppath.write_bytes(d)
        else: path.parent.mkdir(parents=True, exist_ok=True)
        self.logger.info(f'Fetching {url} to {path}')
        try:
            with request.urlopen(url) as r:
                d = r.read(); path.write_bytes(d)
            self.logger.infop(f'Downloaded {url} ({len(d)} byte(s)) to {path}')
        except Exception as e:
            self.logger.error(f'An error occured whilst fetching {url} to {path}:\n{"".join(traceback.format_exception(e))}')
            if path.exists():
                if (ld := len(path.read_bytes())):
                    self.logger.warning(f'{path} appears to still exist (holding {ld} byte(s)), leaving it in the hopes that it is functional')
                    return
                self.logger.error(f'{path} appears to still exist, but holds no data')
            if bkppath.exists():
                d = bkppath.read_bytes()
                if len(d):
                    self.logger.warning(f'A backup exists at {bkppath}, copying {len(d)} byte(s) to {path} in the hopes that it is functional')
                    path.write_bytes(d)
                    return
                self.logger.error(f'A backup exists at {bkppath}, but holds no data')
            self.logger.fatal(f'No usable local versions ({path}) or backups ({bkppath}) found, the program may not function as intended')
    # Helper / compat function
    @staticmethod
    def _logger() -> logging.Logger:
        '''Ensures compatability, whether or not the logger is set up'''
        logger = logging.getLogger('RS.BS.M')
        if not hasattr(logger, 'infop'):
            logger.infop = logger.warning
        return logger
    # Constructors
    def __init__(self):
        '''Use from_dict, from_file, or from_remote instead'''
        raise TypeError('Should not be initialized here, use from_dict or from_file')
    @classmethod
    def __internal_init(cls):
        self = super().__new__(cls)
        self.logger = self._logger()
        return self
    ## Setters
    def set_path(self, *, base: Path | None = None, own: Path | None = None) -> typing.Self:
        '''Sets the manifest's "target" and "own" paths, and returns the Manifest object for chaining'''
        if base is not None: self.base_path = base
        if own is not None: self.own_path = own
        return self
    ## From
    @classmethod
    def from_dict(cls, d: ManifestDict) -> typing.Self:
        '''Initializes the UserDict superclass with a new instance of Manifest, setting d as its "data" attribute'''
        self = cls.__internal_init()
        UserDict.__init__(self, d); self.data = d
        return self
    ### From string types
    @classmethod
    def from_json(cls, jsn: str) -> typing.Self:
        '''Generates a Manifest instance from JSON text (Convenience method for Manifest.from_json(Manifest.dict_from_json_text(...)))'''
        self = cls.from_dict(cls.dict_from_json_text(jsn))
        self.own_type = 'json'
        return self
    @classmethod
    def from_ini(cls, ini: str) -> typing.Self:
        '''Generates a Manifest instance from INI text (Convenience method for Manifest.from_dict(Manifest.dict_from_ini_text(...)))'''
        self = cls.from_dict(cls.dict_from_ini_text(ini))
        self.own_type = 'ini'
        return self
    #### Dict from string types
    @staticmethod
    def dict_from_json_text(jsn: str) -> ManifestDict:
        '''Helper method to convert JSON text to a dictionary (current implementation just calls json.loads)'''
        return json.loads(jsn)
    @staticmethod
    def dict_from_ini_text(ini: str) -> ManifestDict:
        '''Helper method to convert INI text into a dict (note that interpolation is disabled and keys are case-sensitive)'''
        p = ConfigParser(interpolation=None); p.optionxform = lambda o: o; p.read_string(ini)
        return {k: {ik: literal_eval(iv) for ik,iv in v.items()} for k,v in p.items() if k != 'DEFAULT'}
    ### From files
    @classmethod
    def from_file(cls, path: Path, path_type: typing.Literal['json', 'ini'] | None = None) -> typing.Self:
        '''
            Initializes Manifest from a file.
            Can load from the following file types:
                'json': .json files
                'ini': .ini files
            If path_type is given, then attempts to load a file of that type
            Otherwise, path_type is guessed from path's suffix, using Manifest.suffix_to_type
        '''
        logger = cls._logger(); data = path.read_text()
        if path_type is None: path_type = cls.suffix_to_type.get(path.suffix, None) # Guess it through the suffix
        if path_type is None: # Try every handler
            logger.warning(f'path_type not given, and guessing it via the path\'s suffix ({path.suffix=}) failed')
            for k in cls.type_to_suffix:
                try:
                    logger.infop(f'Trying {k} handler on contents of {path}')
                    return getattr(cls, f'from_{k}')(data).set_path(base=path.parent, own=path)
                except Exception as e:
                    logger.error(f'{k} handler failed on contents of {path}:\n{"".join(traceback.format_exception(e))}')
            raise NotImplementedError(f'Cannot parse manifest from {path}, no handlers succeeded')
        if path_type not in cls.type_to_suffix: raise TypeError(f'Illegal path type {path_type!r}')
        return getattr(cls, f'from_{path_type}')(data).set_path(base=path.parent, own=path)
    @classmethod
    def from_remote(cls, url: str, path_type: typing.Literal['ini', 'json'] | None = None) -> typing.Self:
        '''Initializes Manifest from a file, has the same path_type properties of from_file'''
        logger = cls._logger()
        with request.urlopen(url, timeout=cls.DOWNLOAD_TIMEOUT) as r: data = r.read().decode()
        if path_type is None: path_type = cls.suffix_to_type.get(url[url.rindex('.'):] if ('.' in url) else '', None) # Guess it through the suffix
        if path_type is None: # Try every handler
                logger.warning(f'path_type not given, and guessing it via the URL\'s extension failed!')
                for k in cls.type_to_suffix:
                    logger.infop(f'Trying {k} handler on contents of {url}')
                    try: return getattr(cls, f'from_{k}')(data)
                    except Exception as e:
                        logger.error(f'{k} handler failed on contents of {url}:\n{"".join(traceback.format_exception(e))}')
                raise NotImplementedError(f'Cannot parse manifest from {url}, no handlers succeeded')
        if path_type not in cls.type_to_suffix: raise TypeError(f'Illegal path type {path_type!r}')
        return getattr(cls, f'from_{path_type}')(data)
    # Rendering
    JSON_ARRAY_CLEANER_A = re.compile(r'^(\s*"[^"]*":\s*)(\[[^\]]*\])(,?\s*)$', re.MULTILINE)
    JSON_ARRAY_CLEANER_B = staticmethod(lambda m: m.group(1)+(re.sub(r'\s+', '', m.group(2)).replace(',', ', '))+m.group(3))
    def render_json(self, to: typing.TextIO | None = None) -> str:
        '''Render the Manifest dictionary to JSON (if `to` is given, write it to `to` and return the JSON string)'''
        data = self.JSON_ARRAY_CLEANER_A.sub(self.JSON_ARRAY_CLEANER_B, json.dumps(self.data, sort_keys=False, indent=4))
        if to is not None: to.write(data)
        return data
    def render_ini(self, to: None | typing.TextIO = None) -> str:
        '''Render the Manifest dictionary to INI (if `to` is given, write it to `to` and return the INI string)'''
        p = ConfigParser(interpolation=None); p.optionxform = lambda o: o
        for ok,ov in self.data.items(): p[ok] = {ik: repr(iv) for ik,iv in ov.items()}
        if to is not None: p.write(to)
        sio = StringIO(); p.write(sio); return sio.getvalue()
    # Property shortcuts
    @property
    def name(self) -> str: return self['metadata']['name']
    # Data extraction
    def i_d_files(self) -> typing.Generator[tuple[str, bytes], None, None]:
        return ((k, base64.b85decode(v)) for k,v in self.data['files'].items())
    @property
    def d_files(self) -> dict[str, bytes]: return dict(self.i_d_files())
    @property
    def d_sig(self) -> bytes: return base64.b85decode(self['_']['signature'])
    @property
    def d_pubkey(self) -> EdPubK: return EdPubK.from_public_bytes(base64.b85decode(self['_']['pubkey']))
    # Compilation
    def compile(self): return self.compile_dict(self.data)
    ## Constants
    COMPILED_KEY_ORDER = ('creation', 'metadata', 'system', 'files')
    COMPILED_KEY_VALUE_SEP = 255
    COMPILED_ENTRY_SEP = 0
    ## Individual value compilers
    _val_compilers = {
        bytes: lambda b: b, str: lambda s: s.encode(),
        int: lambda n: n.to_bytes(((n.bit_length() + 1) + 7) // 8, signed=True),
        type(None): lambda v: bytes((255,)),
    }
    @classmethod
    def _compile_value(cls, val: None | bytes | str | int | tuple | list) -> bytes:
        if isinstance(val, (tuple, list)):
            return b''.join(cls._compile_value(v) for v in val)
        if type(val) not in cls._val_compilers:
            raise TypeError(f'Cannot handle type {type(val).__qualname__} (value {val!r})')
        return cls._val_compilers[type(val)](val)
    ## Dictionary compiler
    @classmethod
    def compile_dict(cls, manif: ManifestDict) -> bytes:
        '''
            Compiles dictionaries for signing
            Keys are compiled in the following order (by default, see COMPILED_KEY_ORDER): 'creation', 'metadata', 'system', 'files'
            with each inner value being added to the compiled data as (where, by default, COMPILED_KEY_VALUE_SEP is 255 and COMPILED_ENTRY_SEP is 0):
                _compile_value(outer_key), COMPILED_KEY_VALUE_SEP, _compile_value(inner_key), COMPILED_KEY_VALUE_SEP, _compile_value(value), COMPILED_KEY_VALUE_SEP, COMPILED_ENTRY_SEP
        '''
        # Bring in values for readability (and I suppose for a tiny inner loop efficiency bonus)
        compile_val = cls._compile_value
        COMPILED_KEY_VAL_SEP = cls.COMPILED_KEY_VALUE_SEP; COMPILED_ENTRY_SEP = cls.COMPILED_ENTRY_SEP
        return bytes(byte for bytes_ in ((*compile_val(outer_key), COMPILED_KEY_VAL_SEP, *compile_val(inner_key), COMPILED_KEY_VAL_SEP, *compile_val(value), COMPILED_KEY_VAL_SEP, COMPILED_ENTRY_SEP)
                    for outer_key in cls.COMPILED_KEY_ORDER for inner_key,value in manif[outer_key].items()) for byte in bytes_) # I'm sorry...
    # Verification
    def verify(self, other: typing.Self | None = None):
        '''Verifies either this manifest or another with this manifest's public key'''
        self.d_pubkey.verify((self if other is None else other).d_sig, (self if other is None else other).compile())
    # Information formatting
    DEFAULT_FORMAT = {
        'terse':   '\'{metadata.name}\' by {creation.by}',
        'normal':  '\'{metadata.name}\' by {creation.by}{f_alias} (updated {fd_updated} to rev.{creation.nupdates}): "{metadata.description}"',
        'verbose': '\'{metadata.name}\' by {creation.by}{f_alias} (meta-version: {o_metaversion})\n'
                   '{metadata.description}\n'
                   ' Created on {fd_created}, updated on {fd_updated} to rev.{creation.nupdates}\n'
                   ' Contains {n_files} file(s) hashed with {_.hash_algorithm} ({_.encoding})\n'
                   '  Signed with {_.pubkey!r} -> {_.signature!r}',
        'verbose+': ...,
        'datefmt': '%Y-%m-%d %H:%M:%S %Z',
        'aliasfmt': ('', ' (AKA "{creation.aka}")'),
        'sysfmt': ('<system info redacted>',
                   '\n  OS: {system.os_name} ({system.architecture})\n  {system.python_implementation} {f_pyver}',
                   '"{system.hostname}"\n  {system.platform} [{system.os_name}] {system.os_release} ({system.architecture})\n  {system.python_implementation} {f_pyver}'),
    }
    DEFAULT_FORMAT['verbose+'] = DEFAULT_FORMAT['verbose'] + '\n' \
                                 ' Updates from:\n' \
                                 '  Self: {metadata.manifest_upstream}\n' \
                                 '  Contents: {metadata.content_upstream}\n' \
                                 ' Generated on: (info level {system._info_level}): {f_system}'
    def info(self, level: typing.Literal['terse', 'normal', 'verbose', 'verbose+'] = 'verbose+', force_default: bool = False) -> str:
        fmt = (self.DEFAULT_FORMAT if (force_default or (self.get('format', None) is None)) else self['format'])
        fmtdict = {k: types.SimpleNamespace() for k in self.keys()}
        for ok,ns in fmtdict.items():
            for ik,iv in self[ok].items(): setattr(ns, ik, iv)
        fmtdict['f_alias'] = fmt['aliasfmt'][self['creation']['aka'] is not None].format_map(fmtdict)
        for t in ('created', 'updated'):
            fmtdict[f'fd_{t}'] = time.strftime(fmt['datefmt'], time.localtime(self['creation'][f'{t}_at'])).format_map(fmtdict)
        if self['system']['_info_level'] == 0:
            fmtdict['f_pyver'] = '<version info redacted>'
            fmtdict['f_system'] = fmt['sysfmt'][0].format_map(fmtdict)
        elif (s := self['system'])['_info_level'] == 1:
            fmtdict['f_pyver'] = '.'.join(s['python_version'][:3])
            fmtdict['f_system'] = fmt['sysfmt'][1].format_map(fmtdict)
        elif (s := self['system'])['_info_level'] == 2:
            fmtdict['f_pyver'] = f'{".".join(str(v) for v in s["python_version"][:3])} {s["python_version"][3]} {s["python_version"][4]}'
            fmtdict['f_system'] = fmt['sysfmt'][2].format_map(fmtdict)
        fmtdict['n_files'] = len(self['files'])
        fmtdict['o_metaversion'] = self['metadata'].get('meta_version', '<not provided>')
        return fmt[level].format_map(fmtdict)
    def _loglvl_to_infolvl(self) -> str:
        lvl = self.logger.getEffectiveLevel()
        if lvl < logging.INFO: return 'verbose+'
        elif lvl < getattr(logging, 'INFOPLUS', logging.INFO): return 'verbose'
        elif lvl < logging.WARNING: return 'normal'
        return 'terse'
    def _log_info(self, force_default: bool = False) -> str:
        return self.info(self._loglvl_to_infolvl(), force_default)
    # Generation
    class _ManifestFactory:
        __slots__ = ('Manifest',)
        def __init__(self, manif: typing.Type['Manifest']): self.Manifest = Manifest
        # Fields
        @staticmethod
        def gen_field__(*, hash_algorithm: typing.Literal[*hashlib.algorithms_available], key: EdPrivK, data: bytes) -> ManifestDict__:
            return {'encoding': sys.getdefaultencoding(), 'hash_algorithm': hash_algorithm,
                    'pubkey': base64.b85encode(key.public_key().public_bytes_raw()).decode(),
                    'signature': base64.b85encode(key.sign(data)).decode()}
        @staticmethod
        def gen_field_creation(*, by: str | None, aka: str | None = None, contact: str | None = None) -> ManifestDict_creation:
            crtime = round(time.time())
            return {'created_at': crtime, 'updated_at': crtime, 'by': by, 'aka': aka, 'contact': contact, 'nupdates': 0}
        @staticmethod
        def gen_field_metadata(*, name: str, manifest_upstream: str, content_upstream: str, description: str | None = None) -> ManifestDict_metadata:
            return {'name': name, 'description': description, 'manifest_upstream': manifest_upstream, 'content_upstream': content_upstream}
        field_system_info__none: ManifestDict_system = {'_info_level': 0,
            'os_name': None, 'platform': None, 'architecture': None, # more important system info
            'python_version': None, 'python_implementation': None, # Python info
            'os_release': None, 'os_version': None, 'hostname': None} # less important system info
        field_system_info__lite: ManifestDict_system = field_system_info__none | {'_info_level': 1,
            'os_name': os.name, 'architecture': os.uname().machine, 'python_version': sys.version_info[:3],
            'python_implementation': sys.implementation.name}
        field_system_info__full: ManifestDict_system = field_system_info__lite | {'_info_level': 2,
            'platform': sys.platform, 'os_release': os.uname().release, 'os_version': os.uname().version, 'hostname': os.uname().nodename,
            'python_version': sys.version_info[:]}
        FILE_PATTERNS = ('**/*',)
        FILE_EXCLUDED_SUFFIXES = {'.pyc', '.json', '.ini', '.old'}
        @classmethod
        def gen_field_files(cls, algorithm: typing.Literal[*hashlib.algorithms_available], path: Path) -> ManifestDict_files:
            return {file.relative_to(path).as_posix():
                        base64.b85encode(hashlib.new(algorithm, file.read_bytes()).digest()).decode()
                    for patt in cls.FILE_PATTERNS for file in path.glob(patt) if (file.suffix not in cls.FILE_EXCLUDED_SUFFIXES) and file.is_file()}
        # Generation functions
        def generate_outline(self, *,
                             system_info_level: typing.Literal['full', 'lite', 'none'] = 'full',
                             name: str, manifest_upstream: str, content_upstream: str,
                             by: str | None, aka: str | None = None, contact: str | None = None, description: str | None = None) -> ManifestDict:
            '''Creates the '_' and 'files' fields and populates the 'creation', 'metadata', and 'system' fields'''
            assert system_info_level in {'full', 'lite', 'none'}
            return {'_': NotImplemented,
                    'creation': self.gen_field_creation(by=by, aka=aka, contact=contact),
                    'metadata': self.gen_field_metadata(name=name, manifest_upstream=manifest_upstream, content_upstream=content_upstream, description=description),
                    'system': getattr(self, f'field_system_info__{system_info_level}'),
                    'files': NotImplemented}
        def generate_dict(self, path: Path, name: str, manifest_upstream: str, content_upstream: str, *,
                          by: str | None, aka: str | None = None, contact: str | None = None, description: str | None = None,
                          hash_algorithm: typing.Literal[*hashlib.algorithms_available] = 'sha1', key: EdPrivK | Path,
                          system_info_level: typing.Literal['full', 'lite', 'none'] = 'full') -> ManifestDict:
            '''Generates a manifest-dict from the given attributes'''
            if isinstance(key, Path): key = EdPrivK.from_private_bytes(key.read_bytes())
            data = self.generate_outline(system_info_level=system_info_level, name=name, manifest_upstream=manifest_upstream, content_upstream=content_upstream, by=by, aka=aka, contact=contact, description=description)
            data['files'] = self.gen_field_files(hash_algorithm, path)
            data['_'] = self.gen_field__(hash_algorithm=hash_algorithm, key=key, data=self.Manifest.compile_dict(data))
            return data
        @functools.wraps(generate_dict, assigned=('__annotations__', '__type_params__'))
        def __call__(self, *args, **kwargs) -> 'Manifest':
            '''Convenience wrapper for {self.}Manifest.from_dict(Manifest.ManifestFactory{|self}.generate_dict(...))'''
            return self.Manifest.from_dict(self.generate_dict(*args, **kwargs))
    @classmethod
    @property
    def ManifestFactory(cls) -> _ManifestFactory:
        cls.ManifestFactory = cls._ManifestFactory(cls); return cls.ManifestFactory
