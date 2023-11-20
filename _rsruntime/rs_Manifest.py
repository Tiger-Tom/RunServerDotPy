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
    _val_compilers = {
        bytes: lambda b: b,
        str: lambda s: s.encode(),
        int: lambda n: n.to_bytes(((n.bit_length() + 1) + 7) // 8, signed=True),
        type(None): lambda v: bytes(255),
    }
    @classmethod
    def _compile_value(cls, val: typing.Union[*_val_compilers] | tuple | list) -> bytes:
        if type(val) in {tuple, list}:
            return b''.join(cls._compile_value(v) for v in val)
        if type(val) not in cls._val_compilers:
            raise TypeError(f'Cannot handle value {val} (type {type(val)})')
        return cls._val_compilers[type(val)](val)
    @classmethod
    def compile_manifest(cls, manif: dict[str, dict[str, ...]]) -> bytes:
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
            Each key and value is passed to _compile_value
        '''

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
