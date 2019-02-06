import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

SQLALCHEMY_ECHO = True

SQLALCHEMY_DATABASE_URI =  \
        'sqlite:///' + os.path.join(basedir, 'signage.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
UPLOADED_PHOTOS_DEST=os.path.join(basedir + '/uploads')
UPLOADED_FACE_DEST=os.path.join(basedir + '/uploads/face')
