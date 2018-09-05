
# Load Gender Service
FILE_TO_WATCH=/home/pi/Signage/Edge/gender.log
SEARCH_PATTERN='Gender Model Loaded'
rm -rf ${FILE_TO_WATCH}
nohup python3 -u /home/pi/Signage/Edge/gender.py 1> ${FILE_TO_WATCH}  2>/dev/null &
sleep 25
echo "Gender Loaded"

FILE_TO_WATCH=/home/pi/Signage/Edge/player.log
SEARCH_PATTERN='Video Loaded'
rm -rf rm -rf ${FILE_TO_WATCH}
nohup python3 -u /home/pi/Signage/Edge/player.py 1> ${FILE_TO_WATCH} 2>/dev/null &
sleep 5
echo "Player loaded"

FILE_TO_WATCH=/home/pi/Signage/webservices/Akshi/ws.log
SEARCH_PATTERN='0.0.0.0'
rm -rf ${FILE_TO_WATCH}
nohup sh /home/pi/Signage/webservices/Akshi/run.sh 1> ${FILE_TO_WATCH} 2>/dev/null &
sleep 5
echo "Web service loaded"

python3 /home/pi/Signage/Edge/signage.py

