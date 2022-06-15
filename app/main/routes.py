from . import bp
from ..models import Location, TestingCenter, User, Test, risk_people_emails
from flask_restful import Api, Resource, abort, reqparse, fields, marshal_with, marshal
from app.auth.routes import token_required, admin_access_required
from app import db
from datetime import datetime
from flask import current_app
from app.email import send_email

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
user_fields_min =  {
    'id': fields.Integer,
    'first_name': fields.String,
    'last_name': fields.String,
    'username': fields.String
}
visited_fields = {
    'location_name': fields.String,
    'date_visited': fields.String
}

location_fields = {
    'id': fields.Integer,
    'latitude': fields.Float,
    'longitude': fields.Float,
    'location_name': fields.String
}
test_fields = {
    'id': fields.Integer,
    'date': fields.DateTime,
    'location': fields.String
}
testing_center_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'region': fields.String,
    'constituency': fields.String
}

class TestListAPI(Resource):
    """/users/{id}/tests - tests_list"""
    decorators = [token_required]

    def get(self, current_user, id):
        if not current_user.id == id and not current_user.is_admin:
            abort(401, error='Unauthorized', message='User is unauthorized to perform this action')
        tests = Test.query.filter_by(user_id = id).all()      
        deserialized = []
        for test in tests:
            test_obj = {"id": test.id, "date": test.date, "location": test.location.name}
            deserialized.append(test_obj)
        return marshal(deserialized, test_fields)

    def post(self, current_user, id):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('testing_center_id', type=int, required=True, help='ID of testing center missing', location='json')
        self.reqparse.add_argument('is_positive', type=str, required=True, help='Add value for is_positive. either true or false', location='json')
        self.reqparse.add_argument('is_asymptomatic', type=str, required=True, help='Add value for is_positive. either true or false', location='json')
        args = self.reqparse.parse_args()
        center_id, is_pos, is_asymp = args['testing_center_id'], args['is_positive'], args['is_asymptomatic']
        if not center_id or not is_pos or not is_asymp or is_pos not in ['true', 'false'] or is_asymp not in ['true', 'false']:
            abort(400, error='Bad request', message='Bad request')
        if not current_user.id == id and not current_user.is_admin:
            abort(401, error='Unauthorized', message='User is unauthorized to perform this action')
        is_pos, is_asymp = is_pos == "true", is_asymp == "true"
        try:
            new_test = Test(is_positive=is_pos, is_asymptomatic=is_asymp, user_id=id, testing_center_id=center_id)
            db.session.add(new_test)
            db.session.commit()
            
            # CONTACT TRACING ALGORITHM
            # TO NOTIFY ALL CLOSE CONTACTS
            # AND USERS WHO VISITED THE
            # SAME LOCATIONS ON THE SAME
            # DAY AS THE USER WHO JUST TESTED POSITIVE

            if new_test.is_positive:
                user_tested_positive = User.query.get(id)
                # getting emails of the user's close contacts
                emails_of_contacts = user_tested_positive.get_all_close_contacts_emails()
                # getting emails of people who visited locations the same day as the users. this method returns a set
                people_at_risk = risk_people_emails(user_id=user_tested_positive.id, user_email=user_tested_positive.email)

                # combining the two into a single list so that the email can be sent to the users
                emails_of_contacts = [*emails_of_contacts, *people_at_risk]

                if emails_of_contacts:
                    txt_body = f"This is an alert email from a contact tracing app. A close contact of yours\
                        or someone whom you might have come in contact with has contracted covid. Please self isolate and\
                        get tested too as you might be at risk. This email was sent on {datetime.utcnow().year}-{datetime.utcnow().month}-{datetime.utcnow().day}."
                    html_body = f'<p>{txt_body}</p>'
                    first_email = emails_of_contacts[0]
                    rest_of_emails = emails_of_contacts[1:] if len(emails_of_contacts) > 1 else None

                    # since we want to send the emails with bcc so that the recipients will not find out
                    # who else received an email. for privacy and security reasons

                    send_email(subject='RISK OF COVID',
                        sender=('Contact Tracing App', current_app.config['MAIL_USERNAME']),
                        recipients=[first_email],
                        bcc=rest_of_emails,
                        text_body=txt_body,
                        html_body=html_body)

        except Exception as e:
            print(e)
            db.session.rollback()
            abort(500, error='Internal server error', message='Something went wrong')
        finally:
            db.session.close()
        return {"message": "Added test successfully and contacts notified if test was positive", "error": None, "data": {"id": new_test.id}}, 200


class ContactListAPI(Resource):
    """/users/{id}/contacts - contacts_list"""
    decorators = [token_required]    

    def get(self, current_user, id):
        if not current_user.id == id:
            abort(401, error='Unauthorized', message='User is unauthorized to perform this action')
        user = User.query.get(id)
        contacts = user.knows.all()
        return marshal(contacts, user_fields)
        


    def post(self, current_user, id):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('contact_id', type=int, help='ID of user to add was not found', location='json')
        args = self.reqparse.parse_args()
        contact_id = args['contact_id']
        if contact_id is None:
            abort(400, error='Bad request', message='Bad request')
        if not current_user.id == id:
            abort(401, error='Unauthorized', message='User is unauthorized to perform this action')
        user_to_add_to_contacts = User.query.get(contact_id)
        if not user_to_add_to_contacts or user_to_add_to_contacts.is_known_by(current_user):
            abort(400, error='Bad request', message='Bad request')
        try:
            current_user.knows.append(user_to_add_to_contacts)
            db.session.add(current_user)
            db.session.commit()
        except Exception as e:
            print(e)
            abort(500, error='Internal server error', message='Something went wrong')
        finally:
            db.session.close()
        return {"message": "Added contact successfully", "error": None, "data": {"id": contact_id}}, 200


class ContactAPI(Resource):
    """/users/{id}/contacts/{contact_id} - contact"""
    decorators = [token_required]

    def delete(self, current_user, id, contact_id):
        if not current_user.id == id:
            abort(401, error='Unauthorized', message='User is unauthorized to perform this action')
        user_to_remove = User.query.get(contact_id)
        if not user_to_remove or not user_to_remove.is_known_by(current_user):
            abort(400, error='Bad request', message='Bad request')
        try:
            current_user.knows.remove(user_to_remove)
            db.session.add(current_user)
            db.session.commit()
        except Exception as e:
            print(e)
            abort(500, error='Internal server error', message='Something went wrong')
        finally:
            db.session.close()
        return {"message": "Removed contact successfully", "error": None, "data": None}, 200


class VisitedListAPI(Resource):
    """/users/{id}/visited - visited_list"""
    decorators = [token_required]

    def get(self, current_user, id):
        if not current_user.id == id:    
            abort(401, error='Unauthorized', message='User is unauthorized to perform this action')
        visited_locations = current_user.visited_locations().all()
        return marshal(visited_locations, visited_fields), 200

    def post(self, current_user, id):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('location_id', type=int, required=True, help='ID of location to add', location='json')
        args = self.reqparse.parse_args()
        location_id = args['location_id']
        if location_id is None:
            abort(400, error='Bad request', message='Bad request')
        if not current_user.id == id:
            abort(401, error='Unauthorized', message='User is unauthorized to perform this action')
        try:
            location_to_add = Location.query.get(location_id)
            current_user.visits.append(location_to_add)
            db.session.add(current_user)
            db.session.commit()
            # datetime_of_visit = db.session.query()
        except Exception as e:
            abort(500, error='Internal server error', message='Something went wrong. The location may have been deleted')
        finally:
            db.session.close()
        return {"message": "Successfully added location to history", "error": None, "data": {"id": location_id}}, 200


class VisitedAPI(Resource):
    """/users/{id}/visited/{location_id} - visited"""
    decorators = [token_required]

    def delete(self, current_user, id, location_id):
        if not current_user.id == id:
            abort(401, error='Unauthorized', message='User is unauthorized to perform this action')
        location_to_remove = Location.query.get(location_id)
        if not location_to_remove or not current_user in location_to_remove.wasvisitedby:
            abort(400, error='Bad request', message='Bad request')
        try:
            current_user.visits.remove(location_to_remove)
            db.session.add(current_user)
            db.session.commit()
        except Exception as e:
            print(e)
            abort(400, error='Bad request', message='Bad request')
        finally:
            db.session.close()
        return {"message": "Removed location successfully", "error": None, "data": {"id": location_id}}, 200


class SearchLocationAPI(Resource):
    """/locations/search-by-lat-lon - search_by_text"""
    def get(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('lat', type=str, required=True, help='latitude of location to search not provided', location='args')
        self.reqparse.add_argument('lon', type=str, required=True, help='longitude of location to search not provided', location='args')
        args = self.reqparse.parse_args()
        if not args['lat'] or not args['lon']:
            abort(400, error='Bad request', message='Bad request')
        latitude, longitude = args['lat'], args['lon']
        location = Location.query.filter_by(longitude=float(longitude)).filter_by(latitude=float(latitude)).first()
        if location is None:
            abort(404, error='Not found', message='Not found')
        return {"message": "Location found", "data": {"id": location.id}, "error": None}, 200


class LocationListAPI(Resource):
    """/locations/all"""
    def get(self):
        locations = Location.query.all()
        return {"message": "Locations found", "data": marshal(locations, location_fields), "error": None}, 200

    @token_required
    def post(self, current_user):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('lat', type=str, required=True, help='Latitude of location not provided', location='json')
        self.reqparse.add_argument('lon', type=str, required=True, help='Longitude of location not provided', location='json')
        self.reqparse.add_argument('name', type=str, required=True, help='Name of location not provided', location='json')
        args = self.reqparse.parse_args()
        if not args['lat'] or not args['lon'] or not args['name']:
            abort(400, error='Bad request', message='Bad request')
        try:
            lat, lon, name = float(args['lat']), float(args['lon']), args['name']
            if Location.search_by_lat_and_lon(lat, lon).count() > 0:
                abort(400, error='Bad request', message='Bad request')
            location = Location(latitude=lat, longitude=lon, location_name=name)
            db.session.add(location)
            db.session.commit()
        except Exception as e:
            print(e)
            abort(400, error='Bad request', message='Bad request')
        finally:
            db.session.close()
        return {"message": "Location added successfully", "data": {"id": location.id}, "error": None}, 200


class UserAPI(Resource):
    """/users/{id}/edit-profile - edit_profile"""
    decorators = [token_required]
    def get(self, current_user, id):
        if not current_user.id == id:
            abort(401, error='Unauthorized', message='User is unauthorized to perform this action')
        user = User.query.get(id)
        if not user:
            abort(404, error='Not found', message='Not found')
        return {"message": "User found", "error": None, "data": marshal(user, user_fields)}

    
    def put(self, current_user, id):
        if not current_user.id == id or current_user.is_verified:
            abort(401, error='Unauthorized', message='User is unauthorized to perform this action')
        user = User.query.get(id)
        if not user:
            abort(404, error='Not found', message='Not found')
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('first_name', type=str, help='Provide a valid first name', location='json')
        self.reqparse.add_argument('other_names', type=str, help='Provide a valid middle name', location='json')
        self.reqparse.add_argument('last_name', type=str, help='Provide a valid last name', location='json')
        self.reqparse.add_argument('gender', type=str, help='Select a gender', location='json')
        self.reqparse.add_argument('dob', type=str, help='Provide a date of birth', location='json')
        self.reqparse.add_argument('username', type=str, help='Provide a valid username', location='json')
        self.reqparse.add_argument('phone_number', type=str, help='Provide a phone number', location='json')
        args = self.reqparse.parse_args()
        try:
            # the gender and dob fields need to be modified a bit before they can ...
            # ... be applied to the user object
            if args['gender'] and args['gender'].lower() in ['m', 'f']:
                user.gender = args['gender'].lower() == 'm'
            if args['dob']:
                datetime_obj = datetime.strptime(args['dob'], '%Y-%m-%dT%H:%M:%S.%fZ')
                user.dob = datetime_obj
            for key, value in args.items():
                if value and key != 'gender' and key != 'dob':
                    user.__setattr__(key, value)
            db.session.add(user)
            db.session.commit()
            return {
                "message": "User profile edited successfully",
                "data": {"id": user.id},
                "error": None
            }, 200
        except Exception as e:
            print(e)
            abort(500, error='Internal server error', message='Something went wrong')
        finally:
            db.session.close()


class SearchUserAPI(Resource):
    """/users/search - search_users"""
    def get(self):
        try:
            self.reqparse = reqparse.RequestParser()
            self.reqparse.add_argument('q', type=str, required=True, help='Type in a name or username of a user to search', location='args')
            args = self.reqparse.parse_args()
            user_details = args['q']
            found_users, total = User.search(user_details, 1, current_app.config['USERS_PER_PAGE'])
            found_users = found_users.all()
            if total > 0:
                return {"message": "Users found", "error": None, "data": {"count": total, "users": marshal(found_users, user_fields_min)}}, 200
            return {"message": "No users found", "error": None, "data": {"count": total, "users": []}}, 200
        except Exception as e:
            abort(400, error='Bad request', message='Bad request')
        finally:
            db.session.close()

class SearchTestingCenterAPI(Resource):
    """/testing-centers/search - search_testing_centers"""
    def get(self):
        try:
            self.reqparse = reqparse.RequestParser()
            self.reqparse.add_argument('q', type=str, required=True, help='Type in the name of the testing center to search', location='args')
            args = self.reqparse.parse_args()
            testing_center_details = args['q']
            found_testing_centers, total = TestingCenter.search(testing_center_details, 1, current_app.config['USERS_PER_PAGE'])
            found_testing_centers = found_testing_centers.all()
            if total > 0:
                return {"message": "Testing centers found", "error": None, "data": {"count": total, "testing_centers": marshal(found_testing_centers, testing_center_fields)}}, 200
            return {"message": "No testing centers found", "error": None, "data": {"count": total, "testing_centers": []}}, 200
        except Exception as e:
            abort(400, error='Bad request', message='Bad request')
        finally:
            db.session.close()

api.add_resource(ContactListAPI, '/users/<int:id>/contacts', endpoint='contacts_list')
api.add_resource(ContactAPI, '/users/<int:id>/contacts/<int:contact_id>', endpoint='contact')
api.add_resource(VisitedListAPI, '/users/<int:id>/visited', endpoint='visited_list')
api.add_resource(VisitedAPI, '/users/<int:id>/visited/<int:location_id>', endpoint='visited')
api.add_resource(SearchLocationAPI, '/locations/search-by-lat-lon', endpoint='search_locations')
api.add_resource(LocationListAPI, '/locations/all', endpoint='locations_list')
api.add_resource(TestListAPI, '/users/<int:id>/tests', endpoint='tests_list')
api.add_resource(UserAPI, '/users/<int:id>/edit-profile', endpoint='edit_profile')
api.add_resource(SearchUserAPI, '/users/search', endpoint='search_users')
api.add_resource(SearchTestingCenterAPI, '/testing-centers/search', endpoint='search_testing_centers')