#!/bin/python3

#> Imports
import re
import time
import traceback
# Files
import zipfile
from pathlib import Path
# Types
import typing
#</Imports

# RunServer Module
import RS
from RS import Config, BS

#> Header >/
class PluginManager:
    __slots__ = ('logger', 'ManifestLoader', 'ML', 'plugins')

    class Plugin:
        __slots__ = ('source', 'plugin_type')

        def __init__(self, src: Path, man: BS.Manifest):
            self.source = src
    
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
        def manifest_path_of(self, plug: Path) -> Path:
            # plug.glob('manifest.json', case_sensitive=False)
            ...
        # Plugin discovery
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
        all(map(self.ML.update_execute, self.ML.discover_manifests(Path(Config['plugins/plugins_path']))))
    def load_plugins(self):
        ...
    def start(self):
        ...
