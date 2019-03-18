import requests as _requests
import json
import pandas as pd 
import numpy as np
import itertools
import collections
import ast

cfg_defaults = { 
      'camera'                : {
          'enabled'           : False
        , 'stream_address'    : '192.168.1.168/usecondstream'
        , 'protocol'          : 'rtsp://'
        , 'location_name'     : 'signage-analysis-demo'
        , 'name'              : 'signage-camera-1'
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


class SignageManager():
	def __init__(self):
		self.person_url = uri + '/api/v2/signage/person'
		self.person_live_url = uri + '/api/v2/signage/person/live/'

	def _fetch(self, url):
		response = _requests.get(protocol+cred+"@"+url,headers=headers)
		response_native = {'results': None}
		if response.status_code == _requests.codes.ok:
			response_native = json.loads(response.text)
		return response_native

	def live_person(self, location):
		return_df = pd.DataFrame()
		try:
			return_df = pd.DataFrame.from_dict(self._fetch(self.person_live_url + location))
		except Exception as e:
			return return_df
		
		return  return_df

	def person(self):
		return_df = pd.DataFrame()
		try:
			return_df = pd.DataFrame.from_dict(self._fetch(self.person_url))
		except Exception as e:
			return return_df
		
		return  return_df





	################ Header Row Functions #######################

	def get_first_row_header(self):

		person = self.person()
		total_impressions = person['face_id'].count()
		avg_dwell_time = person['time_alive'].mean()
		engagement_range = person['engagement_range'].mean()
		male_count = person[person['gender'] == 'male']['face_id'].count()
		female_count = person[person['gender'] == 'female']['face_id'].count()

		teen_count = person[person['age'] == 'teen']['face_id'].count()
		adult_count = person[person['age'] == 'adult']['face_id'].count()
		senior_count = person[person['age'] == 'senior']['face_id'].count()

		age_ = {'teen': teen_count, 'adult':adult_count, 'senior':senior_count}
		age_ = sorted(age_.items(), key=lambda x: (x[1],x[1]), reverse=True)

		age_group = age_[0][0]

		return pd.DataFrame({"Total Impressions":[total_impressions], 
			"Avg Dwell time":[avg_dwell_time], 
			"Engagement Range":[engagement_range],
			"Male Count": [male_count],
			"Female Count": [female_count],"Age Group": [age_group]})










def main():

	smgr = SignageManager()
	df = smgr.person()
	df = df.groupby(['location','gender']).aggregate({'face_id':'nunique'}).reset_index()
	print(df)
	locations = df['location'].unique()

	male_count = []
	female_count = []

	for location in locations:
		print(df[ (df['location'] == location) & (df['gender'] == 'male')]['face_id'].values)
		print(df[ (df['location'] == location) & (df['gender'] == 'female')]['face_id'].values)




def gender_count(in_pd):
	res = in_pd.groupby(['location','gender']).aggregate({'face_id':'nunique'}).reset_index()
	print(res)

if __name__ == '__main__':
	main()

