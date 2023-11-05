#!/bin/python3

#> Imports
import sys
import logging
from pathlib import Path
#</Imports

#> Logging
def setup_logger():
    log_path = (Path.cwd() / '_rslog'); log_path.mkdir(exist_ok=True)
    # Formats
    log_fmt_short = '[$asctime] [$name/$threadName/$levelname] $message'
    log_fmt_long = '[$asctime] [$name/$processName:$threadName<$module.$funcName[$lineno]>/$levelname] $message'
    ## Date
    date_fmt_short = '%H:%M:%S'
    date_fmt_long = '%Y-%m-%d %H:%M:%S'
    # Configure logger
    logging.basicConfig(
        filename=log_path / 'RunServer.log',
        level=logging.DEBUG if '--debug' in sys.argv[1:] \
            else logging.INFO if '--verbose' in sys.argv[1:] \
            else logging.WARNING,
        format=log_fmt_long,
        datefmt=date_fmt_long,
        style='$',
    )
    ## Set loglevel names
    logging.addLevelName(logging.DEBUG, 'DBG')
    logging.addLevelName(logging.INFO, 'INF')
    logging.addLevelName(logging.WARNING, 'WRN')
    logging.addLevelName(logging.ERROR, 'ERR')
    logging.addLevelName(logging.CRITICAL, 'CRT')
    # Create logger
    logger = logging.getLogger()
    # Stream handler
    stream_h = logging.StreamHandler()
    logger.addHandler(stream_h)
    ## Format stream handler
    stream_h.setFormatter(logging.Formatter(
        log_fmt_long if '--verbose-log-headers' in sys.argv[1:] else log_fmt_short,
        date_fmt_long if '--verbose-log-headers' in sys.argv[1:] else date_fmt_short,
        style='$',
    ))
    
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
