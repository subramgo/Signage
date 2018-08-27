# Signage Edge Processing

## Deployment

  * `Folder /home/pi/Signage/Edge/`
  * `Gender.py` service to determine the gender
  * `Player.py` service to play video
  * `client.py` is the configurable python client.
  * `singlerun.sh` runs the client with set configuration.

  * [optional]
  * `Folder /home/pi/Signage/webservice/Akshi/`
  *  Flask web service.
  *  ./run.sh to start the web service. 


  * Videos to be stored in `/opt/signage/videos`
  * Gender Model download from https://drive.google.com/open?id=1dLg4izlUYVTRkrGyTVv5OJ60awa69zwN
  *  `gender/4_try.h5` and `gender/4_try.json`

### Configuration
Configuration is located in `Signage/singlerun.sh`:

    python3 /home/pi/Signage/Edge/client.py -g True  -c 0 -w http://127.0.0.1:5000/api/v1/signage/signage_upload  -l signage-analysis-demo -i signage-camera-1


  * -c rtsp address for IP camera. 0 if USB camera is used
  * -w address for application server
  * -g to include gender detection
  * -l name for the location
  * -i name for the camera

Set up `/etc/network/interfaces` to allow access to necessary IP cameras.

### Automation
 
Add this to `/etc/rc.local`:

    printf "Starting signage script.\n" >> /home/pi/startup.log
    runuser -l pi -c "screen -dmS gender"
    runuser -l pi -c "screen -S gender -p 0 -X stuff 'watch -n 1 python3 /home/pi/Signage/Edge/Gender.py\n'"
    runuser -l pi -c "screen -dmS video"
    runuser -l pi -c "screen -S video -p 0 -X stuff 'watch -n 1 python3 /home/pi/Signage/Edge/Player.py\n'"
    runuser -l pi -c "screen -dmS webservice"
    runuser -l pi -c "screen -S webservice -p 0 -X stuff 'watch -n 1 /home/pi/Signage/webservice/Akshi/run.sh\n"
    runuser -l pi -c "screen -dmS signage"
    runuser -l pi -c "screen -S signage -p 0 -X stuff 'watch -n 1 /home/pi/Signage/singlerun.sh\n'"
    printf "started signage screen session" >> /home/pi/startup.log
 
  * `singlerun.sh` is our main script
  * `watch` re-runs the script when it see the script complete.
  * `/etc/rc.local` creates a screen session for `watch` on system startup.




# Setting up the edge device for signage app.
## Operating System

  lsb_release -a
  Raspbian Strech 9.4

## Python Version

  3.5.3

  $ sudo apt-get install python3-dev python3-pip
  $ sudo pip3 install numpy
  $ sudo ln -sf /usr/bin/python3 /usr/bin/python

## opencv installation

### Dependencies

#### Developer tools
  $ sudo apt-get install build-essential git cmake pkg-config
  $ sudo apt-get install screen
#### Image
  $ sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
#### Video
  $ sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
  $ sudo apt-get install libxvidcore-dev libx264-dev

#### GUI
  $ sudo apt-get install libgtk2.0-dev
#### Math
  $ sudo apt-get install libatlas-base-dev gfortran
#### Get opencv
  $ wget -O opencv-3.3.0.tgz https://github.com/opencv/opencv/archive/3.3.0.tar.gz
  $ tar -xvzf opencv-3.3.0.tgz
  $ wget -O opencv_contrib-3.3.0.tgz https://github.com/opencv/opencv_contrib/archive/3.3.0.tar.gz
  $ tar -xvzf opencv_contrib-3.3.0.tgz

#### Prepare build
  $ cd ~/opencv-3.0.0/
  $ mkdir build
  $ cd build
  $ cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_C_EXAMPLES=ON \
    -D INSTALL_PYTHON_EXAMPLES=ON \
    -D OPENCV_EXTRA_MODULES_PATH=~/src/opencv_contrib-3.3.0/modules \
    -D BUILD_EXAMPLES=ON ..
#### Run Build
  $ screen -S opencv-build
  $ make 2>&1 | tee buildLog.out
#### Install
  $ sudo make install
  $ sudo ldconfig

## tensorflow
  sudo pip3 install tensorflow
  sudo pip3 install keras
  sudo pip3 install dlib
  sudo pip3 install requests
  sudo pip3 install pillow


## Signage Setup

create a folder 'signage' in /opt

  sudo mkdir /opt/signage
  chown pi:root /opt/signage

  mkdir /opt/signage/gender

Download the model files from google drive https://drive.google.com/open?id=1dLg4izlUYVTRkrGyTVv5OJ60awa69zwN
  * from gender folder in google drive, copy the models to  /opt/signage/gender/
  mkdir /opt/signage/videos
  * move the videos to this folder

## pexpect
  pip3 install pexpect