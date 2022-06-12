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
    SWAGGER = {
        'title': 'Contact Tracing API',
        'doc_dir': os.path.join(basedir, 'docs'),
        'description': 'Documentation for contact tracing REST API',
        'version': '1.0.0'
    }
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True