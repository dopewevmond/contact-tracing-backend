from flask import current_app
from datetime import datetime
from app import db
from passlib.apps import custom_app_context as pwd_context

visited = db.Table('visited',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('location_id', db.Integer, db.ForeignKey('location.id')),
    db.Column('date_tested', db.DateTime, default=datetime.utcnow())
)


# based on the implementation in Flask Mega Tutorial by Miguel Grinberg, Part VIII
# for every entry in the `known_by` association table, the left entity is assumed to know the right entity. 
# For instance, a representation of the users who know a <User id=3>.ie.(with an id of 3) might be
# represented in the `known_by` association table as

####################################
##   knows_id    ##   known_id    ##
####################################
##       1       ##        3      ##
##       2       ##        3      ##
##       7       ##        3      ##
##       9       ##        3      ##
##      13       ##        3      ##
####################################

# a relationship can therefore be defined on the left side of the User class as `knows`
# and a backref `known_by` can be defined to access the relationship from the right entity.
# the above could be obtained by running <User id=3>.known_by

known_by = db.Table('known_by',
    db.Column('knows_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('known_id', db.Integer, db.ForeignKey('user.id'))
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
    is_email_verified = db.Column(db.Boolean, default=False)
    is_number_verified = db.Column(db.Boolean, default=False)

    knows = db.relationship(
        'User', secondary=known_by,
        primaryjoin=(known_by.c.knows_id == id),
        secondaryjoin=(known_by.c.known_id == id),
        backref=db.backref('known_by', lazy='dynamic'), lazy='dynamic')
    
    # to add a new location to a user's history we can just call, <User >.visits.append(<Location >)
    visits = db.relationship('Location', secondary=visited, backref='wasvisitedby')

    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)



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