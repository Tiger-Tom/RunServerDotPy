#!/bin/python3

#> Imports
import argparse
from pathlib import Path
import typing
import sys
# Crytography
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey as EdPrivK, Ed25519PublicKey as EdPubK
#</Imports

#> Header
def create_key() -> EdPrivK:
    return EdPrivK.generate()
def read_key(path: Path = Path('key.pyk')) -> EdPrivK:
    with path.open('rb') as f:
        return EdPrivK.from_private_bytes(f.read())
def write_key(priv: EdPrivK, path: Path = Path('key.pyk')):
    with path.open('wb') as f:
        f.write(priv.private_bytes_raw())
def signstr(priv: EdPrivK, data: bytes, long: bool = False) -> str | tuple[int]:
    dat = priv.sign(data)
    if long: return tuple(dat)
    return base64.b85encode(dat).decode()
def verstr(pub: EdPubK, sig: str | tuple[int], msg: bytes):
    if isinstance(sig, str): sig = base64.b85decode(sig)
    pub.verify(bytes(sig), msg)
eprint = lambda *a,**kw: print(*a, **kw, file=sys.stderr)
#</Header

#> Main >/
if (__name__ == '__main__') and ('idlelib.run' not in sys.modules):
    p = argparse.ArgumentParser(prog='pysign.py')
    sp = p.add_subparsers(dest='mode')
    gp = sp.add_parser('generate')
    gp.add_argument('path', help='The path to write the key to, defaults to writing to stdout', type=Path, default=None, nargs='?')
    ep = sp.add_parser('extract')
    kr = ep.add_argument_group()
    kr.add_argument('--extract-priv', '-priv', help='Print the public key', action='store_true')
    kr.add_argument('--extract-pub','-pub', help='Print the private key', action='store_true')
    om = ep.add_argument_group()
    modes = []
    def add_omode(name: str, func: typing.Callable[[bytes], str]):
        om.add_argument(
            f'--in-{name}', f'-{name}',
            help=f'Print the selected keys in {name} format',
            action='append_const', const=(name, func), dest='output', default=[])
        modes.append((name, func))
    add_omode('raw', lambda b: b.decode(errors='backslashreplace'))
    add_omode('repr', lambda b: repr(b))
    add_omode('base10', lambda b: repr(tuple(b)))
    add_omode('base16', base64.b16encode)
    add_omode('base32', base64.b32encode)
    add_omode('base32_hex', base64.b32hexencode)
    add_omode('base64', base64.b64encode)
    add_omode('base64_standard', base64.standard_b64encode)
    add_omode('base64_urlsafe', base64.urlsafe_b64encode)
    add_omode('base85', base64.b85encode)
    add_omode('ascii85', base64.a85encode)
    om.add_argument('--in-all', help='Print in all modes', action='store_true')
    ep.add_argument('--print-delim', help='What to print after each print-type (types such as "base64", "base10", etc.) (defaults to a newline)', default='\n')
    ep.add_argument('--print-header-sep', help='What to print between print-type headers and their values (default: ": ")', default=': ')
    ep.add_argument('--key-delim', help='What to print between the two keys ONLY IF they are both printed with (defaults to a newline, equivelant to two if --print-delim is also a newline)', default='\n')
    ep.add_argument('--no-headers', help='Don\'t print headers (key names and output mode names)', action='store_true')
    ep.add_argument('--col-names', help='The column names to print as headers (default: "private" "public")', nargs=2, default=('private', 'public'))
    ep.add_argument('path', help='The path to read the key from, defaults to reading from stdin', type=Path, default=None, nargs='?')
    args = p.parse_args()
    if args.mode == 'generate':
        key = create_key()
        eprint(f'Generated key [hex]: private {key.private_bytes_raw().hex()}')
        eprint(f'                     public  {key.public_key().public_bytes_raw().hex()}')
        if args.path is None:
            sys.stdout.buffer.write(key.private_bytes_raw())
            exit()
        with args.path.open('wb') as f:
            f.write(key.private_bytes_raw())
        exit()
    elif args.mode != 'extract':
        p.print_help()
        exit(1)
    assert args.extract_pub or args.extract_priv, 'No keys selected for extraction'
    assert args.output or args.in_all, 'No output modes selected'
    if args.path is None: key = EdPrivK.from_private_bytes(sys.stdin.buffer.read())
    else: key = read_key(args.path)
    def print_key(n: int, k: bytes):
        if not args.no_headers: print(args.col_names[n], end=args.print_delim)
        for n,f in (modes if args.in_all else args.output):
            if not args.no_headers: print(n, end=args.print_header_sep)
            fk = f(k); print(fk.decode() if isinstance(fk, bytes) else fk, end=args.print_delim)
    if args.extract_priv:
        print_key(0, key.private_bytes_raw())
        if args.extract_priv: print(args.key_delim, end='')
    if args.extract_pub:
        print_key(1, key.public_key().public_bytes_raw())
