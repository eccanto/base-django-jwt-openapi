#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR=.

RED="31"
GREEN="32"
BOLDRED="\e[1;${RED}m"
BOLDGREEN="\e[1;${GREEN}m"
ENDCOLOR="\e[0m"

# dictionary: checker -> flags
declare -A checkers=(
    ["pylint"]=""
    ["prospector"]=""
    ["black"]=""
    ["isort"]="--check-only --diff"
)

error=false
for checker in "${!checkers[@]}"; do
    flags=${checkers[$checker]}
    echo -e "${BOLDGREEN}> running checker: ${checker} ${flags}${ENDCOLOR}"

    ${checker} ${flags} ${PROJECT_DIR} && echo -e "${BOLDGREEN}OK. "${checker}" runned.\n${ENDCOLOR}"
    if [[ $? -ne 0 ]]; then
        echo -e "${BOLDRED}checker \"${checker}\" has failed.\n${ENDCOLOR}"
        error=true
    fi
done

if [[ "${error}" == "true" ]]; then
    echo -e "${BOLDRED}failed.${ENDCOLOR}"
    exit 1
fi
