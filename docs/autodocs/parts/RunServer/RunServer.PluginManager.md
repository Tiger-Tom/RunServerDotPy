# `PluginManager` (`RunServer.PluginManager` | `RS.PM`)
[`_rsruntime/lib/rs_plugins.py`](/_rsruntime/lib/rs_plugins.py "Source")  
[Standalone doc: parts/RunServer/RunServer.PluginManager.md](RunServer.PluginManager.md)  

## early_load_plugins()
```python
def early_load_plugins()
```

[`_rsruntime/lib/rs_plugins.py@172:180`](/_rsruntime/lib/rs_plugins.py#L172)

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

[`_rsruntime/lib/rs_plugins.py@182:184`](/_rsruntime/lib/rs_plugins.py#L182)

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

[`_rsruntime/lib/rs_plugins.py@213:214`](/_rsruntime/lib/rs_plugins.py#L213)

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

[`_rsruntime/lib/rs_plugins.py@211:212`](/_rsruntime/lib/rs_plugins.py#L211)

<details>
<summary>Source Code</summary>

```python
def start(self):
    self._pmagic('start', 'Starting plugin {plug_name}')
```
</details>

> <no doc>