#!/bin/python3

#> Imports
import sys, os
import inspect
from pathlib import Path
from functools import cache

from pycallgraph2 import Config, GlobbingFilter, PyCallGraph
from pycallgraph2.output import GephiOutput, GraphvizOutput
from pycallgraph2.grouper import Grouper
#</Imports

# Try to get Bootstrapper
if (p := Path.cwd().as_posix()) not in sys.path: sys.path.append(p)
if not Path('./_rsruntime/rs_BOOTSTRAP.py').exists():
    if Path('../_rsruntime/rs_BOOTSTRAP.py').exists():
        os.chdir('..')
        sys.path.append(Path.cwd().as_posix())
    else:
        raise ModuleNotFoundError('Could not find [.]./_rsruntime/rs_BOOTSTRAP.py')

# Monkey-patch currently broken pycallgraph2 memory profiler
#import resource
#from pycallgraph2 import memory_profiler
#memory_profiler._get_memory = lambda pid: resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024

# Configure
config = Config(memory=False)
## Filtering
def RunServerFilter(full_name: str | None = None):
    return any((
        (full_name == '__main__'),
        (full_name == '__new__'),
        *((full_name == pfx) or full_name.startswith(f'{pfx}.') for pfx in (
            '_rsruntime', 'RS',
            'Manifest',
            'cryptography.hazmat.primitives.asymmetric.ed25519',
            'SourceFileLoader',
        )),
    ))

config.trace_filter = RunServerFilter
## Trace grouper
def guess_catch_methods(m: 'Module', fn: str) -> str | None:
    for n in dir(m):
        c = getattr(m, n)
        if not inspect.isclass(c): continue # is not a class
        if c.__module__ != m.__name__: continue # external class
        if fn in dir(c):
            return n
    return None
def split_mod(fullname: tuple[str, ...]) -> tuple[str, str] | None:
    working = []
    collect = ()
    for n in fullname:
        working.append(n)
        if '.'.join(working) in sys.modules:
            collect = tuple(working)
    if collect: return ('.'.join(collect), '.'.join(fullname[len(collect):]))
    return None
def trace_to(name: str) -> str | None:
    if len(ns := name.split('.')) == 2:
        return trace_to(ns[0]) or trace_to(ns[1])
    for n,m in sys.modules.items():
        if not any((n.startswith(f'{pfx}.') for pfx in ('_rsruntime', 'RS'))):
            continue
        if name in dir(m): return n
        if (sm := guess_catch_methods(m, name)): return f'{n}.{sm}.{name}'
    return None

@cache
def RunServerGrouper(full_name: str | None = None) -> str | None:
    if full_name is None: return None
    full_name = full_name.split('.')
    if full_name[0] != '_rsruntime':
        return '<!uncategorized!>'
    mf = split_mod(full_name)
    if mf is None:
        return '<!uncategorized!>'
    if mf[1].startswith('<'): # lambda, etc.
        return mf[0]
    if m := sys.modules.get(mf[0], None):
        if mf[1] in dir(m):
            return m.__name__
    if m := trace_to(mf[1]):
        return m
    print(f'uncat:{full_name}')
    return '<!uncategorized!>'

config.trace_grouper = RunServerGrouper
## Output
Path('./docs/startup-trace/').mkdir(parents=True, exist_ok=True)
class GraphvizOutputX(GraphvizOutput):
    def prepare_graph_attributes(self):
        super().prepare_graph_attributes()
        self.graph_attributes['graph'] |= {
            #'strict': 'true',
            'overlap': 'prism',
            'overlap_shrink': 'true',
            'splines': 'true',
        }
        self.graph_attributes['edge'] |= {
            # Head
            'fillcolor': 'red',
            # Body
            'penwidth': '2px',
            'color': '#00000080',
        }
        self.graph_attributes['node'] |= {
            'z': '2',
        }
    def done(self):
        print(f'{self}: rendering {self.output_file} via {self.output_type}')
        otype = self.output_type
        self.output_type += ' -x -LT1' # shell=True is always interesting
        super().done()
        self.output_type = otype
outputs = tuple(
    GraphvizOutputX(output_file=f'./docs/startup-trace/{tool}.{ot}', output_type=ot, tool=tool,
                    group_font_size=20, font_size=14)
    for ot in ('svg',)#('png', 'pdf', 'svg')
    for tool in ('dot', 'neato', 'fdp', 'sfdp', 'circo', 'twopi', 'osage', 'patchwork')
)

#> Header >/
with PyCallGraph(config=config, output=outputs):
    from _rsruntime.rs_BOOTSTRAP import Bootstrapper
    RS_Bootstrapper = Bootstrapper()
    RS_Bootstrapper.is_dry_run = RS_Bootstrapper.args.dry_run = True
    RS_Bootstrapper.bootstrap()
