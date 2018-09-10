#!/bin/bash
###########################################################
# Install and set up environment for edge-device programs #
# Update in case of existing installations                #
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
    printf "$desc" | tee $LOG
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

echo `date` - Webservices Install/Update Run: >> $LOG

###########################################################
####                  Configuration                    ####
###########################################################
func(){
  ### Resource Storage
  sudo mkdir -p /opt/signage
  sudo chown -R `whoami`:`id -gn` /opt/signage
  sudo chmod -R 700 /opt/signage

  # credentials
  echo "copying credential template if not present"
  cp -n credentials.template.yml /opt/signage/web.yml
}
watching func "Config and resource directories."

###########################################################
####                    Dependencies                   ####
###########################################################

echo "Installing ML Python packages"
# `pip list` can be slow so only check once
installed=$(pip3 list --format=columns 2>/dev/null)
pip_installed() {
    echo $installed | grep -i $1 2>/dev/null
}
pyml=`cat Akshi/requirements.txt`
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

###########################################################
####                     Deployment                    ####
###########################################################
INSTALL_PATH=~/.local/bin/signage-web

mkdir -p $INSTALL_PATH      2>/dev/null
cp -r Akshi/* $INSTALL_PATH
printf "Installed signage-web to $INSTALL_PATH\n"

if [[ $(grep 'signage' /etc/rc.local) ]]
then
    echo "Signage already autostarting in \`rc.local\`."
else
  sudo tee -a /etc/rc.local >/dev/null << EOF
runuser -l pi -c 'printf "Starting signage web script.\n"  >> /home/pi/startup.log'
runuser -l pi -c "screen -dmS signage-web"
runuser -l pi -c "screen -S signage-web -p 0 -X stuff 'watch -n 1 $INSTALL_PATH/run.sh >> /home/pi/signage-web.log\n'"
runuser -l pi -c 'printf "Started signage services.\n" >> /home/pi/startup.log'
EOF

  sudo sed -i 's|exit 0||' /etc/rc.local
  printf "\nexit 0\n" | sudo tee -a /etc/rc.local >/dev/null

  echo "Signage autostarting in \`rc.local\`."
fi

