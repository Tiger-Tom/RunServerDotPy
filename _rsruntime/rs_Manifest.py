#!/bin/python3

#> Imports
from pathlib import Path
from collections import UserDict
import typing
import logging
import time
import os
import sys
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as EdPrivK, Ed25519PublicKey as EdPubK
import base64
import hashlib
import json
import re
from configparser import ConfigParser
import io
from ast import literal_eval
import logging
import traceback
import functools
#</Imports

#> Header >/
# Manifest typehints
ManifestDict__ = typing.TypedDict("ManifestDict['_']", {
    'encoding': str,
    'hash_algorithm': typing.Literal[*hashlib.algorithms_available],
    'pubkey': str,
    'signature': str,
})
ManifestDict_creation = typing.TypedDict("ManifestDict['creation']", {
    'at': int,
    'by': str,
    'aka': str | None,
    'contact': str | None,
    'description': str | None,
})
ManifestDict_metadata = typing.TypedDict("ManifestDict['metadata']", {
    'name': str,
    'manifest_upstream': str,
    'content_upstream': str,
})
ManifestDict_system = typing.TypedDict('ManifestDict[\'system\']', {
    'os_name': str | None,
    'platform': str | None,
    'architecture': str | None,
    'python_version': tuple[int | str] | None,
    'python_implementation': str | None,
    'os_release': str | None,
    'os_version': str | None,
    'hostname': str | None,
    '_info_level': int,
})
ManifestDict_files = typing.Dict[str, bytes]
ManifestDict = typing.TypedDict('ManifestDict', {
    '_': ManifestDict__,
    'creation': ManifestDict_creation,
    'metadata': ManifestDict_metadata,
    'system': ManifestDict_system,
    'files': ManifestDict_files,
})
# Manifest class
class Manifest(UserDict):
    __slots__ = ('own_path', 'base_path')
    type_to_suffix = {
        'ini': '.ini',
        'json': '.json',
    }; suffix_to_type = {v: k for k,v in type_to_suffix.items()}

    # Helper / compat function
    @staticmethod
    def _logger() -> logging.Logger:
        '''Ensures compatability whether or not the logger is set up'''
        logger = logging.getLogger('RS.BS.M')
        if not hasattr(logger, 'infop'):
            logger.infop = logger.warning
        return logger
    # Constructors
    def __init__(self):
        '''Use from_dict or from_file instead (from_json and from_ini can be called through from_file or directly)'''
        raise TypeError('Should not be initialized here, use from_dict or from_file')
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
        self = object.__new__(cls)
        UserDict.__init__(self, d)
        return self
    ### From string types
    @classmethod
    def from_json(cls, jsn: str) -> typing.Self:
        '''
            Generates a Manifest instance from JSON text
                Convenience method for Manifest.from_json(Manifest.dict_from_json_text(...))
        '''
        return cls.from_dict(cls.dict_from_json_text(jsn))
    @classmethod
    def from_ini(cls, ini: str) -> typing.Self:
        '''
            Generates a Manifest instance from INI text
                Convenience method for Manifest.from_dict(Manifest.dict_from_ini_text(...))
        '''
        return cls.from_dict(cls.dict_from_ini_text(ini))
    #### Dict from string types
    @staticmethod
    def dict_from_json_text(jsn: str) -> ManifestDict:
        '''
            Helper method to convert JSON text to a dictionary
                Current implementation just calls json.loads
        '''
        return json.loads(jsn)
    @staticmethod
    def dict_from_ini_text(ini: str) -> ManifestDict:
        '''
            Helper method to convert INI text into a dict
            Notes:
              - interpolation is disabled
              - keys are case-sensitive
        '''
        p = ConfigParser(interpolation=None)
        p.optionxform = lambda o: o # prevents lowercasing of filenames
        p.read_string(ini)
        data = {}
        for k,v in p.items():
            if k == 'DEFAULT': continue
            data[k] = {ik: literal_eval(iv) for ik,iv in v.items()}
        return data
    ### From files
    @classmethod
    def from_file(cls, path: Path, path_type: typing.Literal[*type_to_suffix] | None = None) -> typing.Self:
        '''
            Initializes Manifest from a file.
            Can load from the following file types:
                'json': .json files
                'ini': .ini files
            If path_type is given, then attempts to load a file of that type
            Otherwise, path_type is guessed from path's suffix, using Manifest.suffix_to_type
        '''
        logger = cls._logger()
        if path_type is None:
            # Guess it through the path suffix
            if path.suffix in cls.suffix_to_type:
                path_type = cls.suffix_to_type[path.suffix]
            else:
                logger.warning(f'path_type not given, and guessing it via the path\'s suffix ({path.suffix=}) failed')
                data = path.read_text()
                for k,v in cls.type_to_handler:
                    try:
                        logger.infop(f'Trying {k!r} handler on contents of {path}')
                        return v(data)
                    except Exception as e:
                        logger.error(f'{k!r} handler failed on contents of {path} failed:\n{traceback.format_exception(e)}')
                raise NotImplementedError(f'Cannot parse manifest with extension {path.suffix!r}, no handlers succeeded')
        if path_type not in cls.type_to_suffix:
            raise TypeError(f'Illegal path type {path_type!r}')
        data = path.read_text()
        return getattr(cls, f'from_{path_type}')(data).set_paths(base=path.parent, own=path)
    # Rendering
    JSON_ARRAY_CLEANER_A = re.compile(r'^(\s*"[^"]*":\s*)(\[[^\]]*\])(,?\s*)$', re.MULTILINE)
    JSON_ARRAY_CLEANER_B = staticmethod(lambda m: m.group(1)+(re.sub(r'\s+', '', m.group(2)).replace(',', ', '))+m.group(3))
    def render_json(self, to: typing.TextIO | None = None) -> str:
        data = self.JSON_ARRAY_CLEANER_A.sub(self.JSON_ARRAY_CLEANER_B, json.dumps(self.data, sort_keys=False, indent=4))
        if to is not None: to.write(data)
        return data
    def render_ini(self, to: None | typing.TextIO = None) -> str | None:
        p = ConfigParser(interpolation=None)
        p.optionxform = lambda o: o # prevents lowercasing of filenames
        for ok,ov in self.data.items():
            p[ok] = {ik: repr(iv) for ik,iv in ov.items()}
        if to is None:
            sio = io.StringIO()
            p.write(sio)
            return sio.getvalue()
        p.write(to)
        return None
    # Data extraction
    def i_d_files(self) -> typing.Generator[tuple[Path, bytes], None, None]:
        return (((self.base_path / k), base64.b85decode(v)) for k,v in self.data['files'].items())
    @property
    def d_files(self) -> ManifestDict_files:
        return ManifestDict_files(self.i_d_files())
    # Compilation
    ## Constants
    COMPILED_KEY_ORDER = ('creation', 'metadata', 'system', 'files')
    COMPILED_KEY_VALUE_SEP = 255
    COMPILED_ENTRY_SEP = 0
    ## Individual value compilers
    _val_compilers = {
        bytes: lambda b: b,
        str: lambda s: s.encode(),
        int: lambda n: n.to_bytes(((n.bit_length() + 1) + 7) // 8, signed=True),
        type(None): lambda v: bytes((255,)),
    }
    @classmethod
    def _compile_value(cls, val: typing.Union[*_val_compilers] | tuple | list) -> bytes:
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
            Keys are compiled in the following order (by default, see COMPILED_KEY_ORDER):
             - 'creation'
             - 'metadata'
             - 'system'
             - 'files'
            with each inner value being added to the compiled data as (where, by default, COMPILED_KEY_VALUE_SEP is 255 and COMPILED_ENTRY_SEP is 0):
             - _compile_value(outer_key)
             - COMPILED_KEY_VALUE_SEP
             - _compile_value(inner_key)
             - COMPILED_KEY_VALUE_SEP
             - _compile_value(value)
             - COMPILED_KEY_VALUE_SEP
             - COMPILED_ENTRY_SEP
            So, to add "manif['creation']['at']", where the value is 1700515559, the function would add:
             - _compile_value('creation')
             - COMPILED_KEY_VALUE_SEP
             - _compile_value('at')
             - COMPILED_KEY_VALUE_SEP
             - _compile_value(1700515559)
             - COMPILED_KEY_VALUE_SEP
             - COMPILED_ENTRY_SEP
        '''
        # Bring in values for readability (and I suppose for a tiny inner loop efficiency bonus)
        compile_val = cls._compile_value
        COMPILED_KEY_VAL_SEP = cls.COMPILED_KEY_VALUE_SEP; COMPILED_ENTRY_SEP = cls.COMPILED_ENTRY_SEP
        # Generators
        compiler = ((*compile_val(outer_key), COMPILED_KEY_VAL_SEP, *compile_val(inner_key), COMPILED_KEY_VAL_SEP, *compile_val(value), COMPILED_KEY_VAL_SEP, COMPILED_ENTRY_SEP)
                    for outer_key in cls.COMPILED_KEY_ORDER for inner_key,value in manif[outer_key].items())
        flattener = (byte for bytes_ in compiler for byte in bytes_)
        # Evaluate and render into bytes
        return bytes(flattener)
    
        # Why the generators above are split and named:
        #return bytes(byte for bytes_ in ((*compile_val(outer_key), COMPILED_KEY_VAL_SEP, *compile_val(inner_key), COMPILED_KEY_VAL_SEP, *compile_val(value), COMPILED_KEY_VAL_SEP, COMPILED_ENTRY_SEP)
        #                                 for outer_key in cls.COMPILED_KEY_ORDER for inner_key,value in manif[outer_key].items()) for byte in bytes_)
        
        # Original prototype code for the sake of readability versus the monstrosity above:
        #compd = bytearray()
        #for k in cls.COMPILED_KEY_ORDER:
        #    for ik,iv in manif[k].items():
        #        compd.extend(cls._compile_value(k))
        #        compd.append(cls.COMPILED_KEY_VALUE_SEP)
        #        compd.extend(cls._compile_value(ik))
        #        compd.append(cls.COMPILED_KEY_VALUE_SEP)
        #        compd.extend(cls._compile_value(iv))
        #        compd.extend((cls.COMPILED_KEY_VALUE_SEP, cls.COMPILED_ENTRY_SEP))
        #return bytes(compd)
        

    # methods for manifest generation
    class _ManifestFactory:
        __slots__ = ('Manifest',)
        def __init__(self, manif: typing.Type['Manifest']):
            self.Manifest = Manifest
        # Fields
        ## "_" field
        def gen_field__(self, *, hash_algorithm: typing.Literal[*hashlib.algorithms_available], pub_key: EdPubK, sig: bytes) -> ManifestDict__:
            return {
                'encoding': sys.getdefaultencoding(),
                'hash_algorithm': hash_algorithm,
                'pubkey': base64.b85encode(pub_key.public_bytes_raw()).decode(),
                'signature': base64.b85encode(sig).decode(),
            }
        # "creation" field
        def gen_field_creation(self, *,
                               by: str | None, aka: str | None = None,
                               contact: str | None = None,
                               description: str | None = None) -> ManifestDict_creation:
            return {
                'at': round(time.time()),
                'by': by, 'aka': aka,
                'contact': contact,
                'description': description,
            }
        # "metadata" field
        def gen_field_metadata(self, *, name: str, manifest_upstream: str, content_upstream: str) -> ManifestDict_metadata:
            return {
                'name': name,
                'manifest_upstream': manifest_upstream,
                'content_upstream': content_upstream,
            }
        # system info field
        @classmethod
        @property
        def field_system_info__full(cls) -> ManifestDict_system:
            unam = os.uname()
            return cls.field_system_info__lite | {
                'platform': sys.platform,
                'python_version': sys.version_info[:],
                'os_release': unam.release,
                'os_version': unam.version,
                'hostname': unam.nodename,
                '_info_level': 2,
            }
        @classmethod
        @property
        def field_system_info__lite(cls) -> ManifestDict_system:
            unam = os.uname()
            return cls.field_system_info__none | {
                'os_name': os.name,
                'architecture': unam.machine,
                'python_version': sys.version_info[:3],
                'python_implementation': sys.implementation.name,
                '_info_level': 1,
            }
        field_system_info__none: ManifestDict_system = {
            # more important system info
            'os_name': None,               # lite
            'platform': None,              # full
            'architecture': None,          # lite
            # Python info
            'python_version': None,        # lite
            'python_implementation': None, # lite
            # less important system info
            'os_release': None,            # full
            'os_version': None,            # full
            'hostname': None,              # full
            # metadata
            '_info_level': 0,
        }
        # File hashing
        @staticmethod
        def files_from_path(path: Path, patterns: tuple[str] = ('**/*.py', '**/rs_*'), exclude_suffixes: tuple[str] = ('.pyc',)) -> set[Path]:
            files = set()
            #for pat in patterns:
            #    files |= set(p for p in path.glob(pat) if p.suffix not in exclude)
            tuple(map(lambda pat: files.update(p.relative_to(path) for p in path.glob(pat) if p.suffix not in exclude_suffixes), patterns))
            return files
        @classmethod
        def hash_files(cls, algorithm: str, files: set[Path]) -> dict[Path, bytes]:
            assert algorithm in hashlib.algorithms_guaranteed
            hashes = {}
            for p in sorted((p for p in files), key=lambda p: (len(p.parents), p)):
                with p.open('rb') as f:
                    hashes[p] = hashlib.file_digest(f, algorithm).digest()
            return hashes
        # Generation functions
        def generate_outline(self, *,
                             system_info_level: typing.Literal['full', 'lite', 'none'] = 'full',
                             name: str, manifest_upstream: str, content_upstream: str,
                             by: str | None, aka: str | None = None, contact: str | None = None, description: str | None = None) -> ManifestDict:
            '''
                Generates and completes the following fields:
                    creation, metadata, system
                Creates but does not populate the following fields:
                    _, files
            '''
            assert system_info_level in {'full', 'lite', 'none'}
            return {
                '_': NotImplemented,
                'creation': self.gen_field_creation(by=by, aka=aka, contact=contact, description=description),
                'metadata': self.gen_field_metadata(name=name, manifest_upstream=manifest_upstream, content_upstream=content_upstream),
                'system': getattr(self, f'field_system_info__{system_info_level}'),
                'files': NotImplemented,
            }
        def generate_cryptography(self, hash_algorithm: typing.Literal[*hashlib.algorithms_available], key: EdPrivK, data: bytes) -> ManifestDict__:
            '''Does everything necessary to populate the "_" field'''
            return self.gen_field__(hash_algorithm=hash_algorithm, pub_key=key.public_key(), sig=key.sign(data))
        def generate_files(self, algorithm: typing.Literal[*hashlib.algorithms_available], path: Path) -> ManifestDict_files:
            '''
                Finds the files under path, then returns a dict with the key being:
                    the posix representation of the files (relative to path)
                and the value being:
                    the base85 encoded hash
            '''
            return {k.as_posix(): base64.b85encode(v).decode() for k,v in
                    self.hash_files(algorithm, self.files_from_path(path)).items()}
        def generate_dict(self, path: Path, name: str, manifest_upstream: str, content_upstream: str, *,
                          by: str | None, aka: str | None = None, contact: str | None = None, description: str | None = None,
                          hash_algorithm: typing.Literal[*hashlib.algorithms_available] = 'sha1', key: EdPrivK | Path,
                          system_info_level: typing.Literal['full', 'lite', 'none'] = 'full') -> ManifestDict:
            '''Generates a manifest-dict from the given attributes'''
            if isinstance(key, Path):
                key = EdPrivK.from_private_bytes(key.read_bytes())
            data = self.generate_outline(system_info_level=system_info_level, name=name, manifest_upstream=manifest_upstream, content_upstream=content_upstream, by=by, aka=aka, contact=contact, description=description)
            data['files'] = self.generate_files(hash_algorithm, path)
            data['_'] = self.generate_cryptography(hash_algorithm, key, self.Manifest.compile_dict(data))
            return data
        @functools.wraps(generate_dict, assigned=('__annotations__', '__type_params__'))
        def __call__(self, *args, **kwargs) -> 'Manifest':
            '''
                Convenience wrapper for {self.}Manifest.from_dict(Manifest.ManifestFactory{|self}.generate_dict(...))
                    See Manifest.ManifestFactory.generate_dict for kwargs
            '''
            return self.Manifest.from_dict(self.generate_dict(*args, **kwargs))
    @classmethod
    @property
    def ManifestFactory(cls) -> _ManifestFactory:
        cls.ManifestFactory = cls._ManifestFactory(cls)
        return cls.ManifestFactory
