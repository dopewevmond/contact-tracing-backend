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

class TestingCenterListAPI(Resource):
    def get(self):
        """
        Returns all testing centers
        """
        centers = TestingCenter.query.all()
        return marshal(centers, testing_center_fields), 200

    def post(self):
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
            abort(400)
        
        testing_center = TestingCenter(name=name, region=region, constituency=constituency)
        db.session.add(testing_center)
        db.session.commit()
        return {"message": "Added testing center successfully", "error": None, "data": {"id": testing_center.id}}


class TestingCenterAPI(Resource):
    def get(self, id):
        center = TestingCenter.query.get(id)
        if not center:
            abort(404)
        return marshal(center, testing_center_fields)

    def put(self, id):
        center = TestingCenter.query.get(id)
        if not center:
            abort(404)

        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str, help='Name of testing center missing', location='json')
        self.reqparse.add_argument('region', type=str, help='Region of testing center is missing', location='json')
        self.reqparse.add_argument('constituency', type=str, help='Constituency of testing center is missing', location='json')
        args = self.reqparse.parse_args()
        name, region, constituency = args['name'], args['region'], args['constituency']

        try:
            if name:
                center.name = name
            if region:
                center.region = region
            if constituency:
                center.constituency = constituency
            db.session.add(center)
            db.session.commit()

            return {"message": "Updated successfully", "error": None, "data": {"id": center.id}}

        except Exception as e:
            return {
                "error": "Something went wrong1",
                "message": str(e)
            }, 500

    def delete(self, id):
        center = TestingCenter.query.get(id)
        if not center:
            abort(404)
        db.session.delete(center)
        db.session.commit()
        return {"message": "Deleted successfully", "error": None, "data": None}
        


class SearchTestingCenterAPI(Resource):
    def get(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('region', type=str, required=True, help='Add region to search for testing center', location='json')
        args = self.reqparse.parse_args()
        
        region = args['region']
        if not region:
            abort(400)
        
        return marshal(TestingCenter.search_by_region(region).all(), testing_center_fields)


api.add_resource(TestingCenterListAPI, '/testing-centers', endpoint='testing_center_list')
api.add_resource(TestingCenterAPI, '/testing-centers/<int:id>', endpoint='testing_centers')
api.add_resource(SearchTestingCenterAPI, '/search-testing-center', endpoint='search_testing_center')
