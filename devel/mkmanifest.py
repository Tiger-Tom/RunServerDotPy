#!/bin/python3

#> Imports
import argparse
import sys
from pathlib import Path
import hashlib
import json
import subprocess
from pprint import pprint
import pysign
import base64
#</Imports

#> Main >/
eprint = lambda *k,**kw: print(*k, **kw, file=sys.stderr)

def parse_args(args=None):
    p = argparse.ArgumentParser(prog='mkmanifest.py')
    sp = p.add_subparsers(dest='cmd')
    u = sp.add_parser('update')
    u.add_argument('old_manifest', help='The manifest to read old values from', type=Path)
    u.add_argument('--output', help='The file to write to (defaults to stdout)', type=Path, default=None)
    u.add_argument('--sign', help='The name of the private key to sign with (use pysign.py)', type=Path)
    a = sp.add_parser('add')
    a.add_argument('name', help='The name of the manifest')
    a.add_argument('path', help='The path to create a manifest for', type=Path)
    a.add_argument('manifest_upstream', help='The URI to fetch manifest updates from', nargs='?')
    a.add_argument('file_upstream', help='The URI to fetch file updates from', nargs='?')
    a.add_argument('--output', help='The file to write to (defaults to stdout)', type=argparse.FileType('w'), default=sys.stdout)
    a.add_argument('--sign', help='The path of the key to sign with (use pysign.py to generate)', type=Path)
    args = p.parse_args(args)
    if args.cmd == 'update':
        with args.old_manifest.open('r') as f:
            old = json.load(f)
        eprint('Fetched old manifest')
        parse_args(('add', old['_metadata']['name'], str(args.old_manifest.parent),
                    old['_metadata']['manifest_upstream'], old['_metadata']['file_upstream'], '--output', args.sign) + \
                   (('--output', str(args.output)) if args.output is not None else ()))
        return
    if args.cmd != 'add':
        p.print_help()
        exit(1)
    priv = pysign.read_key(args.sign)
    manifest = {
        '_metadata': {
            'name': args.name,
            'manifest_upstream': args.manifest_upstream,
            'file_upstream': args.file_upstream,
            'public_key': base64.b85encode(priv.public_key().public_bytes_raw()).decode(),
            'signature': None,
        },
    }
    ba = bytearray()
    # metadata
    ba = bytearray()
    if args.name is None: ba.append(255)
    else: ba.extend(args.name.encode())
    ba.append(0)
    if args.manifest_upstream is None: ba.append(255)
    else: ba.extend(args.manifest_upstream.encode())
    ba.append(0)
    if args.file_upstream is None: ba.append(255)
    else: ba.extend(args.file_upstream.encode())
    ba.extend((0, 0))
    # file hashes
    for p in sorted(set(args.path.glob('**/*.py')) | set(args.path.glob('**/rs_*.*'))):
        if p.suffix in {'.pyc'}: continue
        eprint(f'Adding manifest entry for {p.name}')
        with p.open('rb') as f:
            hd = hashlib.file_digest(f, hashlib.sha1).digest()
        eprint(f'"{p.name}": "{base64.b85encode(hd).decode()}"')
        manifest[p.relative_to(args.path).as_posix()] = base64.b85encode(hd).decode()
        ba.extend(hd)
        ba.append(255)
        ba.extend(p.relative_to(args.path).as_posix().encode())
        ba.append(0)
    eprint(ba)
    eprint(f'Signing with privkey {base64.b85encode(priv.private_bytes_raw()).decode()}')
    manifest['_metadata']['signature'] = pysign.signstr(priv, bytes(ba))
    eprint(f'Signature: {manifest["_metadata"]["signature"]}')
    eprint(f'pubkey: {manifest["_metadata"]["public_key"]}')
    json.dump(manifest, args.output, indent=4, sort_keys=False)
if __name__ == '__main__': parse_args()
