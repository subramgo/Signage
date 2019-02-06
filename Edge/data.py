
import requests as _requests

class DataClient:
    """ Uses the signage.py configuration object and credentials. """
    def __init__(self,logger,cfg,camfig):
        self.logger = logger
        self.cfg = cfg
        self.camfig = camfig
        
        if not cfg['enabled']:
            logger.info("Data reporting is disabled.")
        else:
            try:
                logger.info("Connecting to data service...")
                _requests.get(self.cfg['data_protocol']+self.cfg['data_server'])
                logger.info("Database is available.")
            except (_requests.exceptions.ConnectionError,_requests.exceptions.Timeout,_requests.exceptions.HTTPError) as err: 
                logger.error("Cannot reach data reporting service; "+str(err))

    def upload_windows(self,windows):
        if not self.cfg['enabled']:
            return
        protocol=self.cfg['data_protocol']
        uri=self.cfg['data_server']
        cred=self.cfg['credentials']
        path='/api/v2/signage/faces'

        camera_id=self.camfig['name']
        location=self.camfig['location_name']
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


    def upload_demographics(self,demographics):
        if not self.cfg['enabled'] or not demographics:
            return
        protocol=self.cfg['data_protocol']
        uri=self.cfg['data_server']
        cred=self.cfg['credentials']
        path='/api/v2/signage/demographics'

        camera_id=self.camfig['name']
        location=self.camfig['location_name'] 

        data = {
                'camera_id'    : camera_id
               ,'location'     : location
               ,'male_count'   : sum([1 for g in demographics if g[0]=='male'])
               ,'female_count' : sum([1 for g in demographics if g[0]=='female'])
               ,'gender_list'     : ','.join(str( g[0] ) for g in demographics)
               ,'age_list' : ','.join(str( g[1] ) for g in demographics)
        }
        headers  = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        self.logger.info("Uploading demographics...")
        r = _requests.post(protocol+cred+"@"+uri+path,json=data,headers=headers)
        self.logger.info("Demographics upload: "+str(r))

