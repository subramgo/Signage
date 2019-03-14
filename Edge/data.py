

import requests as _requests

class DataClient:
    """ Uses the signage.py configuration object and credentials. """
    def __init__(self,logger,cfg):
        self.logger = logger
        self.cfg = cfg['data']
        self.camfig = cfg['camera']
        
        if not self.cfg['enabled']:
            logger.info("Data reporting is disabled.")
        else:
            try:
                logger.info("Connecting to data service...")
                _requests.get(self.cfg['data_protocol']+self.cfg['data_server'])
                logger.info("Database is available.")
            except (_requests.exceptions.ConnectionError,_requests.exceptions.Timeout,_requests.exceptions.HTTPError) as err: 
                logger.error("Cannot reach data reporting service; "+str(err))

    def upload(self,audience_measures):
        if not self.cfg['enabled'] or not audience_measures:
            return

        protocol=self.cfg['data_protocol']
        uri=self.cfg['data_server']
        cred=self.cfg['credentials']
        path='/api/v2/signage/person/upload'

        camera_id=self.camfig['name']
        location=self.camfig['location_name'] 

        self.logger.info("Uploading demographics...")
        for person in audience_measures:
            data = {
                      'camera_id' : camera_id
                    , 'gender'    : person.gender
                    , 'age'       : person.age
                    , 'time_alive': str(person.time_alive)
                    , 'engagement_range' : str(person.engagement_range)
                    , 'location'  : location
                    , 'face_id'   : str(person.iduid)
                    }
            headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            r = _requests.post(protocol+cred+"@"+uri+path,json=data,headers=headers)
            
            self.logger.info("    ... {}".format(r if r.ok else r.reason + " " + str(r)))

