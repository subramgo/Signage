
import requests as _requests

class DataClient:
    """ Uses the signage.py configuration object and credentials. """
    def __init__(self,logger,cfg):
        self.logger = logger
        self.cfg = cfg

        if self.cfg['data_service']:
            try:
                self.logger.info("Connecting to data service...")
                _requests.get(self.cfg['data_protocol']+self.cfg['data_server'])
                self.logger.info("Database is available.")
            except (_requests.exceptions.ConnectionError,_requests.exceptions.Timeout,_requests.exceptions.HTTPError) as err: 
                self.logger.error("Cannot reach data reporting service; "+str(err))
            logger.info("Connected to data server.")
        else:
            logger.info("Data reporting is disabled.")

    def upload_faces(self,windows):
        if not self.cfg['data_service']:
            return
        protocol=self.cfg['data_protocol']
        uri=self.cfg['data_server']
        cred=self.cfg['data_credentials']
        path='/api/v2/signage/faces'

        camera_id=self.cfg['cam_name']
        location=self.cfg['cam_location_name']
        data = {
                'camera_id' : camera_id
               ,'no_faces'  : str(len(windows))
               ,'windows'   : ",".join(str(r) for v in windows for r in v)
               ,'location'  : location
                }
        headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        self.logger.info("Uploading detections...")
        r = _requests.post(protocol+cred+"@"+uri+path,json=data,headers=headers)
        self.logger.info("Detections upload: "+str(r))


    def upload_demographics(self,genders):
        if not self.cfg['data_service']:
            return
        protocol=self.cfg['data_protocol']
        uri=self.cfg['data_server']
        cred=self.cfg['data_credentials']
        path='/api/v2/signage/demographics'

        camera_id=self.cfg['cam_name']
        location=self.cfg['cam_location_name'] 

        data = {
                'camera_id'    : camera_id
               ,'location'     : location
               ,'male_count'   : sum([1 for g in genders if g[0]=='male'])
               ,'female_count' : sum([1 for g in genders if g[0]=='female'])
               ,'gender_list'     : ','.join(str( g[0] ) for g in genders)
               ,'age_list' : ','.join(str( g[1] ) for g in genders)
        }
        headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        self.logger.info("Uploading demographics...")
        r = _requests.post(protocol+cred+"@"+uri+path,json=data,headers=headers)
        self.logger.info("Demographics upload: "+str(r))


