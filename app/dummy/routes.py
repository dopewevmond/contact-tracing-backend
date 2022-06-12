from app.dummy import bp
from flask_restful import Api, Resource, reqparse
from app.email import send_email
from flask import current_app

api = Api(bp)

class MyTest(Resource):
    def post(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('lon', type=str, required=True, help='longitude of location to search not provided', location='json')
        args = self.reqparse.parse_args()
        print(args)

        return {"data": args['lon']}

class SendEmail(Resource):
    def get(self):
        txt_body = "This is a test email from the Flask server"
        html_body = f'<p>{txt_body}</p>'
        send_email(subject='TEST EMAIL - CONTACT TRACING', sender=current_app.config['MAIL_USERNAME'], recipients=['klenamaj3@gmail.com'], text_body=txt_body, html_body=html_body)
        return "Mail sent"


api.add_resource(MyTest, '/dummy', endpoint='dummy')
api.add_resource(SendEmail, '/email', endpoint='send_email')