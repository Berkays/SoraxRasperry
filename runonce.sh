#!/bin/bash

str=0
if [[ "$(< /home/admin/update.txt)" == "$str" ]]; then
    # No runonce update
    exit 0
fi

# Copy files 
if test -d /home/admin/SoraxRasperry; then
    echo "Writing new source files"
    cp /home/admin/SoraxRasperry/listener.py /home/admin/listener.py
    cp /home/admin/SoraxRasperry/modemConnect.py /home/admin/modemConnect.py
    cp /home/admin/SoraxRasperry/modemCycle.py /home/admin/modemCycle.py
    cp /home/admin/SoraxRasperry/boot_sim_configure.py /home/admin/boot_sim_configure.py
    cp /home/admin/SoraxRasperry/fonks.py /home/admin/fonks.py

    cp /home/admin/SoraxRasperry/create_log.sh /home/admin/create_log.sh
    cp /home/admin/SoraxRasperry/upload_log.sh /home/admin/upload_log.sh
    cp /home/admin/SoraxRasperry/fetch_source.sh /home/admin/fetch_source.sh
    cp /home/admin/SoraxRasperry/runonce.sh /home/admin/runonce.sh
fi

echo "0" > /home/admin/update.txt