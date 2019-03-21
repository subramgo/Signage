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
       # , 'data_server'       : 'signagedata.azurewebsites.net'
        , 'data_server'       : '0.0.0.0:5000/api/v2/signage'

        #, 'data_protocol'     : 'https://'
        , 'data_protocol'     : 'http://'

    }


    }

protocol=cfg_defaults['data']['data_protocol']
uri=cfg_defaults['data']['data_server']
cred=cfg_defaults['data']['credentials']
headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}


class SignageManager():
	
	def __init__(self):
		self.person_url = uri + '/person/'
		self.person_live_url = uri + '/person/live/'
		self.stores_url = uri + '/store/all/'
		self.single_store_url = uri + '/store/'
		self.signage_url = uri + '/signage/'
		self.signage_single_url = uri + '/signage/single/'
		self.enterprise_url = uri + '/enterprise'

	def _fetch(self, url):
		response = _requests.get(protocol+cred+"@"+url,headers=headers)
		response_native = {'results': None}
		if response.status_code == _requests.codes.ok:
			response_native = json.loads(response.text)
		return response_native

	def live_person(self, signage_id):
		return_df = pd.DataFrame()
		try:
			#return_df = pd.DataFrame.from_dict(self._fetch(self.person_live_url + signage_id))
			return_df = self.person(signage_id)

		except Exception as e:
			return return_df
		
		return  return_df

	def person(self, signage_id=11):
		return_df = pd.DataFrame()
		signage_id = str(signage_id)

		try:
			return_df = pd.DataFrame.from_dict(self._fetch(self.person_url + signage_id))
			return_df.engagement_range = pd.to_numeric(return_df.engagement_range)
			return_df.time_alive = pd.to_numeric(return_df.time_alive)
			return_df.date_created = pd.to_datetime(return_df.date_created)



		except Exception as e:
			return return_df

		
		return  return_df

	def stores(self, enterprise_id):
		return_df = pd.DataFrame()
		enterprise_id = str(enterprise_id)

		try:
			return_df = pd.DataFrame.from_dict(self._fetch(self.stores_url + enterprise_id))
		except Exception as e:
			return return_df
		
		return  return_df

	def store(self, store_id):
		return_df = pd.DataFrame()
		store_id = str(store_id)

		try:
			return_df = pd.DataFrame.from_dict(self._fetch(self.single_store_url + store_id))
		except Exception as e:
			return return_df
		
		return  return_df


	def enterprise(self):
		return_df = pd.DataFrame()

		try:
			return_df = pd.DataFrame.from_dict(self._fetch(self.enterprise_url))
		except Exception as e:
			return return_df
		
		return  return_df


	def signage_details(self, signage_id):
		return_df = pd.DataFrame()
		signage_id = str(signage_id)

		try:
			return_df = pd.DataFrame.from_dict(self._fetch(self.signage_single_url + signage_id))
		except Exception as e:
			return return_df
		
		return  return_df

	def signage(self, store_id):
		return_df = pd.DataFrame()
		store_id = str(store_id)

		try:
			return_df = pd.DataFrame.from_dict(self._fetch(self.signage_url + store_id))
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

	

	############### get locations ##################################

	def get_locations(self):
	    """
	    Returns list of location for drop down box
	    """
	    faces = self.person()
	    if faces.empty == True:
	        return ({'label': "NA", 'value': "NA"},"N/A")

	    locations = faces['location'].unique()

	    options_ = []

	    for location in locations:
	        option = {'label': location, 'value': location}
	        options_.append(option)

	    return (options_, location)


	def get_signage(self, store_id):
	    """
	    Returns list of enterprise for drop down box
	    """
	    signs = self.signage(store_id)
	    if signs.empty == True:
	        return ({'label': "NA", 'value': "NA"},"N/A")

	    snames = signs['zone'].unique()
	    sids   = signs['id'].unique()


	    options_ = []

	    for i, sname in enumerate(snames):
	        option = {'label': sname, 'value': sids[i]}
	        options_.append(option)

	    return (options_, sids[0])

	def get_stores(self, enterprise_id):
	    """
	    Returns list of enterprise for drop down box
	    """
	    stores = self.stores(enterprise_id)
	    if stores.empty == True:
	        return ({'label': "NA", 'value': "NA"},"N/A")

	    snames = stores['store_name'].unique()
	    sids   = stores['id'].unique()


	    options_ = []

	    for i, sname in enumerate(snames):
	        option = {'label': sname, 'value': sids[i]}
	        options_.append(option)

	    return (options_, sids[0])


	def get_enterprise(self):
	    """
	    Returns list of enterprise for drop down box
	    """
	    enterprises = self.enterprise()
	    if enterprises.empty == True:
	        return ({'label': "NA", 'value': "NA"},"N/A")

	    enames = enterprises['enterprise_name'].unique()
	    eids   = enterprises['id'].unique()


	    options_ = []

	    for i, ename in enumerate(enames):
	        option = {'label': ename, 'value': eids[i]}
	        options_.append(option)

	    return (options_, eids[0])
	

	def _decay_func(self,x):
	    return (1/2)**x

	def _calculate_engagement(self,in_df, time_alive_col, eng_range_col, normalize=True):
	    
	    x1 = np.array(in_df[time_alive_col], dtype=np.float32)
	    x2 = np.array(in_df[eng_range_col], dtype=np.float32)



	    in_df['engagement_timealive'] = np.exp(x1)
	    in_df['engagement_distance']  = self._decay_func(x2)

	    in_df['total_engagement'] = 0.5 * in_df['engagement_timealive'] + \
	    0.5 * in_df['engagement_distance']
	    
	    if normalize:

	        in_df['normalized_engagement'] = (in_df['total_engagement'] - in_df['total_engagement'].min())\
	        /(in_df['total_engagement'].max()- in_df['total_engagement'].min())

	    

	    
	    return in_df


	def overall_effectiveness(self, signage_id):

		persons = self.person(signage_id)

		persons.date_created = pd.to_datetime(persons.date_created)
		persons['hour_of_day'] = persons.date_created.dt.hour
		persons['dayofweek'] = persons.date_created.dt.dayofweek

		effect = self._calculate_engagement(persons, 'time_alive','engagement_range')

		return effect

	def get_recommendation(self,signage_id):
		
		df = self.overall_effectiveness(int(signage_id))


		rules = []
		rules_dict = {}

		male_rating = df[df.gender == 'male']['normalized_engagement'].mean() * 10
		female_rating = df[df.gender == 'female']['normalized_engagement'].mean() * 10

		if male_rating > female_rating:
			rules_dict['Gender Effect'] = ['Male customers are more engaged with the contents']
		else:
			rules_dict['Gender Effect'] = ['Female customers are more engaged with the contents']


		teen_rating = df[df.age == 'teen']['normalized_engagement'].mean() * 10
		adult_rating = df[df.age == 'adult']['normalized_engagement'].mean() * 10
		senior_rating = df[df.age == 'senior']['normalized_engagement'].mean() * 10

		if teen_rating > adult_rating:
			if teen_rating > senior_rating:
				rules_dict['Age Effect'] = ['Teen customers are more engaged with the contents']
		else:
			if adult_rating > senior_rating:
				rules_dict['Age Effect'] = ['Adult customers are more engaged with the contents']
			else:
				rules_dict['Age Effect'] = ['Senior customers are more engaged with the contents']

		rules_df = pd.DataFrame.from_dict(rules_dict)

		return rules_dict


def main():
	smgr = SignageManager()
	df = smgr.person()

	df = df[['location','time_alive']]
	locations = df['location'].unique()
	bar_data = []
    
	for location in locations:
		vals = df[df['location'] == location]['time_alive'].tolist()
		print(vals)
		tot  = sum(vals)
		count = len(vals)

def enterprise():
	smgr = SignageManager()
	signages = smgr.enterprise()
	print(signages.head())

def signs():
	smgr = SignageManager()
	signages = smgr.signage(200)
	print(signages.head())



def stores():
	smgr = SignageManager()
	stores = smgr.stores(100)
	print(stores.head())

def store():
	smgr = SignageManager()
	stores = smgr.store(200)
	print(stores.head())

def test():
	smgr = SignageManager()
	sign_dtls = smgr.signage_details(11)
	st_dtls = smgr.store(int(sign_dtls['store_id']))
	print(st_dtls.head())

def person():
	smgr = SignageManager()
	person = smgr.person(11)
	print(person.head())

def live_person():
	smgr = SignageManager()
	person = smgr.live_person(11)
	print(person.head())

def effect():
	smgr = SignageManager()
	locations = smgr.get_locations()
	df = smgr.overall_effectiveness('boca-mac-1')
	print(df.head())


def gender_Test():

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
	test()


