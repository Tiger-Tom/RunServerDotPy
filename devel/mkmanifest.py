#!/bin/python3

#> Imports
import argparse
import sys
import hashlib
from pathlib import Path
from types import ModuleType
from importlib.machinery import SourceFileLoader
from ast import literal_eval
import base64
import typing
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as EdPrivK
import time
#</Imports

# E-print
eprint = lambda *k,**kw: print(*k, **kw, file=sys.stderr)

# Attempt to import Manifest
def try_find_bootstrapfile(p: Path) -> Path | None:
    eprint(f'Trying to find rs_BOOTSTRAP.py in {p}')
    if (p / 'rs_BOOTSTRAP.py').is_file():
        return p / 'rs_BOOTSTRAP.py'
    if (p / '_rsruntime').is_dir():
        return try_find_bootstrapfile(p / '_rsruntime')
    eprint('No dice')
    return None

file = try_find_bootstrapfile(Path('.'))
if file is None: file = try_find_bootstrapfile(Path('..'))
if file is None:
    raise FileNotFoundError('Could not find rs_BOOTSTRAP.py')
eprint(f'Found bootstrap file: {file}; importing')
try:
    sfl = SourceFileLoader('rs_BOOTSTRAP', str(file))
    rs_BOOTSTRAP = ModuleType(sfl.name)
    sfl.exec_module(rs_BOOTSTRAP)
except ImportError as e:
    raise ImportError('Could not import Manifest') from e
Manifest = rs_BOOTSTRAP.Manifest
ManifestFactory = Manifest.ManifestFactory

#> Header
# Common args
def args_common_output(p: argparse.ArgumentParser, add_overwrite: bool = True):
    if add_overwrite:
        meog = p.add_mutually_exclusive_group(required=add_overwrite)
        meog.add_argument('--output', metavar='file', help='Write the manifest to a file', type=argparse.FileType('w'))
        meog.add_argument('--overwrite', help='Output to (overwrite) the original manifest', action='store_true')
        meog.add_argument('--print-output', help='Prints the manifest to stdout instead of writing it to a file', action='store_const', dest='output', const=sys.stdout)
    else: p.add_argument('--output', metavar='file', help='The file to write to, defaults to stdout', type=argparse.FileType('w'), default=sys.stdout)
    p.add_argument('--render-json', help='Render output as JSON instead of INI (!!this is NEVER implicit and should always be added if you need JSON output!!)', action='store_true')
def args_common_manifestread(p: argparse.ArgumentParser, phelp='The manifest to read'):
    p.add_argument('manifest', metavar='file', help=phelp, type=Path)
def args_manifest_contact(p: argparse.ArgumentParser):
    p.add_argument('--creator', help='The "real name" of the creator (either this or --creator-username is needed) [\'by\']', default=None)
    p.add_argument('--creator-username', help='The "username" of the creator (either this or --creator is needed) [\'aka\' (with --creator) / \'by\' (without --creator)]')
    p.add_argument('--contact', help='The contact information of the creator', default=None)
    p.add_argument('--description', help='A description to embed in the manifest', default=None)
def args_manifest_metadata(p: argparse.ArgumentParser, positional: bool = False):
    p.add_argument(f'{"" if positional else "--"}manifest_name', help="The name of the manifest ['name']")
    p.add_argument(f'{"" if positional else "--"}manifest_upstream', help="The URL to fetch manifest updates from ['manifest_upstream']")
    p.add_argument(f'{"" if positional else "--"}content_upstream', help="The URL to fetch file (content) updates from ['content_upstream']")
def args_manifest_system(p: argparse.ArgumentParser):
    p.add_argument('--system-info-level', help='The level of system-info to write (default: "full")', choices=('full', 'lite', 'none'), default='full')
# Common functions
def common_output(man: Manifest, args: argparse.Namespace):
    mt = (man.render_json() if args.render_json else man.render_ini()).strip()
    eprint(mt)
    if args.overwrite: args.manifest.write_text(mt)
    else: args.output.write(mt)
    if args.output == sys.stdout:
        eprint() # print a newline to prevent terminal issues in case output is not redirected
# Modes
def args_make(p: argparse.ArgumentParser):
    p.add_argument('path', help='The path to add files:hashes from', type=Path)
    args_manifest_metadata(p.add_argument_group("['metadata']"), True)
    args_manifest_contact(p.add_argument_group("['creation']"))
    args_manifest_system(p)
    cg = p.add_argument_group('Cryptography')
    cg.add_argument('--key', help='The path to the private key file (default: "./key.pyk", if it exists)', type=Path,
                    default=Path('./key.pyk') if Path('./key.pyk').is_file() else None, required=not Path('./key.pyk').is_file())
    cg.add_argument('--hash-algorithm', help='The hashing algorithm to use (default: "sha1")', choices=hashlib.algorithms_available, default='sha1')
    args_common_output(p, False)
    ag = p.add_argument_group('ADVANCED')
    ag.add_argument('--file-patterns', help='File pattern(glob)s to use when finding files. This argument can be used more than once, and when used overwrites the default patterns', action='append', default=[])
    ag.add_argument('--file-excluded-suffixes', help='File suffixes to exclude when finding files. This argument can be used more than once, and when used overwrites the default suffixes', action='append', default=[])
def mode_make(args: argparse.Namespace):
    if not (bool(args.creator) or bool(args.creator_username)):
        raise ValueError('At least one of --creator or --creator-username is required')
    if args.file_patterns:
        ManifestFactory.FILE_PATTERNS = tuple(args.file_patterns)
    if args.file_excluded_suffixes:
        ManifestFactory.FILE_EXCLUDED_SUFFIXES = set(args.file_excluded_suffixes)
    m = ManifestFactory(args.path, args.manifest_name, args.manifest_upstream, args.content_upstream,
                        by=(args.creator_username if (args.creator is None) else args.creator), aka=(None if (args.creator is None) else args.creator_username), contact=args.contact, description=args.description,
                        hash_algorithm=args.hash_algorithm, key=args.key,
                        system_info_level=args.system_info_level)
    mt = (m.render_json() if args.render_json else m.render_ini()).strip()
    eprint(mt); args.output.write(mt)

def args_update(p: argparse.ArgumentParser):
    args_common_manifestread(p)
    p.add_argument('path', help='The path to add file:hashes from', type=Path)
    p.add_argument('--hash-algorithm', help='The hashing algorithm to use (defaults to the algorithm set in the manifest)', choices=hashlib.algorithms_available, default=None)
    args_common_output(p)
def mode_update(args: argparse.Namespace):
    man = Manifest.from_file(args.manifest)
    halg = man['_']['hash_algorithm'] = man['_']['hash_algorithm'] if (args.hash_algorithm is None) else args.hash_algorithm
    eprint(f'Updating manifest: files from {args.manifest}, algorithm {halg}')
    if man['files'] != (fs := ManifestFactory.gen_field_files(halg, args.path)):
        man['files'] = fs
        man['creation']['nupdates'] += 1
        man['creation']['updated_at'] = round(time.time())
        no_changes = False
    else:
        eprint(f'No new changes to write!')
        no_changes = True
    common_output(man, args)
    try: man.verify()
    except InvalidSignature:
        eprint(f'\nYou may want to run "sign" on the manifest now, as it currently fails verification')
    if no_changes: exit(-1)

def args_sign(p: argparse.ArgumentParser):
    args_common_manifestread(p, 'The path of the manifest to sign')
    p.add_argument('key', help='The path to the private key file (default: "./key.pyk", if it exists)', type=Path,
                    default=Path('./key.pyk') if Path('./key.pyk').is_file() else None, nargs=('?' if Path('./key.pyk').is_file() else 1))
    args_common_output(p)
def mode_sign(args: argparse.Namespace):
    man = Manifest.from_file(args.manifest)
    key = EdPrivK.from_private_bytes(args.key.read_bytes())
    eprint(f'Signing manifest with {base64.b85encode(key.private_bytes_raw()).decode()}')
    man['_']['pubkey'] = base64.b85encode(key.public_key().public_bytes_raw()).decode()
    man['_']['signature'] = base64.b85encode(key.sign(man.compile())).decode()
    try: man.verify()
    except InvalidSignature as e:
        raise RuntimeError('Something went wrong: the manifest failed verification; will not write') from e
    common_output(man, args)

def args_verify(p: argparse.ArgumentParser):
    args_common_manifestread(p, 'The path of the manifest to verify')
def mode_verify(args: argparse.Namespace):
    man = Manifest.from_file(args.manifest)
    man.verify()
    eprint('Verification successful')

def args_compile(p: argparse.ArgumentParser):
    args_common_manifestread(p, 'The path of the manifest to compile')
    args_common_output(p, False)
    p.add_argument('-m', '--mode', help='The mode to output in (defaults to "raw")', choices=('raw', 'literal', 'base85', 'hex', 'base64'), default='raw')
def mode_compile(args: argparse.Namespace):
    sys.stdout.buffer.write({
        'raw': lambda b: b,
        'literal': repr,
        'base85': lambda b: base64.b85encode(b).decode(),
        'hex': lambda b: base64.b16encode(b).decode(),
        'base64': lambda b: base64.b16encode(b).decode(),
    }[args.mode](Manifest.from_file(args.manifest).compile()))
    eprint() # print a newline to prevent terminal issues if stdout is not redirected

def args_transpose(p: argparse.ArgumentParser):
    args_common_manifestread(p, 'The path of the manifest to copy/move')
    args_common_output(p)
    p.add_argument('--move', help='Delete the source manifest (defaults to keeping it)', action='store_true')
def mode_transpose(args: argparse.Namespace):
    common_output(Manifest.from_file(args.manifest), args)
    if args.move: args.manifest.unlink()

def args_modify(p: argparse.ArgumentParser):
    args_common_manifestread(p, 'The path of the manifest to modify')
    class ModifyAction(argparse.Action):
        __slots__ = ('target',)
        def __init__(self, *args, const: tuple[str, str], **kwargs):
            self.target = const
            super().__init__(*args, const=const, nargs=1, **kwargs)
        def __call__(self, p: argparse.ArgumentParser, ns: argparse.Namespace, values: str, opt_str: str | None = None):
            if not hasattr(ns, 'modify'): ns.modify = {}
            if not self.target[0] in ns.modify: ns.modify[self.target[0]] = {}
            ns.modify[self.target[0]][self.target[1]] = literal_eval(values[0])
    to_argn = lambda f, sf: f'--{f}.{sf}'
    to_type = lambda t: type(t.__args__[0]).__qualname__ if (getattr(t, '__origin__', None) is typing.Literal) else getattr(t, '__qualname__', repr(t))
    to_agsh = lambda t: f', specifically one of: {t.__args__}'
    to_help = lambda f, sf, an: f'Subfield {sf!r} under field {f!r}, should have type {to_type(an)}{to_agsh(an) if (getattr(an, "__origin__", None) is typing.Literal) else ""}'
    for f,t in {
        '_': rs_BOOTSTRAP.ManifestDict__,
        'creation': rs_BOOTSTRAP.ManifestDict_creation,
        'metadata': rs_BOOTSTRAP.ManifestDict_metadata,
        'system': rs_BOOTSTRAP.ManifestDict_system}.items():
        grp = p.add_argument_group(f'Field "{f}"')
        for sf,an in t.__annotations__.items():
            grp.add_argument(to_argn(f, sf), help=to_help(f, sf, an), metavar=f'({to_type(an)})', action=ModifyAction, const=(f, sf))
    args_common_output(p)
def mode_modify(args: argparse.Namespace):
    if not getattr(args, 'modify', None):
        raise ValueError('No arguments given to modify, perhaps see --help?')
    man = Manifest.from_file(args.manifest)
    for fn,fv in args.modify.items():
        for sfn,v in fv.items():
            eprint(f'Modified field {fn}/{sfn}: {man[fn][sfn]!r} -> {v}')
            man[fn][sfn] = v
    common_output(man, args)
#</Header>

#> Main >/
# Parser
def parse_args():
    # create parsers
    p = argparse.ArgumentParser(sys.argv[0])
    sp = p.add_subparsers(dest='cmd', required=True)
    args_make(sp.add_parser('make', help='Create a new manifest'))
    args_update(sp.add_parser('update', help='Update a manifest\'s files:hashes'))
    args_sign(sp.add_parser('sign', help='Sign a manifest with a key'))
    args_verify(sp.add_parser('verify', help='Ensure that a manifest passes verification'))
    args_compile(sp.add_parser('compile', help='Compile a manifest as though it is going to be verified, then write the result to stdout (in "raw" mode, may cause pain to terminals)'))
    args_transpose(sp.add_parser('transpose', help='Render a manifest to a new path, optionally deleting the source or changing its format via inclusion or lack of of --render-json'))
    args_modify(sp.add_parser('modify', help='Directly reach in and modify values of a manifest. Values are given as Python-style "literals", parsed with ast.literal_eval. Keep in mind that shells may treat certain characters specially, so use quotes and escape characters (usually "\\") when needed'))
    # parse args
    args = p.parse_args()
    # modes
    {
        'make': mode_make,
        'update': mode_update,
        'sign': mode_sign,
        'verify': mode_verify,
        'compile': mode_compile,
        'transpose': mode_transpose,
        'modify': mode_modify,
    }[args.cmd](args)
# Execute parser
if (__name__ == '__main__') and ('idlelib.run' not in sys.modules):
    parse_args()
