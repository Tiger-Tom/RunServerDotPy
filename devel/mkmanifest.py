#!/bin/python3

#> Imports
import argparse
import sys
from pathlib import Path
import hashlib
import json
import subprocess
from pprint import pprint
#</Imports

#> Main >/
eprint = lambda *k,**kw: print(*k, **kw, file=sys.stderr)

def parse_args(args=None):
    p = argparse.ArgumentParser(prog='mkmanifest.py')
    sp = p.add_subparsers(dest='cmd')
    u = sp.add_parser('update')
    u.add_argument('old_manifest', help='The manifest to read old values from', type=Path)
    u.add_argument('--output', help='The file to write to (defaults to stdout)', type=Path, default=None)
    a = sp.add_parser('add')
    a.add_argument('name', help='The name of the manifest')
    a.add_argument('path', help='The path to create a manifest for', type=Path)
    a.add_argument('manifest_upstream', help='The URI to fetch manifest updates from', nargs='?')
    a.add_argument('file_upstream', help='The URI to fetch file updates from', nargs='?')
    a.add_argument('--output', help='The file to write to (defaults to stdout)', type=argparse.FileType('w'), default=sys.stdout)
    args = p.parse_args(args)
    if args.cmd == 'update':
        with args.old_manifest.open('r') as f:
            old = json.load(f)
        eprint('Fetched old manifest')
        parse_args(('add', old['_metadata']['name'], str(args.old_manifest.parent), old['_metadata']['manifest_upstream'], old['_metadata']['file_upstream']) \
                   +(('--output', str(args.output)) if args.output is not None else ()))
        return
    if args.cmd != 'add':
        p.print_help()
        exit(1)
    manifest = {
        '_metadata': {
            'name': args.name,
            'manifest_upstream': args.manifest_upstream,
            'file_upstream': args.file_upstream,
        },
    }
    for p in sorted(set(args.path.glob('**/*.py')) | set(args.path.glob('**/rs_*.*'))):
        if p.suffix in {'.pyc'}: continue
        eprint(f'Adding manifest entry for {p.name}')
        with p.open('rb') as f:
            hd = hashlib.file_digest(f, hashlib.sha1).hexdigest()
        eprint(f'"{p.name}": "{hd}"')
        manifest[p.relative_to(args.path).as_posix()] = hd
    json.dump(manifest, args.output, indent=4, sort_keys=False)
if __name__ == '__main__': parse_args()
