# Signage Edge Processing


## Configuration
Configuration is located in `/boot/signage/config.yml`
A template is in `config.template.yml`

Sensitive credentials are in `/opt/signage/credentials.yml`
A template is in `credentials.template.yml`

## Components

  * `signage.py`
    * reads from IP Cam 
    * performs face detection
    * orchestrates data flow
  * `gender.py` service to determine the gender
    * Gender Model download from https://drive.google.com/open?id=1dLg4izlUYVTRkrGyTVv5OJ60awa69zwN
    *  `gender/4_try.h5` and `gender/4_try.json`
  * `player.py` service to play video
    * Videos to be stored in `/opt/signage/videos`


# Edge Deployment.

## Dependencies

  * Raspbian Stretch 9.4
    * `lsb_release -a` to check
  * Python 3+

#### Developer tools
  $ sudo apt-get install build-essential git cmake pkg-config screen vim

#### Image
  $ sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk2.0-dev install libatlas-base-dev gfortran

#### Important Data Processing Packages
  * numpy
  * opencv
  * tensorflow
  * keras
  * dlib

#### Models
Download the model files from google drive https://drive.google.com/open?id=1dLg4izlUYVTRkrGyTVv5OJ60awa69zwN
  * from gender folder in google drive, copy the models to  `/opt/signage/gender/`

#### Ad Media
  `mkdir /opt/signage/videos`
  * move the videos to this folder

#### Everything else

    install.sh

## Automation

We auto-start the services by creating screen sessions for each via commands added to `/etc/rc.local`.

