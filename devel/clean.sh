#!/bin/bash

# Cleans up byproducts of RunServer.py (using [CLEAN_CMD := "rm -riv"], such as:
#  ./__pycache__/ & **/__pycache__/  [CLEAN_PYCACHE != 0]
#  ./_rsconfig/                      [CLEAN_RSCONFIG != 0]
#  ./_rslog/                         [CLEAN_RSLOG != 0]
#  ./_rsusers/                       [CLEAN_RSUSERS != 0]

: ${CLEAN_CMD:="rm -rvI"}

if [[ "$CLEAN_PYCACHE" != 0 ]]; then
    [[ -f "./__pycache__/" ]] && echo "Cleaning ./__pycache__/" && $CLEAN_CMD ./__pycache__/
    (compgen -G "**/__pycache__/" > /dev/null) && echo "Cleaning **/__pycache__/" && $CLEAN_CMD **/__pycache__/
fi
[[ "$CLEAN_RSCONFIG" != 0 ]] && [[ -d "./_rsconfig/" ]] && echo "Cleaning ./_rsconfig/" && $CLEAN_CMD ./_rsconfig/
[[ "$CLEAN_RSLOG" != 0 ]] && [[ -d "./_rslog/" ]] && echo "Cleaning ./_rslog/" && $CLEAN_CMD ./_rslog/
[[ "$CLEAN_RSUSERS" != 0 ]] && [[ -d "./_rsusers/" ]] && echo "Cleaning ./_rsusers/" && $CLEAN_CMD ./_rsusers/