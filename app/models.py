from flask import current_app
from datetime import datetime
from app import db
from passlib.apps import custom_app_context as pwd_context
from app.search import add_to_index, remove_from_index, query_index


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

    knows = db.relationship(
        'User', secondary=known_by,
        primaryjoin=(known_by.c.knows_id == id),
        secondaryjoin=(known_by.c.known_id == id),
        backref=db.backref('known_by', lazy='dynamic'), lazy='dynamic')
    
    # to add a new location to a user's history we can just call, <User >.visits.append(<Location >)
    # the lazy='dynamic' was added to all backrefs to allow the count() method to be called on the queries
    visits = db.relationship('Location', secondary=visited, backref=db.backref('wasvisitedby', lazy='dynamic'), lazy='dynamic')

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
        return db.session.query(Location.location_name, visited.c.date_tested)\
            .filter(Location.id == visited.c.location_id)\
            .filter(visited.c.user_id == self.id)\
            .order_by(visited.c.date_tested.desc())
    
    @classmethod
    def check_if_username_exists(cls, username):
        return cls.query.filter_by(username=username).count() > 0


class TestingCenter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    region = db.Column(db.String(3))
    constituency = db.Column(db.String(140))
    location = db.relationship('Test', backref='location', lazy='dynamic')

    @classmethod
    def search_by_region(cls, region):
        return cls.query.filter_by(region=region)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Integer)
    longitude = db.Column(db.Integer)
    location_name = db.Column(db.String(120))

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