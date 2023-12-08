# `Bootstrapper` (`RunServer.Bootstrapper` | `RS.BS`)
[`_rsruntime/rs_BOOTSTRAP.py`](/_rsruntime/rs_BOOTSTRAP.py "Source")  
[Standalone doc: parts/RunServer/RunServer.Bootstrapper.md](RunServer.Bootstrapper.md)  
> Does the necessary startup and take-down for RunServer

## close(...)
```python
def close(do_exit: bool | int = False)
```

[`_rsruntime/rs_BOOTSTRAP.py@235:243`](/_rsruntime/rs_BOOTSTRAP.py#L235)

<details>
<summary>Source Code</summary>

```python
def close(self, do_exit: bool | int = False):
    '''Executes all shutdown callbacks and closes logging (logging.shutdown()), and exits with exit code do_exit if it isn't False'''
    if self.is_closed: return
    self.logger.irrec('Instructed to perform orderly shutdown, executing shutdown callbacks...')
    for h in self.shutdown_callbacks: h()
    self.logger.irrec(f'Closing logger{f" and exiting with code {do_exit}" if do_exit is not False else ""}, goodbye!')
    logging.shutdown()
    if do_exit is False: self.is_closed = True
    else: exit(do_exit)
```
</details>

> Executes all shutdown callbacks and closes logging (logging.shutdown()), and exits with exit code do_exit if it isn't False

## register_onclose(...)
```python
def register_onclose(cb: Callable)
```

[`_rsruntime/rs_BOOTSTRAP.py@244:246`](/_rsruntime/rs_BOOTSTRAP.py#L244)

<details>
<summary>Source Code</summary>

```python
def register_onclose(self, cb: typing.Callable[[], None]):
    '''Registers a function to run when self.close() is called'''
    self.shutdown_callbacks.add(cb)
```
</details>

> Registers a function to run when self.close() is called