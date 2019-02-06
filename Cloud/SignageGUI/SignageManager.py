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
        , 'data_server'       : '127.0.0.1:5000'
        , 'data_protocol'     : 'http://'
    }


    }

protocol=cfg_defaults['data']['data_protocol']
uri=cfg_defaults['data']['data_server']
cred=cfg_defaults['data']['credentials']
headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}



class SignageManager():

	def __init__(self):

		self.faces_live_url    = uri + '/api/v2/signage/faces/live/'
		self.faces_url         = uri + '/api/v2/signage/faces'

		self.activty_url       = uri + '/api/v2/signage/activity'
		self.activity_live_url = uri + '/api/v2/signage/activity/live/'

		self.demographics_url  = uri + '/api/v2/signage/demographics'
		self.demographics_live_url = uri + '/api/v2/signage/demographics/live/'



	def _fetch(self, url):
		response = _requests.get(protocol+cred+"@"+url,headers=headers)
		response_native = {'results': None}
		if response.status_code == _requests.codes.ok:
			response_native = json.loads(response.text)
		return response_native

	############## Face related functions ######################

	def live_faces(self, location):
		return pd.DataFrame.from_dict(self._fetch(self.faces_live_url + location))

	def faces(self):
		return pd.DataFrame.from_dict(self._fetch(self.faces_url))


	############## Activity related functions ####################

	def live_activity(self, location):
		return pd.DataFrame.from_dict(self._fetch(self.activity_live_url + location))


	def activity(self):
		return pd.DataFrame.from_dict(self._fetch(self.activty_url))


	############## Demographics related functons ##################

	def demographics(self):
		return pd.DataFrame.from_dict(self._fetch(self.demographics_url))


	def live_demograhics(self, location):
		return pd.DataFrame.from_dict(self._fetch(self.demographics_live_url + location))



	################ Header Row Functions #######################

	def total_impressions(self):

		faces = self.faces()
		faces['date_created'] = pd.to_datetime(faces['date_created'],unit='s')
		impressions_bydays = faces.groupby('date_created').agg({'no_faces':np.sum})
		impressions_bydays.reset_index(inplace = True)
		impressions_bydays= impressions_bydays.resample('D', on='date_created').sum()
		impressions_bydays.reset_index(inplace = True)
		impressions_bydays.fillna(value = 0, inplace = True)
		impressions_bydays = impressions_bydays.round(0)
		return impressions_bydays['no_faces'].sum()

	def avg_dwell_time(self):
		activity = self.activity()
		dwell = activity['time_alive'].mean()
		return dwell

	def engagement_range(self):
		faces = self.faces()
		faces_ = np.array(faces['distances'].tolist())
		mean_values = []
		for row in faces_:
			mean_values.append(np.array(row).mean())
		return np.array(mean_values).mean()

	def demographics_count(self):
		demographics = self.demographics()
		male_count = demographics['male_count'].sum()
		female_count = demographics['female_count'].sum()
		return (male_count, female_count)

	def age_group_summary(self):
		demographics = self.demographics()
		age_groups = demographics['age_list'].tolist()
		return max(set(age_groups), key=age_groups.count)


	def get_first_row_header(self):
		total_impressions = self.total_impressions()
		avg_dwell_time = self.avg_dwell_time()
		engagement_range = self.engagement_range()
		male_count,female_count = self.demographics_count()
		age_group = self.age_group_summary()

		return pd.DataFrame({"Total Impressions":[total_impressions], 
			"Avg Dwell time":[avg_dwell_time], 
			"Engagement Range":[engagement_range],
			"Male Count": [male_count],
			"Female Count": [female_count],"Age Group": [age_group]})




############# Test Functions #################

def test_engagement(smgr):
	df = smgr.live_faces('datagenerator')
	distances = np.around([distance for distance in itertools.chain.from_iterable(df['distances'].tolist())], decimals=2)

	count, y_values = np.histogram(distances, bins = 5, range=(1.0, max(distances)))


	data_frame = pd.DataFrame()
	x_values = []
	y_vals   = []


	for i in range(len(count)):
		if count[i] > 0:
			x_values.extend(np.random.randint(low=1, high=25, size=count[i]))
			y_vals.extend(np.repeat( ( (y_values[i] + y_values[i+1] )/2*1.0), count[i]))

	data_frame['x_vals'] = x_values
	data_frame['y_vals'] = y_vals

	print(data_frame)


def test_age_buckets(smgr):
	df = smgr.demographics()

	df = df[['location','age_list']]

	locations = df['location'].unique()

	data = []
	for location in locations:
		print(location)
		unique_age_buckets = []

		age_list = df[df['location'] == location]['age_list'].tolist()
		for age in age_list:
			content = ast.literal_eval(age)
			# Single or multiple tuples ?

			if type(content[0]) == int:
				unique_age_buckets.append(content)
			elif type(content[0]) == tuple:
				for c in content:
					unique_age_buckets.append(c) 

		print (unique_age_buckets)
		dic = collections.Counter(unique_age_buckets)
		print(dic)






def main():

	smgr = SignageManager()
	#test_age_buckets(smgr)



if __name__ == '__main__':
	main()

