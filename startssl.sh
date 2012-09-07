#!/bin/bash

# check scripts/debian-init.d
# for 'daemon' version

export PYTHONPATH=`dirname $0`
twistd -n cyclone -p 8888 -l 0.0.0.0 \
       -r cyclone2.web.Application -c cyclone2.conf \
       --ssl-port=8443 --ssl-cert=server.crt --ssl-key=server.key \
       --ssl-listen=0.0.0.0 --ssl-appopts=cyclone2.conf --ssl-app=cyclone2.web.Application $*


