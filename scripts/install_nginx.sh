#!/bin/bash
set -e

if [ "$1" = "pacman" ]; then
    sudo $1 -S --noconfirm nginx &>/dev/null
else
    sudo $1 install -y nginx
fi
