#!/bin/bash
###########################################################
# Install edge-device Signage                             #
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

echo `date` - Signage Deploy Run: >> $LOG


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
runuser -l pi -c 'printf "%s Starting signage scripts.\n" "$(date)"  >> /home/pi/startup.log'
runuser -l pi -c "screen -dmS demographics"
runuser -l pi -c "screen -S demographics -p 0 -X stuff 'watch -n 1 python3 $INSTALL_PATH/demographics.py 2>&1\n'"
sleep 10
runuser -l pi -c "screen -dmS adserver"
runuser -l pi -c "screen -S adserver -p 0 -X stuff 'watch -n 1 python3 $INSTALL_PATH/player.py 2>&1\n'"

runuser -l pi -c "screen -dmS signage"
runuser -l pi -c "screen -S signage -p 0 -X stuff 'watch -n 1 python3 $INSTALL_PATH/signage.py 2>&1\n'"
EOF

  sudo sed -i 's|exit 0||' /etc/rc.local
  printf "\nexit 0\n" | sudo tee -a /etc/rc.local >/dev/null

  echo "Signage autostarting in \`rc.local\`."
fi


