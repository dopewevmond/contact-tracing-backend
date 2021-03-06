from flask import current_app
from datetime import datetime, timedelta
from app import db
from passlib.apps import custom_app_context as pwd_context
from app.search import add_to_index, remove_from_index, query_index
from sqlalchemy.sql import func


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session.changes = None

    
    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)


class Visited(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    date_visited = db.Column(db.DateTime, default=func.now())
    visited_by = db.relationship('User', back_populates='visits')
    location_visited = db.relationship('Location', back_populates='has_been_visited_by')


def risk_people_emails(date_of_contraction = datetime.utcnow(), user_id=None, user_email=None):
    if user_id == None or user_email == None:
        return set()
    two_weeks_earlier = date_of_contraction - timedelta(days=14)
    locations = db.session.query(Visited.location_id, Visited.date_visited)\
        .filter(Visited.user_id == user_id)\
        .filter(Visited.date_visited.between(two_weeks_earlier, date_of_contraction))\
        .all()
    users_details = set()
    for location_id, date in locations:
        twelve_hours_before = date - timedelta(hours=12)
        twelve_hours_after = date + timedelta(hours=12)
        users_emails = db.session.query(User.email) \
                            .filter(Visited.user_id == User.id)\
                            .filter(Visited.location_id == location_id) \
                            .filter(Visited.date_visited.between(twelve_hours_before, twelve_hours_after))\
                            .all()
        for email in users_emails:
            users_details.add(email[0])
    # the user who contracted covid's email will also be in the set...
    # ... so we need to delete it from the set so that we can notify...
    # ... the rest of the users
    users_details.remove(user_email)
    return users_details
        


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

class User(SearchableMixin, db.Model):
    __searchable__ = ['username', 'first_name', 'other_names', 'last_name']
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64))
    other_names = db.Column(db.String(64))
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
    is_being_verified = db.Column(db.Boolean(), default=False)
    image_link_for_verification = db.Column(db.String(500))

    knows = db.relationship(
        'User', secondary=known_by,
        primaryjoin=(known_by.c.knows_id == id),
        secondaryjoin=(known_by.c.known_id == id),
        backref=db.backref('known_by', lazy='dynamic'), lazy='dynamic')
    
    # to add a new location to a user's history we can just call, <User >.visits.append(<Location >)
    # the lazy='dynamic' was added to all backrefs to allow the count() method to be called on the queries
    visits = db.relationship('Visited', back_populates='visited_by')

    verification_requests = db.relationship('Verification', backref='author', lazy='dynamic')

    def hash_password(self, password):
        self.password_hash = pwd_context.hash(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def is_known_by(self, user):
        """
        Returns True if self is known by user
        """
        return self in user.knows.all()

    def add_contact(self, user):
        if not user.is_known_by(self):
            self.knows.append(user)
            db.session.add(self)
            db.session.commit()

    def remove_contact(self, user):
        if user.is_known_by(self):
            self.knows.remove(user)
            db.session.add(self)
            db.session.commit()

    def visited_locations(self):
        return db.session.query(Location.location_name, Visited.date_visited)\
            .filter(Location.id == Visited.location_id)\
            .filter(Visited.user_id == self.id)\
            .order_by(Visited.date_visited.desc())
    
    @classmethod
    def check_if_username_exists(cls, username):
        return cls.query.filter_by(username=username).count() > 0

    def has_applied_for_verification(self):
        return self.verification_requests.count() > 0

    def revoke_verification_request(self):
        if self.has_applied_for_verification():
            self.verification_requests.delete()
            db.session.commit()

    def apply_for_verification(self):
        if not self.has_applied_for_verification():
            ver = Verification(user_id=self.id)
            db.session.add(ver)
            db.session.commit()

    def get_all_close_contacts_emails(self):
        """Returns the emails of all close contacts of a user"""
        emails = []
        for user in self.knows.all():
            emails.append(user.email)
        return emails


class Verification(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow())


class TestingCenter(SearchableMixin, db.Model):
    __searchable__ = ['name', 'region', 'constituency']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    region = db.Column(db.String(3))
    constituency = db.Column(db.String(140))
    latitude = db.Column(db.Integer)
    longitude = db.Column(db.Integer)

    @classmethod
    def search_by_region(cls, region):
        return cls.query.filter_by(region=region)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Integer)
    longitude = db.Column(db.Integer)
    location_name = db.Column(db.String(120))
    has_been_visited_by = db.relationship('Visited', back_populates='location_visited')

    @classmethod
    def search_by_lat_and_lon(cls, lat, lon):
        return cls.query.filter_by(latitude=lat).filter_by(longitude=lon)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow())
    is_positive = db.Column(db.Boolean)
    is_asymptomatic = db.Column(db.Boolean)    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    testing_center_id = db.Column(db.Integer, db.ForeignKey('testing_center.id'))