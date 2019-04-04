from flask_sqlalchemy import SQLAlchemy
import datetime
import passlib
from passlib.apps import custom_app_context as pwd_context
import json


signage_db = SQLAlchemy()

############### Helper function to jsonify results ########################
def to_json(inst, cls):
    """
    Jsonify the sql alchemy query result.
    """
    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if v is None:
            d[c.name] = str()
        elif c.type == signage_db.Column(signage_db.DateTime).type:
            d[c.name] = v.isoformat()
        else:
            d[c.name] = str(v)
    return d


class Enterprise(signage_db.Model):
    id = signage_db.Column(signage_db.Integer, primary_key = True)
    enterprise_name = signage_db.Column(signage_db.String(32), index = True)
    stores = signage_db.relationship('Store', backref='store', lazy='dynamic')


    @property
    def json(self):
        return to_json(self, self.__class__)

class Store(signage_db.Model):
    id = signage_db.Column(signage_db.Integer, primary_key = True)
    store_name = signage_db.Column(signage_db.String(32), index = True)
    address = signage_db.Column(signage_db.String(32), index = True)
    city = signage_db.Column(signage_db.String(32), index = True)
    state = signage_db.Column(signage_db.String(32), index = True)
    zipcode = signage_db.Column(signage_db.String(32), index = True)
    enterprise_id = signage_db.Column(signage_db.Integer, signage_db.ForeignKey('enterprise.id'))
    signages = signage_db.relationship('Signage', backref='signage', lazy='dynamic')


    @property
    def json(self):
        return to_json(self, self.__class__)

class Signage(signage_db.Model):
    id = signage_db.Column(signage_db.Integer, primary_key = True)
    zone = signage_db.Column(signage_db.String(32), index = True)
    store_id = signage_db.Column(signage_db.Integer, signage_db.ForeignKey('store.id'))
    contents = signage_db.relationship('Content', backref='content', lazy='dynamic')
    persons = signage_db.relationship('Person', backref='person', lazy='dynamic')


    @property
    def json(self):
        return to_json(self, self.__class__)


class Content(signage_db.Model):
    id = signage_db.Column(signage_db.Integer, primary_key = True)
    from_date = signage_db.Column(signage_db.DateTime, default=signage_db.func.current_timestamp())
    to_date = signage_db.Column(signage_db.DateTime, default=signage_db.func.current_timestamp())
    signage_id = signage_db.Column(signage_db.Integer, signage_db.ForeignKey('signage.id'))
    description = signage_db.Column(signage_db.String)


    @property
    def json(self):
        return to_json(self, self.__class__)

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
    signage_id = signage_db.Column(signage_db.Integer, signage_db.ForeignKey('signage.id'))

    @property
    def json(self):
        return to_json(self, self.__class__)







