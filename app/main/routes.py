from . import bp
from ..models import User
from flask_restful import Api, Resource, abort, reqparse, fields, marshal_with, marshal
from app.auth.routes import token_required, admin_access_required
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

class ContactListAPI(Resource):
    decorators = [token_required]    

    def get(self, current_user, id):
        """
        Retrieves all contacts of a user with id == params:id. Can be accessed only by owner of resource.
        """
        if current_user.id == id:
            user = User.query.filter_by(id=id).first()
            contacts = user.knows.all()
            return marshal(contacts, user_fields)
        return {
                "message": "Unauthorized to access this resource",
                "data": None,
                "error": "Unauthorized"
        }, 401


    def post(self, current_user, id):
        """
        Allows current user to add another user with id of `contact_id` in request body to their close contacts.ie. 'know' them. Can be accessed only by owner of resource.
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('contact_id', type=int, help='ID of user to add was not found', location='json')

        args = self.reqparse.parse_args()
        contact_id = args['contact_id']
        if contact_id is None:
            abort(400)

        user_to_add_to_contacts = User.query.get(contact_id)
        if not user_to_add_to_contacts or user_to_add_to_contacts.is_known_by(current_user):
            return {
                "message": "Bad request",
                "data": None,
                "error": "Bad request"
        }, 400

        current_user.knows.append(user_to_add_to_contacts)
        db.session.add(current_user)
        db.session.commit()
        return {"message": "Added contact successfully", "error": None, "data": contact_id}, 200


class ContactAPI(Resource):
    decorators = [token_required]

    def delete(self, current_user, id, contact_id):
        user_to_remove = User.query.get(contact_id)
        if not user_to_remove or not user_to_remove.is_known_by(current_user):
            return {
                "message": "Bad request",
                "data": None,
                "error": "Bad request"
        }, 400     
        current_user.knows.remove(user_to_remove)
        db.session.add(current_user)
        db.session.commit()
        return {"message": "Removed contact successfully", "error": None, "data": contact_id}, 200


api.add_resource(ContactListAPI, '/users/<int:id>/contacts', endpoint='contacts_list')
api.add_resource(ContactAPI, '/users/<int:id>/contacts/<int:contact_id>', endpoint='contacts')