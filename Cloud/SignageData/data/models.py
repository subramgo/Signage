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


# One table to rule all
class Person(signage_db.Model):
    
    id = signage_db.Column(signage_db.Integer, primary_key=True, autoincrement=True)
    location   = signage_db.Column(signage_db.String)
    camera_id = signage_db.Column(signage_db.String)
    date_created = signage_db.Column(signage_db.DateTime, default=signage_db.func.current_timestamp())
    face_id = signage_db.Column(signage_db.Integer)
    gender = signage_db.Column(signage_db.String)
    time_alive = signage_db.Column(signage_db.Float)
    age = signage_db.Column(signage_db.String)
    engagement_range= signage_db.Column(signage_db.Float)



    def get_json(self):

        return_value = {}
        return_value["id"] = self.id 
        return_value['camera_id'] = self.camera_id
        epoch = datetime.datetime(1970,1,1)
        delta_time = (self.date_created - epoch).total_seconds()
        return_value['date_created'] = delta_time
        return_value['face_id'] = self.face_id
        return_value['age'] = self.age
        return_value['location'] = self.location
        return_value['gender'] = self.gender
        return_value['time_alive'] = self.time_alive
        return_value['engagement_range'] = self.engagement_range


        return return_value

    def __repr__(self):
        return '<id {} date_created {} camera_id {} face_id {} age {}\
         location {} gender {} time_alive {} engagement_range {}>'.format(self.id, 
            self.date_created, self.camera_id, self.face_id, self.age,
            self.location, self.gender, self.time_alive,self.engagement_range)





