from threading import Thread
from flask_mail import Message
from flask import current_app
from app import mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, bcc, text_body, html_body):
    """Send an email from the flask app in a new thread"""
    msg = Message(subject=subject, sender=sender, recipients=recipients, bcc=bcc)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()