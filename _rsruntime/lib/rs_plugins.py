#!/bin/python3

#> Imports
import re
import time
import traceback
# Files
from pathlib import Path
from importlib import util as iutil, machinery as imach
# Types
import typing
from types import ModuleType
#</Imports

# RunServer Module
import RS
from RS import Config, BS
from RS.ShaeLib.types.fbd import INIBackedDict
from RS.ShaeLib.timing import PerfCounter

#> Header >/
class PluginManager:
    __slots__ = ('logger', 'ManifestLoader', 'ML', 'plugins')

    class Plugin:
        __slots__ = ('source', 'base', 'name', 'logger', 'config', 'c', 'module', 'modules', 'specs')

        Config.set_default('plugins/config/base_path', './_rsconfig/plugins/')

        def __init__(self, src: Path, name: str | None = None):
            self.source = src
            self.base = src.parent
            self.name = '<anonymous plugin>' if name is None else name
            self.logger = RS.logger.getChild('PM').getChild(self.name)
            self.config = self.c = Config.__class__(Path(Config['plugins/config/base_path'], f'{self.name}.ini'))
            self.modules = {}; self.specs = {}
            self.module = self._chainload_tomod(self.name, self.source)
            self._populate(self.module)
            self._chainload_execute(self.name)
        def __getattr__(self, attr: str):
            if hasattr(self.module, attr):
                return getattr(self.module, attr)
            else: raise AttributeError(attr)

        def chainload(self, module: Path | str) -> ModuleType:
            path = self.base / module
            name = path.with_suffix('').as_posix().replace('/', '.')
            self.logger.info(f'Chainloading {module} ({name}) from {path}')
            self._populate(self._chainload_tomod(name, path))
            self._chainload_execute(name)
            return self.modules[name]

        def _chainload_tomod(self, name: str, path: Path) -> ModuleType:
            self.logger.debug(f'Chainloading {name}: converting {path} to spec and module')
            self.specs[name] = iutil.spec_from_file_location(path.with_suffix('').as_posix().replace('/', '.'), path)
            self.modules[name] = iutil.module_from_spec(self.specs[name])
            return self.modules[name]
        def _populate(self, module: ModuleType):
            self.logger.debug(f'Populating {module}')
            module.this = self
            module._ = RS._
        def _chainload_execute(self, name: str):
            self.logger.debug(f'Chainloading {name}: executing {self.modules[name]} via {self.specs[name].loader}')
            self.specs[name].loader.exec_module(self.modules[name])

    class _ManifestLoader:
        __slots__ = ('pm', 'logger')
        safe_name = staticmethod(lambda n: re.sub(r'[^\d\w\-\.,]', '-', n.replace(' ', '_')).strip('_-.,'))
        unnamed_plugin = Config('plugins/orphans/unnamed_plugin_name', '_UNNAMED_PLUGIN_')
        unnamed_plugin_by = Config('plugins/orphans/unnamed_plugin_by', '_UNNAMED_PLUGIN_BY_{}')

        # Setup config
        Config.mass_set_default('plugins/orphans', ignore_orphans=False, skip=())

        def __init__(self, pm: 'PluginManager'):
            self.pm = pm
            self.logger = self.pm.logger.getChild('ML')
        # Orphaned manifest handling
        def scrape_orphaned_manifests(self, base: Path):
            '''Under "base", finds all possible manifests and places them into their own folders'''
            if Config['plugins/orphans/ignore_orphans']:
                self.logger.warning('Set to ignore orphans (config plugins/orphans/ignore_orphans)')
                return
            for mf in set(base.glob('*.ini', case_sensitive=False)) | set(base.glob('*.json', case_sensitive=False)) | set(base.glob('*manifest*', case_sensitive=False)):
                if (not mf.is_file()) or (mf.suffix in {'.py', '.pyc'}): continue
                if mf.name in Config['plugins/orphans/skip']:
                    self.logger.warning(f'Set to skip orphan {mf.name} (config plugins/orphans/skip)')
                    continue
                try: man = BS.Manifest(mf)
                except Exception as e:
                    self.logger.warning(f'Could not load orphaned manifest from {mf}, caught {e!r}')
                    continue
                if 'manifest' not in mf.stem.lower(): # name may be guessed by manifest filename
                    pp = self.available_path(base / mf.stem, self_ok_if_is_file=True)
                else: # manifest filename may result in ambiguity
                    pp = self.available_path(base / self.name_from_manif(man))
                pp.mkdir(parents=True)
                self.logger.warning(f'Relocating orphaned manifest from {mf} to {pp / "MANIFEST.json"}')
                mf.rename(pp / 'MANIFEST.json')
        ## Path utils
        def name_from_manif(self, man: BS.Manifest) -> str:
            '''Generates a name from a manifest's "name" field, "by" field, or a fallback'''
            if (man.name is not None) and (n := self.safe_name(man.name)): return n
            if (man.m_creation['by'] is not None) and (n := self.safe_name(man.m_creation['by'])):
                return self.unnamed_plugin_by.format(n)
            return self.unnamed_plugin
        def available_path(self, path: Path, self_ok_if_is_file: bool = False) -> Path: # path self path path
            '''Checks if a path already exists, adding a suffix if it does'''
            if not path.exists(): return path
            if self_ok_if_is_file and path.is_file(): return path
            np = path.with_suffix(f'{path.suffix}.{sum(1 for _ in path.parent.glob(f"{path.name}.*"))}')
            if not np.exists(): return np
            # there must be a gap or unreliable naming, fallback to using current time as suffix
            return self.available_path(path.with_suffix(f'{path.suffix}.{round(time.time())}'))
        # Manifest discovery
        @staticmethod
        def _discover_manifests_key(p: Path) -> int:
            '''
                p is manifest.ini: 0; manifest.json: 1
                p has "manifest" in name: 2
                p has .ini extension: 3; .json extension: 4
                p is not a file: 8
                otherwise: 10
            '''
            if not p.is_file(): return 8
            elif p.suffix == '.ini':
                if p.name.lower() == 'manifest.ini': return 0
                return 3
            elif p.suffix == '.json':
                if p.name.lower() == 'manifest.json': return 1
                return 4
            elif 'manifest' in p.name: return 2
            else: return 10
        def discover_manifests(self, base: Path) -> typing.Generator[BS.Manifest, None, None]:
            '''Yields all manifests in a tree'''
            for p in sorted(base.iterdir(), key=self._discover_manifests_key):
                if p.is_dir():
                    yield from self.discover_manifests(p)
                elif self._discover_manifests_key(p) < 8:
                    try: yield BS.Manifest.from_file(p)
                    except Exception as e:
                        self.logger.error(f'Could not load {p} as manifest ({e!r}), continuing anyway')
                    else: continue
        def nearest_manifest(self, base: Path) -> BS.Manifest | None:
            '''
                Returns the nearest manifest to "base"
                    current implementation returns next of discover_manifests() or None on a StopIteration
            '''
            try: return next(self.discover_manifests(base))
            except StopIteration: return None
        # Manifest convenience
        def update_execute(self, man: BS.Manifest) -> typing.Literal[True]:
            '''
                Updates and executes a manifest
                    always returns false, so that "any" can be used to resolve map()
            '''
            try: man()
            except Exception as e:
                self.logger.fatal(f'Could not update or execute manifest {man.name} because:\n{"".join(traceback.format_exception(e))}\n skipping...')
            return True

    # Setup config
    Config.set_default('plugins/plugins_path', './_rsplugins/')
    Config.mass_set_default('plugins/glob/', early_load='**/__early_load__.py', basic='**/__plugin__.py', standalone='**/*.rs.py')

    unsafe_name = re.compile(r'^[^\w\d\- ;]+$')

    def __init__(self):
        self.logger = RS.logger.getChild('PM')
        self.ManifestLoader = self.ML = self._ManifestLoader(self)
        self.plugins = {}
        Path(Config['plugins/plugins_path']).mkdir(parents=True, exist_ok=True)
    def early_load_plugins(self):
        self.ML.scrape_orphaned_manifests(Path(Config['plugins/plugins_path']))
        self.logger.infop('Loading manifests...')
        pc = PerfCounter()
        all(map(self.ML.update_execute, self.ML.discover_manifests(Path(Config['plugins/plugins_path']))))
        self.logger.infop(f'Manifests loaded after {pc}')
        pc = PerfCounter(sec='', secs='')
        for p in Path(Config['plugins/plugins_path']).glob(Config['plugins/glob/early_load']):
            self.logger.infop(f'Executing early load on {p} (T+{pc})')

    def load_plugins(self):
        bp = Path(Config['plugins/plugins_path'])
        self._traverse_plugins(sorted(set(bp.glob(Config['plugins/glob/basic'])) | set(bp.glob(Config['plugins/glob/standalone']))), PerfCounter(sec='', secs=''))
    def _traverse_plugins(self, paths: typing.Iterable[Path], pc: PerfCounter):
        captured = set()
        for p in paths: # note: add follow_symlinks=True upon release of 3.13
            name = self.unsafe_name.sub('_', p.parent.name if (p.name == '__plugin__.py') else p.stem[:-3])
            self.logger.infop(f'Loading plugin: {name} (T+{pc})')
            if Config(f'plugins/skip_load/p__{name}', False):
                self.logger.warning(f'Plugin {name} has been skipped (config plugins/skip_load/{name})')
                continue
            for c in captured:
                if p.parent.is_relative_to(c.parent):
                    self.logger.fatal(f'Plugin file {p} is relative to already loaded {c}: a tree higher up has already been loaded! Cannot load plugin, skipping')
                    continue
                if c.is_relative_to(p):
                    self.logger.fatal(f'Already loaded {c} is relative to plugin file {p}: a tree lower down has already been loaded! Cannot load plugin, skipping')
                    continue
            if name in self.plugins:
                self.logger.fatal(f'Name {name} already exists in loaded plugins: a plugin with the same name loaded first! Cannot load plugin, skipping')
                continue
            captured.add(p)
            self.plugins[name] = self.Plugin(p, m.name if ((m := self.ML.nearest_manifest(p.parent)) is not None) else name)

    def _pmagic(self, method: str, log: str = 'Called {plug_name}.__{method}__'):
        for n,p in self.plugins.items():
            if not hasattr(p, f'__{method}__'): continue
            self.logger.infop(log.format(plugin=p, plug_name=n, method=method))
            getattr(p, f'__{method}__')(p)
    def start(self):
        self._pmagic('start', 'Starting plugin {plug_name}')
    def restart(self):
        self._pmagic('restart', 'Restarting plugin {plug_name}')
