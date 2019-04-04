import os


basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

SQLALCHEMY_ECHO = True

POSTGRES = {
    'user': 'postgres',
    'pw': 'docker',
    'db': 'signage',
    'host': '0.0.0.0',
    'port': '5432',
}

SQLALCHEMY_DATABASE_URI ='postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

TIMEOUT=20
SQLALCHEMY_TRACK_MODIFICATIONS = False
UPLOADED_PHOTOS_DEST=os.path.join(basedir + '/uploads')
UPLOADED_FACE_DEST=os.path.join(basedir + '/uploads/face')
