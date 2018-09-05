#!/bin/bash
###########################################################
# Install and set up environment for edge-device programs #
###########################################################

### Configuration
sudo mkdir -p /boot/signage
sudo chown -R `whoami`:`id -gn` /boot/signage
cp config.template.yml /boot/signage/config.yml

### Resource Storage
sudo mkdir -p /opt/signage
sudo chown -R `whoami`:`id -gn` /opt/signage

# ad videos
mkdir /opt/signage/videos

# ML models
mkdir /opt/signage/gender

# TODO Set up `/etc/network/interfaces` to allow access to necessary IP cameras.
# TODO the rest of the install shown in README.md