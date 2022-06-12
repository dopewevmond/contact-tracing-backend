from app.dummy import bp
from flask_restful import Api, Resource, reqparse
from flask_mail import Message
from flask import current_app
from app import mail

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
        msg = Message('Subject Line', sender=current_app.config['MAIL_USERNAME'], recipients=['dopewevmond@gmail.com'])
        msg.body = 'This is the body of the email'
        mail.send(msg)
        return "Mail sent"


api.add_resource(MyTest, '/dummy', endpoint='dummy')
api.add_resource(SendEmail, '/email', endpoint='send_email')