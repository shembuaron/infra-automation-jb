#!/bin/bash

if command -v dnf &>/dev/null; then
    echo "dnf"
elif command -v yum &>/dev/null; then
    echo "yum"
elif command -v apt &>/dev/null; then
    echo "apt"
elif command -v pacman &>/dev/null; then
    echo "pacman"
else
    echo "[ERROR] No supported package manager found (dnf/yum/apt/pacman). Exiting with error code 1 " >&2
    exit 1
fi
