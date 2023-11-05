#!/bin/python3

#> Imports
import sys
import logging
from pathlib import Path
#</Imports

#> Logging
def setup_logger():
    log_path = (Path.cwd() / '_rslog'); log_path.mkdir(exist_ok=True)
    date_fmt_short = '%H:%M:%S'
    date_fmt_long = '%Y-%m-%d %H:%M:%S'
    log_fmt_short = '[$asctime] [$name/$threadName/$levelname] $message'
    log_fmt_long = '[$asctime] [$name/$processName:$threadName<$module.$funcName[$lineno]>/$levelname] $message'
    logging.basicConfig(
        filename=log_path / 'RunServer.log',
        level=logging.DEBUG if '--debug' in sys.argv[1:] \
            else logging.INFO if '--verbose' in sys.argv[1:] \
            else logging.WARNING,
        format=log_fmt_long,
        datefmt=date_fmt_long,
        style='$'
    )
    logger = logging.getLogger()
    stream_h = logging.StreamHandler()
    stream_h.setFormatter(logging.Formatter(
        log_fmt_long if '--verbose-log-headers' in sys.argv[1:] else log_fmt_short,
        date_fmt_long if '--verbose-log-headers' in sys.argv[1:] else date_fmt_short,
        style='$',
    ))
    logger.addHandler(stream_h)
#</Logging

#> Bootstrap >/
if __name__ == '__main__':
    setup_logger()
    if 1:#try:
        from _rsruntime.rs_BOOTSTRAP import Bootstrapper
        bs = Bootstrapper() # not the kind you're thinking of!!!
    #except Exception as e:
    #    ...
    bs.bootstrap()
