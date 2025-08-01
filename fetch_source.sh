#!/bin/bash

cd /home/admin/

set -e

if test -d SoraxRasperry; then
    echo "Git found"
    cd SoraxRasperry
    git pull
    echo "1" > /home/admin/update.txt
    else
    echo "Git not found"
    git clone https://github.com/Berkays/SoraxRasperry.git
fi
