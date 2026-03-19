#!/bin/bash
#test the safe installs, later comment out the assume-yes commands
set -e

if [ "$1" = "pacman" ]; then
    #sudo $1 -S --noconfirm nginx
    sudo $1 -S nginx
else
    #sudo $1 install -y nginx
    sudo $1 install nginx
fi
