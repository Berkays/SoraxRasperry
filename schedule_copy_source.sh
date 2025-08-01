#!/bin/bash

if test -d /home/admin/SoraxRasperry; then
    str=1
    echo "Git found"
    if [[ "$(< /home/admin/update.txt)" == "$str" ]]; then
        echo "New Update"
        cp /home/admin/runonce.sh /var/local/runonce.sh
        systemctl enable runonce.service
    else
        # Skip 
        echo "Already up to date"
    fi
fi
