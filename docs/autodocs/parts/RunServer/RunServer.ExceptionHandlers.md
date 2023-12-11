# `ExceptionHandlers` (`RunServer.ExceptionHandlers` | `RS.EH`)
[`_rsruntime/lib/rs_exceptionhandlers.py`](/_rsruntime/lib/rs_exceptionhandlers.py "Source")  
[Standalone doc: parts/RunServer/RunServer.ExceptionHandlers.md](RunServer.ExceptionHandlers)  

## hookin()
```python
def hookin()
```

[`_rsruntime/lib/rs_exceptionhandlers.py@38:41`](/_rsruntime/lib/rs_exceptionhandlers.py#L38)

<details>
<summary>Source Code</summary>

```python
def hookin(self):
    self._hookin_hooktype(sys, 'excepthook')
    self._hookin_hooktype(sys, 'unraisablehook')
    self._hookin_hooktype(threading, 'excepthook')
```
</details>

> <no doc>

## hookout()
```python
def hookout()
```

[`_rsruntime/lib/rs_exceptionhandlers.py@46:49`](/_rsruntime/lib/rs_exceptionhandlers.py#L46)

<details>
<summary>Source Code</summary>

```python
def hookout(self):
    self._hookout_hooktype(sys, 'excepthook')
    self._hookout_hooktype(sys, 'unraisablehook')
    self._hookout_hooktype(threading, 'excepthook')
```
</details>

> <no doc>

## register_exception_hook(...)
```python
def register_exception_hook(callback: Callable(type[BaseException], typing.Any | None, traceback))
```

[`_rsruntime/lib/rs_exceptionhandlers.py@54:55`](/_rsruntime/lib/rs_exceptionhandlers.py#L54)

<details>
<summary>Source Code</summary>

```python
def register_exception_hook(self, callback: typing.Callable[[typing.Type[BaseException], typing.Any | None, types.TracebackType], None]):
    self.exceptionhooks.register(callback)
```
</details>

> <no doc>

## register_thread_exception_hook(...)
```python
def register_thread_exception_hook(callback: Callable(_ExceptHookArgs))
```

[`_rsruntime/lib/rs_exceptionhandlers.py@58:59`](/_rsruntime/lib/rs_exceptionhandlers.py#L58)

<details>
<summary>Source Code</summary>

```python
def register_thread_exception_hook(self, callback: typing.Callable[[threading.ExceptHookArgs], None]):
    self.threadexceptionhooks.register(callback)
```
</details>

> <no doc>

## register_unraisable_hook(...)
```python
def register_unraisable_hook(callback: Callable(ForwardRef('UnraisableHookArgs')))
```

[`_rsruntime/lib/rs_exceptionhandlers.py@56:57`](/_rsruntime/lib/rs_exceptionhandlers.py#L56)

<details>
<summary>Source Code</summary>

```python
def register_unraisable_hook(self, callback: typing.Callable[['UnraisableHookArgs'], None]):
    self.unraisablehook.register(callback)
```
</details>

> <no doc>