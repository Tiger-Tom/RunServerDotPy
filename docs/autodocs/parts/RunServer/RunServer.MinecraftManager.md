# `MinecraftManager` (`RunServer.MinecraftManager` | `RS.MC`)
[`_rsruntime/lib/rs_mcmgr.py`](/_rsruntime/lib/rs_mcmgr.py "Source")  
[Standalone doc: parts/RunServer/RunServer.MinecraftManager.md](RunServer.MinecraftManager)  

## auto_update(...)
```python
def auto_update(force: bool = False)
```

[`_rsruntime/lib/rs_mcmgr.py@142:154`](/_rsruntime/lib/rs_mcmgr.py#L142)

<details>
<summary>Source Code</summary>

```python
def auto_update(self, force: bool = False):
    '''Automatically update to the latest version'''
    if not force:
        if not Config['minecraft/manager/auto_update']:
            self.logger.warning('Skipping auto update (config minecraft/manager/auto_update)')
            return
        if self.jar_is_latest():
            self.logger.infop(f'No need to update: {self.latest["id"]} is the latest viable version')
            return
        if not (Config['minecraft/manager/unattended_autoupdate'] or input('Check and update server JAr to latest version? (y/N) >').lower().startswith('y')):
            self.logger.warning('Skipping auto update (user request)')
            return
    self.install_version(self.latest)
```
</details>

> Automatically update to the latest version

## fetch_versions()
```python
def fetch_versions() -> VersionsType
```

[`_rsruntime/lib/rs_mcmgr.py@75:96`](/_rsruntime/lib/rs_mcmgr.py#L75)
> Fetches the upstream versions manifest

## init2()
```python
def init2()
```

[`_rsruntime/lib/rs_mcmgr.py@40:59`](/_rsruntime/lib/rs_mcmgr.py#L40)
> <no doc>

## install_version(...)
```python
def install_version(ver: str | dict, chunk_notify: Callable(str) | None = None)
```

[`_rsruntime/lib/rs_mcmgr.py@105:123`](/_rsruntime/lib/rs_mcmgr.py#L105)
> (Verifies and) installs the specified version

## jar_is_latest()
```python
def jar_is_latest() -> bool
```

[`_rsruntime/lib/rs_mcmgr.py@72:73`](/_rsruntime/lib/rs_mcmgr.py#L72)

<details>
<summary>Source Code</summary>

```python
def jar_is_latest(self) -> bool:
    return self.jarvers() == self.latest['id']
```
</details>

> <no doc>

## jarvers()
```python
def jarvers() -> str | None
```

[`_rsruntime/lib/rs_mcmgr.py@64:67`](/_rsruntime/lib/rs_mcmgr.py#L64)

<details>
<summary>Source Code</summary>

```python
def jarvers(self) -> str | None:
    if not self.jarpath.exists(): return None
    with ZipFile(self.jarpath) as zf, zf.open('version.json') as f:
        return json.load(f)['id']
```
</details>

> <no doc>

## refresh()
```python
def refresh()
```

[`_rsruntime/lib/rs_mcmgr.py@97:100`](/_rsruntime/lib/rs_mcmgr.py#L97)

<details>
<summary>Source Code</summary>

```python
def refresh(self):
    '''Update internal versions manifest'''
    self.versions = self.fetch_versions()
    self.version_load_time = int(time.time())
```
</details>

> Update internal versions manifest

## upon_version(...)
```python
def upon_version(ver: str | dict)
```

[`_rsruntime/lib/rs_mcmgr.py@102:104`](/_rsruntime/lib/rs_mcmgr.py#L102)

<details>
<summary>Source Code</summary>

```python
def upon_version(self, ver: str | dict):
    '''Returns the upstream manifest for the specified version ID or dictionary'''
    return json.loads(fetch.fetch((ver if isinstance(ver, dict) else self.versions.versions[ver])['url']).decode())
```
</details>

> Returns the upstream manifest for the specified version ID or dictionary

## verify(...)
```python
def verify(data: bytes, target_hash: str, target_size: int)
```

[`_rsruntime/lib/rs_mcmgr.py@124:140`](/_rsruntime/lib/rs_mcmgr.py#L124)

<details>
<summary>Source Code</summary>

```python
def verify(self, data: bytes, target_hash: str, target_size: int):
    '''Checks the data against a variety of configurable verifications'''
    v = Config['minecraft/manager/download/verify']
    exc = []
    hash_failed = ('hash' in v) and (target_hash != sha1(data).hexdigest())
    size_failed = ('size' in v) and (diff := (target_size - len(data)))
    if 'zipf' in v:
        try:
            with ZipFile(BytesIO(data)) as zf:
                zipf_failed = zf.testzip() is not None
        except Exception as e:  zipf_failed = True
    else: zipf_failed = False
    failed = hash_failed + size_failed + zipf_failed
    failstr = ('hash' if hash_failed else '') + ('size' if size_failed else '') + ('ZipF' if zipf_failed else '')
    if failed: raise ValueError(f'{failstr[0].upper()}{failstr[1:4]}'
                                f'{f", {failstr[4:8]}, and {failstr[8:]}" if (failed == 3) \
                                    else f" and {failstr[4:]}" if failed == 2 else ""} verification failed')
```
</details>

> Checks the data against a variety of configurable verifications