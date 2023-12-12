#!/bin/python3

#> Imports
import re
from pathlib import Path
import RS
from RS.ShaeLib.net.pattern import link_search_pattern
#</Imports

#> Header >/
this.config.mass_set_default('auto_eula/',
    do_check=True,
    eula_path='./eula.txt',
    eula_true='eula=true',
    eula_false_patt='^eula=false$',
)
def check_eula():
    if not this.config['auto_eula/do_check']:
        this.logger.info('Not auto-checking EULA, config auto_eula/do_check is false')
        return
    eula_path = Path(RS.Config['minecraft/path/base'], this.config['auto_eula/eula_path'])
    if not eula_path.exists():
        this.logger.infop(f'Not auto-checking EULA, {eula_path} doesn\'t exist?')
        return
    fpatt = re.compile(this.config['auto_eula/eula_false_patt'], re.MULTILINE)
    eula = eula_path.read_text()
    if not fpatt.search(eula):
        this.logger.infop('Minecraft EULA appears to have been agreed to')
        return
    link = link_search_pattern.search(eula)
    if not input(f'"{eula.split("\n")[0]}"\nDo you agree to the Minecraft EULA{"" if link is None else f" at `{link.group(1)}`"}? (y/N) >').lower().startswith('y'):
        this.logger.warning('Minecraft EULA not agreed to by user request, trying to proceed anyway')
        this.logger.infop('If the EULA is mistakenly being read as not agreed to when it already has been, please file a bug report and set config auto_eula/do_check to False')
        return
    eula_path.write_text(fpatt.sub(this.config['auto_eula/eula_true'], eula))
