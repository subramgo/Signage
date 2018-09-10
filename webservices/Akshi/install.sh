#!/bin/bash
###########################################################
####                  Configuration                    ####
###########################################################
mkdir -p /opt/signage
chown -R `whoami`:`id -gn` /opt/signage
chmod -R 700 /opt/signage
echo "copying credential template if not present"
cp -n credentials.template.yml /opt/signage/web.yml
