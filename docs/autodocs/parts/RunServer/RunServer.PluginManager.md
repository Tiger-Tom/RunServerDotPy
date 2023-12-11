# `PluginManager` (`RunServer.PluginManager` | `RS.PM`)
[`_rsruntime/lib/rs_plugins.py`](/_rsruntime/lib/rs_plugins.py "Source")  
[Standalone doc: parts/RunServer/RunServer.PluginManager.md](RunServer.PluginManager)  

## early_load_plugins()
```python
def early_load_plugins()
```

[`_rsruntime/lib/rs_plugins.py@173:181`](/_rsruntime/lib/rs_plugins.py#L173)

<details>
<summary>Source Code</summary>

```python
def early_load_plugins(self):
    self.ML.scrape_orphaned_manifests(Path(Config['plugins/plugins_path']))
    self.logger.infop('Loading manifests...')
    pc = PerfCounter()
    all(map(self.ML.update_execute, self.ML.discover_manifests(Path(Config['plugins/plugins_path']))))
    self.logger.infop(f'Manifests loaded after {pc}')
    pc = PerfCounter(sec='', secs='')
    for p in Path(Config['plugins/plugins_path']).glob(Config['plugins/glob/early_load']):
        self.logger.infop(f'Executing early load on {p} (T+{pc})')
```
</details>

> <no doc>

## load_plugins()
```python
def load_plugins()
```

[`_rsruntime/lib/rs_plugins.py@183:185`](/_rsruntime/lib/rs_plugins.py#L183)

<details>
<summary>Source Code</summary>

```python
def load_plugins(self):
    bp = Path(Config['plugins/plugins_path'])
    self._traverse_plugins(sorted(set(bp.glob(Config['plugins/glob/basic'])) | set(bp.glob(Config['plugins/glob/standalone']))), PerfCounter(sec='', secs=''))
```
</details>

> <no doc>

## restart()
```python
def restart()
```

[`_rsruntime/lib/rs_plugins.py@214:215`](/_rsruntime/lib/rs_plugins.py#L214)

<details>
<summary>Source Code</summary>

```python
def restart(self):
    self._pmagic('restart', 'Restarting plugin {plug_name}')
```
</details>

> <no doc>

## start()
```python
def start()
```

[`_rsruntime/lib/rs_plugins.py@212:213`](/_rsruntime/lib/rs_plugins.py#L212)

<details>
<summary>Source Code</summary>

```python
def start(self):
    self._pmagic('start', 'Starting plugin {plug_name}')
```
</details>

> <no doc>