import requests as _requests
import json
import pandas as pd 
import numpy as np

cfg_defaults = { 
      'camera'                : {
          'enabled'           : False
        , 'stream_address'    : '192.168.1.168/usecondstream'
        , 'protocol'          : 'rtsp://'
        , 'location_name'     : 'datagenerator-2'
        , 'name'              : 'datagenerator-2'
        , 'credentials'       : '*user*:*pass*'
    }
    
    , 'data'                  : {
          'enabled'           : False
        , 'credentials'       : 'united:irkbin'
        , 'data_server'       : '0.0.0.0:5000'
        , 'data_protocol'     : 'http://'
    }


    }

protocol=cfg_defaults['data']['data_protocol']
uri=cfg_defaults['data']['data_server']
cred=cfg_defaults['data']['credentials']
headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}
face_path = '/api/v2/signage/faces'
gender_path = '/api/v2/signage/demographics'



test_windows = []
test_windows.append([291,192,513,415])
test_windows.append([381,206,417,242])
test_windows.append([269,206,305,242])

genders = ['male','female']
ages    =['(25,32)','(35,45)','(5,15)']



def get_random_face():
	no_faces = np.random.randint(low = 1, high = 3)
	windows  = []
	for i in range(no_faces):
		windows.append(test_windows[i])

	camera_id=cfg_defaults['camera']['name']
	location=cfg_defaults['camera']['location_name']

	data = {
	        'camera_id' : camera_id
	       ,'no_faces'  : str(len(windows))
	       ,'windows'   : ",".join(str(r) for v in windows for r in v)
	       ,'location'  : location
	        }

	return data, no_faces

def get_random_gender(no_faces):
	genders_  = []
	ages_    = []
	male_count = 0
	female_count = 0
	for i in range(no_faces):
		g = genders[np.random.randint(low=0,high=1)]
		if g == 'male':
			male_count+=1
		else:
			female_count+=1
		genders_.append(g)
		ages_.append(ages[np.random.randint(low=0, high=len(ages))])

	camera_id=cfg_defaults['camera']['name']
	location=cfg_defaults['camera']['location_name']
	path = '/api/v2/signage/faces'

	data = {
	        'camera_id' : camera_id
	       ,'male_count'  : str(male_count)
	       ,'female_count': str(female_count)
	       ,'gender_list'   : ",".join(str(v) for v in genders_)
           ,'age_list' : ','.join(str( g[1] ) for g in genders)


	       ,'age_list'   : ",".join(str(v) for v in ages_)
	       ,'location'  : location
	        }

	return data


def push_test_data():

	data_face, no_faces = get_random_face()
	data_gender = get_random_gender(no_faces)
	print(data_gender)

	r = _requests.post(protocol+cred+"@"+uri+face_path,json=data_face,headers=headers)
	
	r = _requests.post(protocol+cred+"@"+uri+gender_path,json=data_gender,headers=headers)



	print('Done uploading data...\n')






def main():
	for i in range(17):
		push_test_data()



if __name__ == '__main__':
	main()

