#!/bin/python3

#> Imports
import types
import typing
import time
import sys
#</Imports

#> Header >/
class BetterPPrinter:
    _default_config = {
        # tokens
        'token_indent': '    ',
        # types
        'deserve_newline': (dict, tuple, list),
        # type groups w/ config
        'listlike': {
            # <type>: (<append comma when there's only one element>, <brackets>, <line-ending comma (or if there's only one element)>, <line separater>, <single-lining comma>, <what to write when it's empty>),
            tuple: (True, '()', ',', '\n', ', ', None),
            list: (False, '[]', ',', '\n', ', ', None),
            set: (False, '{}', ',', '\n', ', ', 'set()'),

        },
        'maplike': {
            # <type>: (<prepend opening bracket with indent>, <opening bracket>, <closing bracket>, <key-val separator>, <key-value pair separator>),
            dict: (False, '{\n', '}', ': ', ',\n'),
        },

    }
    __slots__ = tuple(_default_config)
    def __init__(self, **config):
        for k,v in (self._default_config | config).items():
            setattr(self, k, v)
    def format(self, obj, *, _indent_: int = 0) -> typing.Generator[str, None, None]:
        if isinstance(obj, tuple(self.maplike.keys())):
            indentopen, opener, closer, keysep, pairsep = self.maplike[type(obj)]
            if indentopen: yield self.indent * _indent_
            yield opener
            for k,v in obj.items():
                yield self.token_indent * (_indent_ + 1)
                yield from self.format(k, _indent_=_indent_+1)
                yield keysep
                yield from self.format(v, _indent_=_indent_+1)
                yield pairsep
            yield self.token_indent * _indent_
            yield closer
        elif isinstance(obj, tuple(self.listlike.keys())):
            istup, brackets, nlcomma, nlchar, slcomma, onempty = self.listlike[type(obj)]
            if len(obj) == 0:
                yield brackets if onempty is None else onempty
            elif len(obj) == 1:
                yield brackets[0]
                yield from self.format(obj[0], _indent_=_indent_+1)
                if istup: yield nlcomma
                yield brackets[1]
            else:
                yield brackets[0]
                for i,o in enumerate(obj):
                    newl = isinstance(o, self.deserve_newline)
                    if newl:
                        yield nlchar; yield self.token_indent * _indent_
                    yield from self.format(o, _indent_=_indent_+1)
                    if newl: yield nlcomma
                    elif i < len(obj)-1: yield slcomma
                yield brackets[1]
        else: yield repr(obj)
    def formats(self, obj, joiner: str = '') -> str:
        return joiner.join(self.format(obj))
    def writes(self, obj, fp=sys.stdout, end: str = '\n', delay: float | None = None, collect: list | typing.Callable[[str], None] | None = None):
        for tok in self.format(obj):
            fp.write(tok)
            if delay: time.sleep(delay) # for aesthetic or testing purposes
            if collect is not None:
                if callable(collect): collect(tok)
                else: collect.append(fp)
        fp.write(end)
        return collect

man = {
    '_metadata': {
        'name': 'rsruntime',
        'public_key': '>(KYi?x2Da4c6nQ!DQrs3EHbwUtG0963<g&*-K6d',
        'signature': 'LladRCpLIM*?h^Cv*6B5o?w~OXe9nIdJJWd6qFh9F=v?UX>?xOU$G*#F#U3tSX@v;8}^g_pdLt{PCxq!',
        'manifest_upstream': None,
        'file_upstream': None,
        'creation': {
            'time': 1700169783,
            'system': {
                'platform': 'linux',
                'os_release': '6.6.1-arch1-1',
                'os_version': '#1 SMP PREEMPT_DYNAMIC Wed, 08 Nov 2023 16:05:38 +0000',
                'arch': 'x86_64',
                'hostname': 'luthien',
                'py_version_full': '3.11.5 (main, Sep  2 2023, 14:16:33) [GCC 13.2.1 20230801]',
                'py_implementation': 'cpython',
                'maxsize': 9223372036854775807,
                'maxunicode': 1114111,
            },
            'by': None,
            'for': {
                'os': 'posix',
                'python': (3,11,5,),
                'encoding': 'utf-8',
            },
            'contact': None,
        },
    },
    'rs_BOOTSTRAP.py': '`P!4ydjgV_2~H#<V$Bk(9ga^k',
    'rs_ENTRYPOINT.py': '+i=Ss+^u#GcM$Yn=dMKt19mXR',
    'rs_Manifest.py': '`-ehbkh~nKr@cNTK)SBsnK^=n',
    'lib/rs_config.py': 'ZeaBXJP_A^pcBxSRG7s<behw<',
    'lib/rs_exceptionhandlers.py': 'Lz~v_`&52Y)qHgYBdIxjm~(X#',
    'lib/rs_lineparser.py': 'MxdxXIf)0X%_n&1vo)07n?CRz',
    'lib/rs_plugins.py': 'W077Qx!X$ud-&_;oPPT`)1&9?',
    'lib/rs_servmgr.py': '(9>>xeKK79XHEq0eVX~<<_C&*',
    'lib/rs_userio.py': 'LB>ckWy(55bpfRp-YRB~f-eV4',
    'util/fbd.py': 'T#~q8EgqYN5&jNf8V)VDRNFIu',
    'util/hooks.py': 'w2uX!2#)VI=H4HInbV5{dnLak',
    'util/locked_resource.py': 'dOkEl!$oxIz?Fb6Q-T>GE>8}t',
    'util/perftimer.py': 'O{L&{OnVL#;4F%=81=1@B52*p',
    'util/timer.py': 'xoD)=ehS~E%(Yu&y2op9$!cQ1',
}

pp = BetterPPrinter()
