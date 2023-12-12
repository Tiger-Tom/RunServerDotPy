# `MCLang` (`RunServer.MCLang` | `RS.L`)
[`_rsruntime/lib/rs_lineparser.py`](/_rsruntime/lib/rs_lineparser.py "Source")  
[Standalone doc: parts/RunServer/RunServer.MCLang.md](RunServer.MCLang)  

## extract_lang()
```python
def extract_lang() -> dict[str, str]
```

[`_rsruntime/lib/rs_lineparser.py@79:98`](/_rsruntime/lib/rs_lineparser.py#L79)
> Extracts the language file from a server JAR file, sets and returns self.lang

## init2()
```python
def init2()
```

[`_rsruntime/lib/rs_lineparser.py@31:32`](/_rsruntime/lib/rs_lineparser.py#L31)

<details>
<summary>Source Code</summary>

```python
def init2(self):
    self.extract_lang()
```
</details>

> <no doc>

## lang_to_pattern(...)
```python
def lang_to_pattern(lang: str, group_names: tuple[str, ...] | None = None, prefix_suffix: str = '^{}$') -> Pattern
```

[`_rsruntime/lib/rs_lineparser.py@43:77`](/_rsruntime/lib/rs_lineparser.py#L43)
> <no doc>

## strip_prefix(...)
```python
def strip_prefix(line: str) -> tuple[tuple[re.Match, time.struct_time] | None, str]
```

[`_rsruntime/lib/rs_lineparser.py@36:41`](/_rsruntime/lib/rs_lineparser.py#L36)

<details>
<summary>Source Code</summary>

```python
def strip_prefix(self, line: str) -> tuple[tuple[re.Match, time.struct_time] | None, str]:
    line = line.strip()
    if (m := self.prefix.fullmatch(line)) is not None:
        # almost as bad as my first idea: `time.strptime(f'{m.time}|{time.strftime("%x")}', '%H:%M:%S|%x')`
        return ((m, time.struct_time(time.localtime()[:3] + time.strptime(m.group('time'), '%H:%M:%S')[3:6] + time.localtime()[6:])), m.group('line'))
    return (None, line)
```
</details>

> <no doc>