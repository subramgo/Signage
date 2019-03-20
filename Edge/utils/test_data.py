

import log,data,sharedconfig,signage

sharedconfig.cfg['camera']['location'] = 'test'
sharedconfig.cfg['camera']['name'] = 'testcam'

client = data.DataClient(log.get_null_logger(),sharedconfig.cfg)

face_id = 99
time_alive = 5
engagement_range = 4
gender = 'male'
age = 25

testguy = signage.Measure(face_id,time_alive,engagement_range,gender,age)

print('uploading testguy...')

client.upload([testguy])

