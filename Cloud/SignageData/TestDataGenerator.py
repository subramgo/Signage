import requests as _requests
import json
import pandas as pd 
import numpy as np
from random import randrange


cfg_defaults = { 
      'camera'                : {
          'enabled'           : False
        , 'stream_address'    : '192.168.1.168/usecondstream'
        , 'protocol'          : 'rtsp://'
        , 'location_name'     : 'boca-mac-1'
        , 'name'              : 'boca-mac-1'
        , 'credentials'       : '*user*:*pass*'
    }
    
    , 'data'                  : {
          'enabled'           : False
        , 'credentials'       : 'united:irkbin'
        , 'data_server'       : 'signagedata.azurewebsites.net'
        , 'data_protocol'     : 'https://'
    }


    }

protocol=cfg_defaults['data']['data_protocol']

uri=cfg_defaults['data']['data_server']
cred=cfg_defaults['data']['credentials']
headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}
post_path = '/api/v2/signage/person/upload'





genders = ['male','female']
ages    =['teen','adult','senior']





def get_random_record():

	random_indx = randrange(len(genders))

	gender = genders[random_indx]
	age   = ages[random_indx]

	engagement_range = np.random.normal(3, 2,1)[0]
	time_alive = np.random.normal(2.0,1,1)[0]
	if time_alive < 0:
		time_alive = 0.5
	face_id = np.random.randint(1,1000,1)[0]



	camera_id=cfg_defaults['camera']['name']
	location=cfg_defaults['camera']['location_name']

	data = {
	        'camera_id' : camera_id
	       ,'gender'  : gender
	       ,'age': age
	       ,'time_alive'   : str(time_alive)
           ,'engagement_range' : str(engagement_range)
	       ,'location'  : location
	       ,'face_id' : str(face_id)
	        }

	return data


def push_test_data():

	post_data = get_random_record()


	r = _requests.post(protocol+cred+"@"+uri+post_path,json=post_data,headers=headers)
	if r.status_code == 200:
		print('Done uploading data...\n')
		return 0
	else:
		print('Cannot upload data!!!')
		return -1


def test_update_data():
	post_data = get_random_record()
	post_data['face_id'] = str(809)
	post_data['time_alive'] = str(1.5)

	r = _requests.post(protocol+cred+"@"+uri+post_path,json=post_data,headers=headers)
	if r.status_code == 200:
		print('Done updating data...\n')
		return 0
	else:
		print('Cannot update data!!!')
		return -1



def main():
	for i in range(17):
		r = push_test_data()
		if r == -1:
			break



if __name__ == '__main__':
	main()
	#test_update_data()

