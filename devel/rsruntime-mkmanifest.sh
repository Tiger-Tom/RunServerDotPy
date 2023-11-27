#!/bin/bash

# Generates a manifest for _rsruntime
#  all arguments are supplied, even if they are simply the defaults, for documentation purposes

python3 ./devel/mkmanifest.py make ./_rsruntime/ \
    --output ./_rsruntime/MANIFEST.ini \
    "RunServer Runtime Files" \
    "http://0.0.0.0:8000/MANIFEST.ini" \
    "http://0.0.0.0:8000/content/" \
    --creator "Shae VanCleave" \
    --creator-username "shae" \
    --description "The actual code of RunServer" \
    --key ./key.pyk \
    --hash-algorithm "sha1" \
    --system-info-level "full"