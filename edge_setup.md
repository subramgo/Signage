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
Download the model files from google drive https://drive.google.com/open?id=1dLg4izlUYVTRkrGyTVv5OJ60awa69zwN
	* from gender folder in google drive, copy the models to  /opt/signage/gender/bin/




