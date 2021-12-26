#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR=.

RED="31"
GREEN="32"
BOLDRED="\e[1;${RED}m"
BOLDGREEN="\e[1;${GREEN}m"
ENDCOLOR="\e[0m"

PY_FILES=$(find . -name "*.py" -not -path "*migrations*" | tr '\n' ' ')

# dictionary: checker -> flags
declare -A checkers=(
    ["shellcheck"]="find ${PROJECT_DIR} -name '*.sh' -type f -exec 'shellcheck' {} \;"
    ["isort"]="isort --check-only --diff ${PROJECT_DIR}"
    ["black"]="black ${PROJECT_DIR}"
    ["pylint"]="pylint ${PY_FILES}"
    ["prospector"]="prospector ${PROJECT_DIR}"
)

error=false
for checker in "${!checkers[@]}"; do
    command=${checkers[$checker]}
    echo -e "${BOLDGREEN}> running checker: ${checker}...${ENDCOLOR}"
    if eval "${command}"; then
        echo -e "\n${BOLDGREEN}OK. \"${checker}\" runned.\n${ENDCOLOR}"
    else
        echo -e "\n${BOLDRED}checker \"${checker}\" has failed.\n${ENDCOLOR}"
        error=true
    fi
done

if [[ "${error}" == "true" ]]; then
    echo -e "${BOLDRED}failed.${ENDCOLOR}"
    exit 1
fi
