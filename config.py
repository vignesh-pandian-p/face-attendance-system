import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-hard-to-guess-string'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:@localhost/face_attendance'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
