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
#</Imports

#> Header >/
class Manifest(UserDict):
    __slots__ = ('_path', '_path_type')
    type_to_suffix = {
        'json': '.json',
        'ini': '.ini',
    }; suffix_to_type = {v: k for k,v in type_to_suffix.items()}

    # Constructors
    def __init__(self):
        ...
    ## From
    @classmethod
    def from_dict(cls, d: dict) -> typing.Self:
        self = object.__init__(cls)
        self.data = d
        return self
    ### From files
    def from_file(cls, path: Path, path_type: typing.Literal[*type_to_suffix] | None = None) -> typing.Self:
        self.path = path
        if path_type is None:
            # Guess it through the path suffix
            if path.suffix not in self.suffix_to_type:
                raise NotImplementedError(f'Cannot parse manifest with extension {path.suffix!r}')
            self.path_type = self.suffix_to_type[path.suffix]
        else:
            assert path_type in self.type_to_suffix
            self.path_type = path_type
    @classmethod
    def from_json(cls, jsn: Path) -> typing.Self:
        ...
    @classmethod
    def from_ini(cls, ini: Path) -> typing.Self:
        ...
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
    def compile_dict(cls, manif: dict[str, dict[str, ...]]) -> bytes:
        '''
            Compiles dictionaries for signing
            Manifest dictionaries would normally, at this stage, have the following structure (keys and values are either types or literals):
                '_cryptography': NotImplemented,
                'creation': {
                    'at': int,
                    'by': str,
                    'aka': str | None,
                    'contact': str | None,
                    'description': str | None,
                },
                'metadata': {
                    'name': str,
                    'manifest_upstream': str,
                    'content_upstream': str,
                },
                'system': {
                    'os_name': str | None,
                    'platform': str | None,
                    'architecture': str | None,
                    'python_version': tuple[int | str] | None,
                    'python_implementation': str | None,
                    'os_release': str | None,
                    'os_version': str | None,
                    'hostname': str | None,
                    '_info_level': int,
                },
                'files': {
                    str: bytes,
                    #...,
                }
            These are compiled in the following order (by default, see COMPILED_KEY_ORDER):
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
    
        # Why the generators above are all seperated:
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
        def __call__(self) -> 'Manifest':
            ...
        # Fields
        ## "_" field
        def gen_field__(self, pub_key: EdPubK, sig: bytes) -> dict[str, str]:
            return {
                'encoding': sys.getdefaultencoding(),
                'pubkey': base64.b85encode(pub_key.public_bytes_raw()),
                'signature': base64.b85encode(sig),
            }
        # "creation" field
        def gen_field_creation(self, *,
                               by: str | None, aka: str | None = None,
                               contact: str | None = None,
                               description: str | None = None) -> dict[str, int | str | None]:
            return {
                'at': round(time.time()),
                'by': by, 'aka': aka,
                'contact': contact,
                'description': description,
            }
        # "metadata" field
        def gen_field_metadata(self, *, name: str, manifest_upstream: str, content_upstream: str) -> dict[str, str]:
            return {
                'name': name,
                'manifest_upstream': manifest_upstream,
                'content_upstream': content_upstream,
            }
        # system info field
        @property
        def field_system_info__full(self) -> dict[str, str | tuple[str | int] | typing.Literal[2]]:
            unam = os.uname()
            return self.field_system_info__lite | {
                'platform': sys.platform,
                'python_version': sys.version_info[:],
                'os_release': unam.release,
                'os_version': unam.version,
                'hostname': unam.nodename,
                '_info_level': 2,
            }
        @property
        def field_system_info__lite(self) -> dict[str, str | tuple[int] | typing.Literal[1]]:
            unam = os.uname()
            return self.field_system_info__none | {
                'os_name': os.name,
                'architecture': unam.machine,
                'python_version': sys.version_info[:3],
                'python_implementation': sys.implementation.name,
                '_info_level': 1,
            }
        @property
        def field_system_info__none(self) -> dict[str, None | typing.Literal[0]]:
            # also serves as the base ordering
            return {
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
        def files_from_path(self, path: Path, patterns: tuple[str] = ('**/*.py', '**/rs_*')):
            ...
        # Generation functions
        def generate_metadatas(self, *,
                               system_info_level: typing.Literal['full', 'lite', 'none'] = 'full',
                               name: str, manifest_upstream: str, content_upstream: str,
                               by: str | None, aka: str | None = None, contact: str | None = None, description: str | None = None) -> dict[str, dict]:
            '''
                Generates and completes the following fields:
                    creation, metadata, system
                Creates but does not populate the following fields:
                    _cryptography, files
            '''
            assert system_info_level in {'full', 'lite', 'none'}
            return {
                '_cryptography': NotImplemented,
                'creation': self.gen_field_creation(by=by, aka=aka, contact=contact, description=description),
                'metadata': self.gen_field_metadata(name=name, manifest_upstream=manifest_upstream, content_upstream=content_upstream),
                'system': getattr(self, f'field_system_info__{system_info_level}'),
                'files': NotImplemented,
            }
        def generate(self) -> 'Manifest':
            
            self.Manifest
    @classmethod
    @property
    def ManifestFactory(cls) -> _ManifestFactory:
        cls.ManifestFactory = cls._ManifestFactory(cls)
        return cls.ManifestFactory
