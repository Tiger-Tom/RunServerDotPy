#!/bin/python3

'''
    Documentation is generated from the source code.
    Documentation is quite probably incomplete or inaccurate, just look at this script!
'''

#> Imports
import re
import inspect
import typing
import os
import sys
from pathlib import Path
from logging import ERROR
from types import SimpleNamespace
from functools import wraps
#</Imports

#eprint = lambda *k,**kw: print(*k, **kw, file=sys.stderr)
eprint = lambda *k,**kw: ...

# Try to get Bootstrapper
if (p := Path.cwd().as_posix()) not in sys.path: sys.path.append(p)
if not Path('./_rsruntime/rs_BOOTSTRAP.py').exists():
    if Path('../_rsruntime/rs_BOOTSTRAP.py').exists():
        os.chdir('..')
        sys.path.append(Path.cwd().as_posix())
    else:
        raise ModuleNotFoundError('Could not find [.]./_rsruntime/rs_BOOTSTRAP.py')
from _rsruntime.rs_BOOTSTRAP import Bootstrapper

#> Header
# Helper functions
## Indentation
nleading_whitespace = re.compile(r'^(\s*\n)')
leading_whitespace = re.compile(r'^( *)[^ ].*$', re.MULTILINE)
whitespace_line = re.compile('^ +$', re.MULTILINE)
def render_indents(s: str) -> str:
    s = whitespace_line.sub('\n', nleading_whitespace.sub('', s.lstrip('\n').rstrip()))
    if not leading_whitespace.search(s): return s # no leading whitespace at all
    lspace = min(len(m.group(1)) for m in leading_whitespace.finditer(s) if m)
    return '\n'.join(line[lspace:] for line in s.split('\n'))
def indent_to_level(s: str) -> typing.Generator[tuple[int, str], None, None]:
    buff = []
    prev = 0
    _lines = tuple(len(m.group(1)) for m in leading_whitespace.finditer(s) if m and len(m.group(1)))
    if not _lines: # no indentation
        yield from ((0, l) for l in s.split('\n'))
        return
    lspace = min(_lines)
    for l in s.split('\n'):
        if (m := leading_whitespace.fullmatch(l)) and len(m.group(1)):
            yield (len(m.group(1)) // lspace), l.lstrip(' ')
        else: yield 0, l
## Functions
def func_get_name(func: typing.Callable):
    func = getattr(func, '__func__', func) # func func func func
    return func.__name__ if hasattr(func, '__name__') else func.__qualname__
## Translation
def _translate_item(i: str | typing.Any, eglobs: dict, elocs: dict, *, _indirect: bool = False) -> str | typing.Any:
    if getattr(i, '__origin__', None) is typing.Union:
        return ' | '.join(_translate_item(p, eglobs, elocs) for p in i.__args__)
    elif (i is None) or isinstance(i, type(None)): return str(None)
    elif not isinstance(i, str):
        eprint(f'{type(i)=} {i=} {repr(i)=}')
        return _translate_item(i.__name__ if hasattr(i, '__name__') else getattr(i, '__qualname__', str(i)), eglobs, elocs, _indirect=True)
    if not _indirect:
        try: return _translate_item(eval(i), eglobs, elocs) # !
        except: pass
    match i.split('.'):
        case _: pass
    return i
def translate_sig(s: inspect.Signature, eglobs: dict = {}, elocs: dict = {}, *, paramlen: int = 2, longindent: str = '    ') -> typing.Generator[str, None, None]:
    yield '('
    long = None if len(s.parameters)/(paramlen+1) <= 1 else 0
    if long is not None:
        yield '...)'
        if (r := s.return_annotation) is not inspect._empty:
            yield f' -> {_translate_item(r, eglobs, elocs)}'
        yield '\n```\n<details><summary>Parameters...</summary>\n```python\n'
    for i,p in enumerate(s.parameters.values()):
        if i:
            if long == 0: yield f',\n{longindent}'
            else: yield ', '
        elif long is not None: yield f'{longindent}'
        yield p.name
        hasann = p.annotation is not inspect._empty
        if hasann:
            yield ': '
            yield _translate_item(p.annotation, eglobs, elocs)
        if p.default is not inspect._empty:
            if hasann: yield ' = '
            else: yield '='
            if isinstance(p.default, str):
                yield repr(p.default)
            else: yield _translate_item(p.default, eglobs, elocs)
        if long is not None:
            long += 1
            if long > paramlen: long = 0
    if long is None:
        yield ')'
        if (r := s.return_annotation) is not inspect._empty:
            yield f' -> {_translate_item(r, eglobs, elocs)}'
        yield '\n```'
    else: yield '\n```\n</details>'
    
    
# Markdown classes
class mdHeader(str):
    __slots__ = ()
    patt = re.compile(r'[^\w]')
    def linkable(self) -> str:
        return self.patt.sub('', self.replace(' ', '-'))
    def link(self, name: str | None = None) -> str:
        if name is None: name = self
        return f'[{name}](#{self.linkable()})  '
    def render(self, level: int = 0) -> str:
        return f'#{"#"*level} {self}'
class mdCode(str):
    __slots__ = ()
    def render(self):
        return f'```python\n{self.replace("\\", "\\\\").replace("`", r"\`")}\n```'
class mdBlockQuote(str):
    __slots__ = ()
    def irender(self, level: int = 0) -> typing.Generator[str, None, None]:
        for line in render_indents(self).split('\n'):
            yield f'>{">"*int(level)} {line}'
    def render(self, level: int = 0) -> str:
        return '\n'.join(self.irender(level))
# Complex markdown functions
def md_docstr(dstr: str):
    if dstr is None:
        yield mdBlockQuote('<no doc>').render(0)
        return
    workin = []; prev = 0
    for lvl,line in indent_to_level(render_indents(dstr)):
        if workin and prev != lvl:
            yield mdBlockQuote('\n'.join(workin)).render(prev)
            workin = []; prev = lvl
        workin.append(line)
    yield mdBlockQuote('\n'.join(workin)).render(prev)
def md_function(func: typing.Callable, level: int = 0):
    build = []
    sig = inspect.signature(func)
    build.append(mdHeader(f'{func_get_name(func)}{"(...)" if sig.parameters else "()"}').render(level))
    build.append(f'```python\n{"@staticmethod\n" if not hasattr(func, "__self__") else "@classmethod\n" if inspect.isclass(func.__self__) else ""}'
                 f'{"@abstractmethod\n" if getattr(func, "__isabstractmethod__", False) else ""}'
                 f'def {func_get_name(func)}{"".join(translate_sig(sig))}')
    if c := getattr(getattr(func, '__func__', getattr(func, '__wrapped__', func)), '__code__', None):
        p = Path(c.co_filename).relative_to(Path.cwd())
        build.append(f'[`{p}@{c.co_firstlineno}:{max(lent[-1] for lent in c.co_lines() if isinstance(lent[-1], int))}`](/{p}#L{c.co_firstlineno})  ')
    build.extend(md_docstr(func.__doc__))
    return '\n'.join(build)
# RS
def _md_rs_heldclass(headl: str, heads: str, level: int, cls: type, long: str, short: str | None = None) -> str | None:
    eprint(f'render {headl=} {heads=} {level=} {cls=} {long=} {short=}')
    if (p := Path(f'docs/doc/._headoverride/{headl}/{long}.md')).exists():
        eprint(f'render {headl=} {long=} overridden @ {p=}')
        return p.read_text()
    if cls is None: return None
    build = []
    build.append(mdHeader(f'`{long}` (`{headl}.{long}` | `{heads}.{short or long}`)').render())
    if m := sys.modules.get(getattr(cls, '__module__', None), None):
        p = Path(m.__file__).relative_to(Path.cwd())
        build.append(f'[`{p}`](/{p} "Source")  ')
    rp = f'parts/{headl.replace(".", "/")}/{long}.md'
    build.append(f'[Standalone doc: {rp}](./{rp})  ')
    if d := getattr(cls, '__doc__', None): build.append('\n'.join(md_docstr(d)))
    #if d := getattr(getattr(cls, '__init__', None), '__doc__', None):
    #    build.append('\n'.join(md_docstr(d)))
    if inspect.ismodule(cls):
        if not cls.__file__.startswith(str(Path.cwd())): return None
        for sn in sorted(dir(cls)):
            if hasattr(cls, '__all__'):
                if sn not in getattr(cls, '__all__', set()): continue
            elif not sn[0].isupper(): continue
            #elif sn.startswith('_'): continue
            build.append('')
            eprint(f'subrender {sn=}')
            build.append(md_rs_heldclass(f'{headl}.{long}', f'{heads}.{short or long}', level + 1, getattr(cls, sn), sn))
        return '\n\n'.join(b for b in build if b is not None)
    membs = tuple((a, getattr(cls, a)) for a in dir(cls) if (not a.startswith('_')) and hasattr(cls, a))
    for f in sorted((f for n,f in membs if (inspect.isroutine(f) and callable(f))), key=func_get_name):
        build.append('')
        build.append(md_function(f, level + 1))
    return '\n'.join(build)
def md_rs_heldclass(headl: str, heads: str, level: int, cls: type, long: str, short: str | None = None) -> str | None:
        r = _md_rs_heldclass(headl, heads, level, cls, long, short)
        if r is None: return None
        rp = Path(f'parts/{headl.replace(".", "/")}/{long}.md')
        p = Path('docs/autodocs/', rp)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(r if not level else _md_rs_heldclass(headl, heads, 0, cls, long, short))
        return f'{r}\n**[Standalone: {rp}](./{rp})**'
#</Header

#> Main >/
# Load-in RS
## Bootstrapper
bs = Bootstrapper()
bs.root_logger.setLevel(ERROR)
bs.args.no_color = bs.args.quiet = True
bs.args.dry_run = bs.is_dry_run = True
## Entrypoint
RS_outer = bs.access_entrypoint('./_rsruntime/rs_ENTRYPOINT.py')
RS = bs.stage_entrypoint(RS_outer)
bs.close()

if not os.getenv('RSDOC_NORUN'):
    dpath = Path('docs/autodocs/RunServer.md')
    dpath.parent.mkdir(parents=True, exist_ok=True)
    dfile = dpath.open('w')
    def dprint(*k, **kw):
        print(*k, **kw)
        print(*k, **kw, file=dfile)

    if not os.getenv('RSDOC_NOHEAD'):
        dprint('*This documentation was generated with `devel/makedoc.py`*')
        dprint('\n'.join(md_docstr(__doc__)), end='\n\n')

    dprint(mdHeader('`RunServer` (imported as `RS`)').render())
    dprint('\n'.join(md_docstr(RS.__doc__)), end='\n\n')
    dprint('\n\n\n'.join((r for r in (md_rs_heldclass('RunServer', 'RS', 0, getattr(RS, l), l, s) for l,s in zip(RS.__slots__[1::2], RS.__slots__[2::2])) if r is not None)))

    dfile.close()
