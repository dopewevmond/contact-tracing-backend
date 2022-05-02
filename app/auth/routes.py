from app.auth import bp
from flask_restful import Api, Resource, abort, reqparse, fields, marshal_with
from app.models import User
from flask import jsonify, make_response
from app import db

api = Api(bp)

user_fields =  {
    'id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'username': fields.String,
    'email': fields.String,
    'gender': fields.Boolean,
    'dob': fields.DateTime,
    'phone_number': fields.String,
    'is_verified': fields.Boolean,
    'is_admin': fields.Boolean,
}

class SignupUserAPI(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('username', type=str, required=True, help='No username provided', location='json')
        self.reqparse.add_argument('password', type=str, required=True, help='No password was entered', location='json')
        super(SignupUserAPI, self).__init__()

    def post(self):
        args = self.reqparse.parse_args()
        username = args['username']
        password = args['password']
        if username is None or password is None:
            abort(400)
        if User.query.filter_by(username=username).first() is not None:
            abort(400)
        user = User(username=username)
        user.hash_password(password)
        print('about to add user', username)
        db.session.add(user)
        db.session.commit()
        return make_response(jsonify({"username": username}), 200)

class UserListAPI(Resource):
    @marshal_with(user_fields)
    def get(self):
        users = User.query.all()
        return users

    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

api.add_resource(UserListAPI, '/contact-tracing/api/v1.0/users', endpoint='all_users')
api.add_resource(SignupUserAPI, '/contact-tracing/api/v1.0/users/signup', endpoint='signup')