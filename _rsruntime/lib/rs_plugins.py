#!/bin/python3

#> Imports
import re
import time
import traceback
# Files
from pathlib import Path
from zipfile import Path as zipPath, is_zipfile
from importlib import util as iutil
from zipimport import zipimporter
# Types
import typing
#</Imports

# RunServer Module
import RS
from RS import Config, BS
from RS.Types import PerfCounter

#> Header >/
class PluginManager:
    __slots__ = ('logger', 'ManifestLoader', 'ML', 'plugins')

    class Plugin:
        __slots__ = ('source', 'name', 'from_zip', 'zip_importer', 'spec', 'module')

        def __init__(self, src: Path | zipPath, name: str | None = None):
            self.source = src
            self.name = '<anonymous plugin>' if name is None else name
            self.from_zip = isinstance(src, zipPath)
            if self.from_zip:
                self.zip_importer = zipimporter(self.source)
                self.spec = iutil.spec_from_file_location(self.name, self.source.root)
                self.spec_or_zipimporter = zipimporter(self.source.root)
                self.plugin_spec = self.zip_importer.find_spec(self.source)
                return
            self.spec = iutil.spec_from_file_location(self.name, self.source)
            self.module = iutil.module_from_spec(self.spec)
            self.spec.loader.exec_module(self.module)
        def __getattr__(self, attr: str):
            if hasattr(self.module, attr):
                return getattr(self.module, attr)
            else: raise AttributeError(attr)
    
    class _ManifestLoader:
        __slots__ = ('pm', 'logger')
        safe_name = staticmethod(lambda n: re.sub(r'[^\d\w\-\.,]', '-', n.replace(' ', '_')).strip('_-.,'))
        unnamed_plugin = Config('plugins/orphans/unnamed_plugin_name', '_UNNAMED_PLUGIN_')
        unnamed_plugin_by = Config('plugins/orphans/unnamed_plugin_by', '_UNNAMED_PLUGIN_BY_{}')

        def __init__(self, pm: 'PluginManager'):
            self.pm = pm
            self.logger = self.pm.logger.getChild('ML')
        # Orphaned manifest handling
        def scrape_orphaned_manifests(self, base: Path):
            '''Under "base", finds all possible manifests and places them into their own folders'''
            if Config('plugins/orphans/ignore_orphans', False):
                self.logger.warning('Set to ignore orphans (config plugins/orphans/ignore_orphans)')
                return
            for mf in set(base.glob('*.json', case_sensitive=False)) | set(base.glob('*manifest*', case_sensitive=False)):
                if (not mf.is_file()) or (mf.suffix in {'.py', '.pyc'}): continue
                if mf.name in Config('plugins/orphans/skip', ()):
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
            if (man.m_name is not None) and (n := self.safe_name(man.m_name)): return n
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
        def discover_manifests(self, base: Path) -> typing.Generator[BS.Manifest, None, None]:
            '''Yields all manifests in a tree'''
            for p in sorted(base.iterdir(),
                            key=lambda p: (p.is_dir(), p.name.lower() != 'manifest.json', not p.match('*manifest*'), not p.match('*.json'), p.name)):
                if p.is_dir():
                    yield from self.discover_manifests(p)
                if (p.name.lower() == 'manifest.json') or p.match('*manifest*') or p.match('*.json'):
                    try:
                        yield BS.Manifest(p)
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
            try: man.update(man.upstream_manif()).execute()
            except Exception as e:
                self.logger.fatal(f'Could not update or execute manifest {man.m_name} because:\n{"".join(traceback.format_exception(e))}\n skipping...')
            return True
    
    def __init__(self):
        self.logger = RS.logger.getChild('PM')
        self.ManifestLoader = self.ML = self._ManifestLoader(self)
        self.plugins = {}
    def early_load_plugins(self):
        self.ML.scrape_orphaned_manifests(Path(Config('plugins/plugins_path', '_rsplugins/')))
        self.logger.infop('Loading manifests...')
        pc = PerfCounter()
        all(map(self.ML.update_execute, self.ML.discover_manifests(Path(Config['plugins/plugins_path']))))
        self.logger.infop(f'Manifests loaded after {pc}')
        pc = PerfCounter(sec='', secs='')
        for p in Path(Config['plugins/plugins_path']).glob('**/__early_load__.py'):
            self.logger.infop(f'Executing early load on {p} (T+{pc})')
            
    def load_plugins(self):
        bp = Path(Config['plugins/plugins_path'])
        self._traverse_plugins(sorted(set(bp.glob('**/__plugin__.py')) | set(bp.glob('**/*.rs.py')) | set(bp.glob('**/*.rs.zip'))), PerfCounter(sec='', secs=''), ())
    def _traverse_plugins(self, paths: set, pc: PerfCounter, zip_name: tuple[str]):
        captured = set()
        for p in paths: # note: add follow_symlinks=True upon release of 3.13
            if p.suffix.endswith('.zip'):
                if not is_zipfile(p):
                    self.logger.fatal(f'{p} is not a valid zipfile; cannot load, skipping')
                    continue
                zp = zipPath(p)
                self._traverse_plugins(sorted(set(zp.glob('__plugin__.py')) | set(zp.glob('*.rs.py'))), pc, zip_name + (zp.parent.name,))
                continue
            name = p.parent.name if (p.name == '__plugin__.py') else p.stem[:-3]
            self.logger.infop(f'Loading plugin: {name} (T+{pc})')
            if Config(f'plugins/skip_load/{name}', False):
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
            self.plugins[name] = self.Plugin(p, m.m_name if ((m := self.ML.nearest_manifest(p.parent)) is not None) else '.'.join(zip_name) if zip_name else name)
    def start(self):
        for n,p in self.plugins.items():
            if not hasattr(p, '__start__'): continue
            self.logger.infop(f'Starting plugin {n}')
            p.__start__(p)
