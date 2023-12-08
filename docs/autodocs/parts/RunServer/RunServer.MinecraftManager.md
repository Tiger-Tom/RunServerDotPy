# `MinecraftManager` (`RunServer.MinecraftManager` | `RS.MC`)
[`_rsruntime/lib/rs_mcmgr.py`](/_rsruntime/lib/rs_mcmgr.py "Source")  
[Standalone doc: parts/RunServer/RunServer.MinecraftManager.md](RunServer.MinecraftManager.md)  

## init2()
```python
def init2()
```

[`_rsruntime/lib/rs_mcmgr.py@34:50`](/_rsruntime/lib/rs_mcmgr.py#L34)

<details>
<summary>Source Code</summary>

```python
def init2(self):
    if Config['minecraft/manager/dl/auto_fetch_if_missing'] or Config['minecraft/manager/dl/auto_update']:
        try: self.versions = self.setup_manifest()
        except Exception as e:
            self.logger.fatal(f'Could not setup Minecraft version manifest:\n{"".join(traceback.format_exception(e))}')
            self.has_manifest = False
        else: self.has_manifest = True
    if not (p := Path(Config['minecraft/path/base'], Config['minecraft/path/server_jar'])).exists():
        self.logger.warning(f'{p} does not exist!')
        if not self.has_manifest:
            self.logger.irrec('Minecraft version manifest failed earlier; cannot continue')
            raise FileNotFoundError(str(p))
        if not Config['minecraft/manager/dl/auto_fetch_if_missing']:
            self.logger.irrec('Config minecraft/manager/dl/auto_fetch_if_missing is false, cannot download!')
            raise FileNotFoundError(str(p))
        if not self.install_update():
            raise ExceptionGroup('The server JAr couldn\'t be found, and the downloaded version failed verification. Cannot possibly continue', (FileNotFoundError(p), ValueError('Verification failed')))
```
</details>

> <no doc>

## install_update()
```python
def install_update() -> bool
```

[`_rsruntime/lib/rs_mcmgr.py@76:95`](/_rsruntime/lib/rs_mcmgr.py#L76)
> <no doc>

## setup_manifest()
```python
def setup_manifest() -> VersionsType
```

[`_rsruntime/lib/rs_mcmgr.py@52:65`](/_rsruntime/lib/rs_mcmgr.py#L52)

<details>
<summary>Source Code</summary>

```python
def setup_manifest(self) -> 'VersionsType':
    self.logger.info(f'Fetching {Config["minecraft/manager/dl/version_manifest_url"]}')
    data = json.loads(fetch.fetch(Config['minecraft/manager/dl/version_manifest_url']).decode())
    tfmt = Config['minecraft/manager/dl/time_fmt']
    versions = {v['id']: v | {
            'time': strptime(v['time'], tfmt), '_time': v['time'],
            'releaseTime': strptime(v['releaseTime'], tfmt), '_releaseTime': v['releaseTime']
        } for v in data['versions']}
    return self.VersionsType(versions=versions,
        latest=max((versions[data['latest']['release']], versions[data['latest']['snapshot']]), key=lambda v: v['time']),
        latest_release=versions[data['latest']['release']],
        latest_snapshot=versions[data['latest']['snapshot']],
        releases = {k: v for k,v in versions.items() if v['type'] == 'release'},
        snapshots = {k: v for k,v in versions.items() if v['type'] == 'snapshot'},
    )
```
</details>

> <no doc>

## verify_update(...)
```python
def verify_update(data: bytes, target_hash: str, target_size: int) -> bool
```

[`_rsruntime/lib/rs_mcmgr.py@96:112`](/_rsruntime/lib/rs_mcmgr.py#L96)

<details>
<summary>Source Code</summary>

```python
def verify_update(self, data: bytes, target_hash: str, target_size: int) -> bool:
    failed_hash, failed_size = False, False
    if Config['minecraft/manager/dl/hash_verify'] and (target_hash != (actual_hash := sha1(data).hexdigest())):
        self.logger.fatal(f'The Minecraft server JAr failed hash verification:\n{target_hash=}\n{actual_hash=}')
        failed_hash = True
    if Config['minecraft/manager/dl/size_verify'] and (target_size != (actual_size := len(data))):
        self.logger.fatal(f'The Minecraft server JAr failed size verification:\n{target_size=}\n{actual_size=}')
        failed_size = True
    if failed_hash or failed_size:
        if (not Config['minecraft/manager/dl/prompt_on_fail_verify']) or \
           (input(f'The Minecraft server JAr failed '
                  f'{"hash" if failed_hash else ""}{" and " if (failed_hash and failed_size) else ""}{"size" if failed_size else ""} '
                  f'verification. Install it anyway? (y/N) >').lower() != 'y'):
            self.logger.error('Not installing')
            return False
        self.logger.warning('Installing anyway, proceed with caution')
    return True
```
</details>

> <no doc>