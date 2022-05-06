from . import bp
from ..models import User
from flask_restful import Api, Resource, reqparse, fields, marshal_with, marshal
from app.auth.routes import token_required, admin_access_required

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
    decorators = [admin_access_required]
    def get(self, current_user):
        users = User.query.all()
        return marshal(users, user_fields)

    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

class ContactListAPI(Resource):
    decorators = [token_required]    

    def get(self, current_user, id):
        print('owns resource?', current_user.id == id)
        print('is_admin?', current_user.is_admin)
        if current_user.id == id or current_user.is_admin:
            user = User.query.filter_by(id=id).first()
            contacts = user.knows.all()
            return marshal(contacts, user_fields)
        return {
                "message": "Unauthorized to access this resource",
                "data": None,
                "error": "Unauthorized"
        }, 401
        


api.add_resource(UserListAPI, '/api/v1.0/users', endpoint='all_users')
api.add_resource(ContactListAPI, '/api/v1.0/contacts/<int:id>', endpoint='all_contacts')