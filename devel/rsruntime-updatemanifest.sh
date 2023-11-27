#!/bin/bash

# Updates the manifest in ./_rsruntime/MANIFEST.ini
#  all arguments are supplied, even if they are simply the defaults, for documentation purposes

python3 ./devel/mkmanifest.py update ./_rsruntime/MANIFEST.ini ./_rsruntime/ \
    --hash-algorithm "sha1" --overwrite

python3 ./devel/mkmanifest.py sign ./_rsruntime/MANIFEST.ini ./key.pyk --overwrite