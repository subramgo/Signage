# Signage Edge Processing


## Configuration
Configuration is located in `/boot/signage/config.yml`
A template is in `config.template.yml`

Sensitive credentials are masked from there and kept in `/opt/signage/credentials.yml` to be protected by OS login.

## Components

  * `ads.py` service to play video
    * depends on ad service platform
  * `camera.py` manages camera input
    * depends on edge device platform
  * `data.py` manages data upload to signage data server
  * `demographics.py.py` service determines gender and age of faces
    * Gender Model download from https://drive.google.com/open?id=1dLg4izlUYVTRkrGyTVv5OJ60awa69zwN
  * `faces.py` performs face detection
  * `signage.py` orchestration


# Edge Deployment

See `utils/install.sh`

#### Image Dependencies
  $ sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev install libatlas-base-dev gfortran

#### Important Data Processing Packages
  * numpy
  * opencv
  * tensorflow
  * keras
  * dlib

## Automation

We auto-start the services by creating screen sessions for each via commands added to `/etc/rc.local`.

