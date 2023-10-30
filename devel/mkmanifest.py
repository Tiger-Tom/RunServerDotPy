#!/bin/python3

#> Imports
import sys
from pathlib import Path
import hashlib
import json
import subprocess
#</Imports

#> Main >/
eprint = lambda *k,**kw: print(*k, **kw, file=sys.stderr)
bmeta = lambda n,mu,fu: {'_metadata': {'name': n, 'manifest_upstream': mu, 'file_upstream': fu}}

match sys.argv:
    case [_, 'add', name, path, mupstream, fupstream]:
        print(name, path, mupstream, fupstream)
        path = Path(path) # path path path
        man = bmeta(name, mupstream, fupstream)
        for p in path.glob('**/*.py'):
            eprint(f'Adding manifest entry for {p.name}')
            with p.open('rb') as f:
                hd = hashlib.file_digest(f, hashlib.sha1).hexdigest()
            eprint(f'"{p.name}": "{hd}"')
            man[p.relative_to(path).as_posix()] = hd
        print(json.dumps(man, indent=4))
    case [_, 'update', path]:
        path = Path(path)
        with path.open('r') as f:
            cman = json.load(f)
        eprint('Fetched old manifest')
        subprocess.call((sys.argv[0], 'add', cman['_metadata']['name'], str(path.parent), cman['_metadata']['manifest_upstream'], cman['_metadata']['file_upstream']))
    case _:
        eprint('usage: mkmanifest.py add [name] [path] [manifest upstream] [file upstream]\nor:    mkmanifest.py update [path]')
        exit(1)
