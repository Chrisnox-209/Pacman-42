#!/bin/bash
set -e

RED='\033[0;31m'
GREEN='\033[1;32m'
RST='\033[0m'

echo -e "\n${RED}=== installing PyInstaller ... ===${RST}\n"
uv sync
uv pip install --python .venv/bin/python "pyinstaller==6.22.3"

echo -e "\n${RED}=== building the executable ... ===${RST}\n"
.venv/bin/pyinstaller \
    --noconfirm \
    --clean \
    --onedir \
    --name Pacman-42 \
    --paths . \
    --add-data "assets:assets" \
    src/__main__.py

echo -e "\n${GREEN}╭───────────────────────────────────────────────────╮"
echo -e "│   ✔ Pacman-42 has been successfully compiled !    │"
echo -e "╰───────────────────────────────────────────────────╯${RST}\n"
