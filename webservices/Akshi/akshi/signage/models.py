from flask_sqlalchemy import SQLAlchemy
import datetime
import passlib
from passlib.apps import custom_app_context as pwd_context

signage_db = SQLAlchemy()

class User(signage_db.Model):
    id = signage_db.Column(signage_db.Integer, primary_key = True)
    username = signage_db.Column(signage_db.String(32), index = True)
    password_hash = signage_db.Column(signage_db.String(128))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

class FaceSignage(signage_db.Model):
    id = signage_db.Column(signage_db.Integer, primary_key=True, autoincrement=True)
    location   = signage_db.Column(signage_db.String)
    camera_id = signage_db.Column(signage_db.String)
    date_created = signage_db.Column(signage_db.DateTime, default=signage_db.func.current_timestamp())
    image_id = signage_db.Column(signage_db.String)
    no_faces = signage_db.Column(signage_db.Integer)
    windows = signage_db.Column(signage_db.String)

    def get_json(self):
    	return_value = {}
    	return_value["id"] = self.id 
    	return_value['camera_id'] = self.camera_id
    	epoch = datetime.datetime(1970,1,1)
    	delta_time = (self.date_created - epoch).total_seconds()
    	return_value['date_created'] = delta_time
    	return_value['no_faces'] = self.no_faces
    	return_value['windows'] = self.windows
    	return_value['image_id'] = self.image_id
    	return_value['location'] = self.location

    	return return_value

    def __repr__(self):
        return '<id {} date_created {} camera_id {} no_faces {} windows {} image_id {} location {}>'.format(self.id, 
        	self.date_created, self.camera_id, self.no_faces, self.windows, self.image_id,self.location)

class Demographics(signage_db.Model):
    id = signage_db.Column(signage_db.Integer, primary_key=True, autoincrement=True)
    date_created = signage_db.Column(signage_db.DateTime, default=signage_db.func.current_timestamp())
    location   = signage_db.Column(signage_db.String)
    camera_id = signage_db.Column(signage_db.String)
    male_count = signage_db.Column(signage_db.Integer)
    female_count = signage_db.Column(signage_db.Integer)
    gender_list = signage_db.Column(signage_db.String)
    age_list = signage_db.Column(signage_db.String)


    def get_json(self):
        return_value = {}
        return_value["id"] = self.id 
        epoch = datetime.datetime(1970,1,1)
        delta_time = (self.date_created - epoch).total_seconds()
        return_value['date_created'] = delta_time
        return_value['location'] = self.location
        return_value['camera_id'] = self.camera_id
        return_value['male_count'] = self.male_count
        return_value['female_count'] = self.female_count
        return_value['gender_list'] = self.gender_list
        return_value['age_list'] = self.age_list


        return return_value
