from . import bp
from ..models import User
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from app.auth.routes import token_required

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

class UserListAPI(Resource):
    decorators = [token_required]
    @marshal_with(user_fields)
    def get(self, current_user):
        users = User.query.all()
        return users

    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

api.add_resource(UserListAPI, '/api/v1.0/users', endpoint='all_users')