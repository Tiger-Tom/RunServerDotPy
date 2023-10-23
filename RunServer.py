#!/bin/python3

#> Imports
import sys
import logging
from pathlib import Path
#</Imports

#> Logging
def setup_logger():
    log_path = (Path.cwd() / '_rslog'); log_path.mkdir(exist_ok=True)
    log_fmt = '[%(asctime)s] [%(name)s<%(funcName)s>:%(levelname)s] %(message)s'
    logging.basicConfig(
        filename=log_path / 'RunServer.log',
        level=logging.DEBUG if '--debug' in sys.argv[1:] \
            else logging.INFO if '--verbose' in sys.argv[1:] \
            else logging.WARNING,
        format=log_fmt,
    )
    logger = logging.getLogger()
    stream_h = logging.StreamHandler()
    stream_h.setFormatter(logging.Formatter(log_fmt))
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
