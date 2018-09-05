
# Old command:
#python3 ./client.py -w http://178.128.68.231:5000/api/v1/signage/signage_upload -c rtsp://root:pass@192.168.1.168/usecondstream -l signage-demo-location -i signage-demo-camera

# Load Gender Service
FILE_TO_WATCH=/home/pi/Signage/Edge/gender.log
SEARCH_PATTERN='Gender Model Loaded'
rm -rf ${FILE_TO_WATCH}
nohup python3 -u /home/pi/Signage/Edge/Gender.py 1> ${FILE_TO_WATCH}  2>/dev/null &
sleep 25
echo "Gender Loaded"

FILE_TO_WATCH=/home/pi/Signage/Edge/player.log
SEARCH_PATTERN='Video Loaded'
rm -rf rm -rf ${FILE_TO_WATCH}
nohup python3 -u /home/pi/Signage/Edge/Player.py 1> ${FILE_TO_WATCH} 2>/dev/null &
sleep 5
echo "Player loaded"

FILE_TO_WATCH=/home/pi/Signage/webservices/Akshi/ws.log
SEARCH_PATTERN='0.0.0.0'
rm -rf ${FILE_TO_WATCH}
nohup sh /home/pi/Signage/webservices/Akshi/run.sh 1> ${FILE_TO_WATCH} 2>/dev/null &
sleep 5
echo "Web service loaded"


CAM_URI=rtsp://root:pass@192.168.1.168/usecondstream
python3 /home/pi/Signage/Edge/client.py -g True  -c $CAM_URI -w http://michael:irkbin@127.0.0.1:5000/api/v1/signage/signage_upload  -l signage-analysis-demo -i signage-camera-1

