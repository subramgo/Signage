#!/bin/bash
###########################################################
# Install and set up environment for edge-device programs #
###########################################################

watching()
{
    local func=$1
    local desc=""
    if [ -n "$2" ]; then desc=$2; fi; 
    local log=~/install.log
    if [ -n "$3" ]; then log=$3; fi; 

    $func >> $log 2>&1 &
    local pid=$!
    local delay=0.5
    local spinstr='|/-\'
    printf "$desc" 
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

###########################################################
####                  Configuration                    ####
###########################################################
func(){
  sudo mkdir -p /boot/signage
  sudo cp -n config.template.yml /boot/signage/config.yml

  ### Resource Storage
  sudo mkdir -p /opt/signage
  sudo chown -R `whoami`:`id -gn` /opt/signage

  # ad videos
  mkdir -p /opt/signage/videos

  # ML models
  mkdir -p /opt/signage/gender
}
watching func "Creating config directories."

###########################################################
####                    Dependencies                   ####
###########################################################

apt_installed() {
    dpkg-query -f '${Package}\n' -W | grep "^$1\$" 2>/dev/null
}
echo "Installing OS utilities"
utils="screen git vim pv omxplayer"
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
pyml="requests pyyaml pillow passlib rpyc pexpect"
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

###########################################################
####                     Deployment                    ####
###########################################################
INSTALL_PATH=~/.local/bin/signage

mkdir -p $INSTALL_PATH      2>/dev/null
cp ./*.py $INSTALL_PATH
printf "Installed signage to $INSTALL_PATH\n"

if [[ $(grep 'signage' /etc/rc.local) ]]
then
    echo "Signage already autostarting in \`rc.local\`."
else
  sudo tee -a /etc/rc.local >/dev/null << EOF
runuser -l pi -c 'printf "Starting signage script.\n"  >> /home/pi/startup.log'
runuser -l pi -c "screen -dmS gender"
runuser -l pi -c "screen -S gender -p 0 -X stuff 'watch -n 1 python3 $INSTALL_PATH/gender.py >> /home/pi/startup.log\n'"
sleep 10
runuser -l pi -c "screen -dmS adserver"
runuser -l pi -c "screen -S adserver -p 0 -X stuff 'watch -n 1 python3 $INSTALL_PATH/player.py >> /home/pi/startup.log\n'"

runuser -l pi -c "screen -dmS signage"
runuser -l pi -c "screen -S signage -p 0 -X stuff 'watch -n 1 python3 $INSTALL_PATH/signage.py >> /home/pi/startup.log\n'"
runuser -l pi -c 'printf "Started signage services.\n" >> /home/pi/startup.log'
EOF

  sudo sed -i 's|exit 0||' /etc/rc.local
  printf "\nexit 0\n" | sudo tee -a /etc/rc.local >/dev/null

  echo "Signage autostarting in \`rc.local\`."
fi

###########################################################
####                      Security                     ####
###########################################################

# TODO disable SSH on the Pi


