#!/bin/bash

# check scripts/debian-init.d
# for 'daemon' version

export PYTHONPATH=`dirname $0`
twistd -n cyclone -p 8888 -l 0.0.0.0 \
       -r rondurev.web.Application -c rondurev.conf \
       --ssl-port=8443 --ssl-cert=server.crt --ssl-key=server.key \
       --ssl-listen=0.0.0.0 --ssl-appopts=rondurev.conf --ssl-app=rondurev.web.Application $*


