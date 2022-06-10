from app.dummy import bp
from flask_restful import Api, Resource, reqparse

api = Api(bp)

class MyTest(Resource):
    def post(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('lon', type=str, required=True, help='longitude of location to search not provided', location='json')
        args = self.reqparse.parse_args()
        print(args)

        return {"data": args['lon']}

api.add_resource(MyTest, '/dummy', endpoint='dummy')