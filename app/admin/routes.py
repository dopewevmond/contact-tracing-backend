from . import bp
from app import db
from app.auth.routes import admin_access_required
from flask_restful import Api, Resource, abort, reqparse, fields, marshal
from app.models import User, TestingCenter


api = Api(bp)

testing_center_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'region': fields.String,
    'constituency': fields.String
}
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
    'id_type': fields.String,
    'id_number': fields.String
}

class TestingCenterListAPI(Resource):
    decorators = [admin_access_required]

    # TESTED
    def get(self, current_user):
        """
        Returns all testing centers
        """
        centers = TestingCenter.query.all()
        return marshal(centers, testing_center_fields), 200

    # TESTED
    def post(self, current_user):
        """
        Allow admins to add a new testing center
        """
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, required=True, help='Name of testing center missing', location='json')
        self.reqparse.add_argument('region', type=str, required=True, help='Region of testing center is missing', location='json')
        self.reqparse.add_argument('constituency', type=str, required=True, help='Constituency of testing center is missing', location='json')
        args = self.reqparse.parse_args()

        name, region, constituency = args['name'], args['region'], args['constituency']
        if not name or not region or not constituency:
            abort(400, error='Bad request', message='Bad request')
        
        success = True
        try:
            testing_center = TestingCenter(name=name, region=region, constituency=constituency)
            db.session.add(testing_center)
            db.session.flush()
            testing_center_id = testing_center.id
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            success = False
        finally:
            db.session.close()
        if not success:
            abort(400, error='Bad request', message='Bad request')
        return {"message": "Added testing center successfully", "error": None, "data": {"id": testing_center_id}}, 201


class TestingCenterAPI(Resource):
    decorators = [admin_access_required]

    # TESTED
    def get(self, current_user, id):
        center = TestingCenter.query.get(id)
        if not center:
            abort(404, error='Not found', message='Not found')
        return marshal(center, testing_center_fields)


    # TESTED
    def patch(self, current_user, id):
        center = TestingCenter.query.get(id)
        if not center:
            abort(404, error='Not found', message='Not found')
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, help='Name of testing center missing', location='json')
        self.reqparse.add_argument('region', type=str, help='Region of testing center is missing', location='json')
        self.reqparse.add_argument('constituency', type=str, help='Constituency of testing center is missing', location='json')
        args = self.reqparse.parse_args()

        success = True
        try:
            for key, value in args.items():
                if value:
                    setattr(center, key, value)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            success = False
        finally:
            db.session.close()
        if not success:
            abort(400, error='Bad request', message='Bad request')
        return {"message": "Updated successfully", "error": None, "data": {"id": id}}, 200


    # TESTED
    def delete(self, current_user, id):
        center = TestingCenter.query.get(id)
        if not center:
            abort(404, error='Not found', message='Not found')

        success = True
        try:
            db.session.delete(center)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            success = False
        finally:
            db.session.close()
        if not success:
            abort(400, error='Bad request', message='Bad request')
        return {"message": "Deleted successfully", "error": None, "data": None}


class VerifyUserAPI(Resource):
    decorators = [admin_access_required]

    # TESTED
    def get(self, current_user, id):
        user = User.query.get(id)
        user_data = marshal(user, user_fields)
        user_data['verif_image_link'] = user.image_link_for_verification
        return {"message": "User data found", "data": user_data}

    # TESTED
    def post(self, current_user, id):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('correct_user_creds', type=bool, required=True, help='User verification eligibilty status missing', location='json')
        args = self.reqparse.parse_args()
        correct_user_creds = args['correct_user_creds']
        if not correct_user_creds:
            abort(400, error='Bad request', message='Bad request')
        
        success = True
        try:
            user = User.query.get(id)
            if not user:
                abort(404, error='Not found', message='Not found')
            if correct_user_creds:
                user.is_verified = True
            user.revoke_verification_request()
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            success = False
        finally:
            db.session.close()
        if not success:
            abort(400, error='Bad request', message='Bad request')
        return {"message": "User verified successfully", "error": None, "data": {"id": id}}, 200

api.add_resource(TestingCenterListAPI, '/testing-centers', endpoint='testing_center_list')
api.add_resource(TestingCenterAPI, '/testing-centers/<int:id>', endpoint='testing_centers')
api.add_resource(VerifyUserAPI, '/verify-user/<int:id>', endpoint='verify_user')