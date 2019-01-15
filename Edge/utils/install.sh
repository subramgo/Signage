#!/bin/bash
###########################################################
# Install and set up environment for edge-device Signage  #
#                                                         #
###########################################################

LOG=~/install.log

watching()
{
    local func=$1
    local desc=""
    if [ -n "$2" ]; then desc=$2; fi; 
    local log=$LOG
    if [ -n "$3" ]; then log=$3; fi; 

    $func >> $log 2>&1 &
    local pid=$!
    local delay=0.5
    local spinstr='|/-\'
    printf "$desc\n" | tee $LOG
    tput civis
    stty -echo
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf " [%c] " "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
        printf "\b\b\b\b\b"
    done
    wait $pid
    ret=$?
    printf "    \b\b\b"
    if [ $ret != 0 ] 
    then
        printf "\n  FAILED (exit code %s)\n" "$ret"
    else
        printf "\n"
    fi
    stty echo
    tput cnorm
}

echo `date` - Signage Install/Update Run: >> $LOG

###########################################################
####                  Configuration                    ####
###########################################################
func(){
  ### Resource Storage
  sudo mkdir -p /boot/signage
  sudo mkdir -p /opt/signage
  sudo chown -R `whoami`:`id -gn` /opt/signage
  sudo chmod -R 700 /opt/signage

  # ad videos
  mkdir -p /opt/signage/videos

  # ML models
  mkdir -p /opt/signage/models
}
watching func "Config and resource directories."

###########################################################
####                    Dependencies                   ####
###########################################################

apt_installed() {
    dpkg-query -f '${Package}\n' -W | grep "^$1\$" 2>/dev/null
}
echo "Installing OS utilities"
utils="screen git vim pv omxplayer cmake make python-opencv"
for p in $utils
do
    if [[ $(apt_installed $p) ]]
    then
        echo "  - $p already installed"
    else
        func() {
            sudo apt install -y $p
        }
        watching func "  - $p"
    fi
done

if ! hash pip3 2>/dev/null
then
    func() {
        sudo apt install python3-pip -y
    }
    watching func "installing pip3"
fi

echo "Installing ML Python packages"
# `pip list` can be slow so only check once
installed=$(pip3 list --format=columns 2>/dev/null)
pip_installed() {
    echo $installed | grep -i $1 2>/dev/null
}
pyml="requests pyyaml pillow passlib rpyc pexpect dlib"
for p in $pyml
do
    if [[ $(pip_installed $p) ]]
    then
        echo "  - $p already installed"
    else
        func() {
            pip3 install --verbose $p
        }
        watching func "  - $p"
    fi
done

echo "Installed dependent libraries."

