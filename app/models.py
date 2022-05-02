from flask import current_app
from datetime import datetime
from app import db

visited = db.Table('visited',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('location_id', db.Integer, db.ForeignKey('location.id')),
    db.Column('date_tested', db.DateTime, default=datetime.utcnow())
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    gender = db.Column(db.Boolean)
    dob = db.Column(db.DateTime)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(120), index=True, unique=True)
    phone_number = db.Column(db.String(9), unique=True)
    id_type = db.Column(db.String(4))
    id_number = db.Column(db.String(10), unique=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    tests = db.relationship('Test', backref='owner', lazy='dynamic')
    
    # to add a new location to a user's history we can just call, <User >.visits.append(<Location >)
    visits = db.relationship('Location', secondary=visited, backref='wasvisitedby')

class TestingCenter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    region = db.Column(db.String(3))
    constituency = db.Column(db.String(140))
    location = db.relationship('Test', backref='location', lazy='dynamic')

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Integer)
    longitude = db.Column(db.Integer)
    location_name = db.Column(db.String(120))

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime)
    is_positive = db.Column(db.Boolean)
    is_asymptomatic = db.Column(db.Boolean)    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    testing_center_id = db.Column(db.Integer, db.ForeignKey('testing_center.id'))