import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') \
        or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'akldfaLKSasd-0423/'
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL')
    USERS_PER_PAGE = 10
    AWS_S3_BUCKET_NAME = os.environ.get('AWS_S3_BUCKET_NAME')