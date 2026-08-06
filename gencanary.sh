#!/bin/bash
# Legacy shell wrapper forwarding to modern Python canary generator

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Ensure GPG TTY is exported for WSL / Linux pinentry passphrase prompts
export GPG_TTY=$(tty)

python3 "$SCRIPT_DIR/gencanary.py" "$@"
