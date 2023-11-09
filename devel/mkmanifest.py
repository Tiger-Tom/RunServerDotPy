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
import re
#</Imports

#> Header
eprint = lambda *k,**kw: print(*k, **kw, file=sys.stderr)

def manifest_metadata(name: str, pubkey: str | tuple[int], sig: str | tuple[int], mupstream: str | None, fupstream: str | None) -> dict:
    return {
        'name': name,
        'public_key': pubkey,
        'signature': sig,
        'manifest_upstream': mupstream,
        'file_upstream': fupstream,
    }
def compile(datas_head: tuple[str | None], datas_body: tuple[tuple[str, bytes]]) -> bytes:
    ba = bytearray()
    eprint(f'Compiling {len(datas_head)} heads')
    for d in datas_head:
        if d is None: ba.append(255)
        else: ba.extend(d.encode())
        ba.append(0)
    ba.append(0)
    eprint(f'Compiling {len(datas_body)} bodies')
    for d0,d1 in datas_body:
        ba.extend(d0.encode())
        ba.append(255)
        ba.extend(d1)
        ba.append(0)
    eprint(f'Final compiled size: {len(ba)}')
    return bytes(ba)
def manifest(name: str, path: Path, key: pysign.EdPrivK, mupstream: str, fupstream: str, long_fmt: bool) -> dict:
    man = {'_metadata': None}
    hashes = tuple(
        (f.relative_to(path).as_posix(), (eprint(f'Hashing {f}...'), hashlib.file_digest(fd, hashlib.sha1).digest(), fd.close())[1]) for f,fd in
        sorted(
            ((f, f.open('rb'))
            for f in set(path.glob('**/*.py')) | set(path.glob('**/rs_*.*'))
            if (not f.name.startswith('_')) and (not f.suffix in {'.pyc'})),
            key=lambda fg: (len(fg[0].parents), fg[0])
        )
    )
    for f,h in hashes:
        man[f] = tuple(h) if long_fmt else base64.b85encode(h).decode()
        eprint(f'{f} -> {man[f]}')
    compd = compile((name, mupstream, fupstream), hashes)
    eprint(f'Compiled: ({len(compd)} byte(s))\n{compd}')
    keydump = tuple(key.public_key().public_bytes_raw()) if long_fmt else base64.b85encode(key.public_key().public_bytes_raw()).decode()
    eprint(f'Signing {len(compd)} bytes\n private: {tuple(key.private_bytes_raw()) if long_fmt else base64.b85encode(key.private_bytes_raw()).decode()}\n public:  {keydump}')
    sig = pysign.signstr(key, compd, long_fmt)
    eprint(f'Signature: {sig}')
    man['_metadata'] = meta = manifest_metadata(name, keydump, sig, mupstream, fupstream)
    return man
def jsonify(manif: dict, long_fmt: bool, compact: bool, extra_compact: bool) -> str:
    jsn = json.dumps(manif, sort_keys=False,
                     indent=None if compact or extra_compact else 4,
                     separators=(',', ':')  if extra_compact else None)
    if (not long_fmt) or compact or extra_compact: return jsn
    return re.sub(r'^(\s*"[^"]*":\s*)(\[[\s\d,]*\])(,?\s*)$', lambda m: m.group(1)+(re.sub(f'\s+', '', m.group(2)).replace(',', ', '))+m.group(3), jsn, flags=re.MULTILINE)
#</Header

#> Main >/
def parse_args(args=None):
    p = argparse.ArgumentParser(prog='mkmanifest.py')
    sp = p.add_subparsers(dest='cmd')
    u = sp.add_parser('update')
    a = sp.add_parser('add')
    # symmetric arguments
    for sub in (u, a):
        sub.add_argument('--output', help='The file to write to (defaults to stdout)', type=Path, default=None)
        sub.add_argument('--sign', help='The path of the key to sign with (use pysign.py to generate)', type=Path)
        sub.add_argument('--long', help='Store the public key, signature, and hashes in long format', action='store_true')
        sub.add_argument('--compact', help='Compact output', action='store_true')
        sub.add_argument('--extra-compact', help='Use extra compact output', action='store_true')
    # update-exclusive arguments
    u.add_argument('old_manifest', help='The manifest to read old values from', type=Path)
    # add-exclusive arguments
    a.add_argument('name', help='The name of the manifest')
    a.add_argument('path', help='The path to create a manifest for', type=Path)
    a.add_argument('manifest_upstream', help='The URI to fetch manifest updates from', nargs='?')
    a.add_argument('file_upstream', help='The URI to fetch file updates from', nargs='?')
    args = p.parse_args(args)
    if args.cmd == 'update':
        with args.old_manifest.open('r') as f:
            old = json.load(f)
        eprint('Fetched old manifest')
        meta = old['_metadata']
        
        man = manifest(meta['name'], args.old_manifest, pysign.read_key(args.sign), meta['manifest_upstream'], meta['file_upstream'], args.long)
    if args.cmd != 'add':
        p.print_help()
        exit(1)
    else:
        man = manifest(args.name, args.path, pysign.read_key(args.sign), args.manifest_upstream, args.file_upstream, args.long)
    jsn = jsonify(man, args.long, args.compact, args.extra_compact)
    eprint(jsn)
    with sys.stdout if args.output is None else args.output.open('w') as f:
        f.write(jsn)
if __name__ == '__main__': parse_args()
