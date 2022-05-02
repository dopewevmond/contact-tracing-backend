from . import bp
from flask import render_template, flash, redirect, url_for, jsonify, current_app
from ..models import User

@bp.route('/')
def index():
    a = User.query.all()
    ht = '<ul>'
    for user in a:
        ht += "<li>{}, {} </li>".format(user.first_name, user.last_name)
    ht += '</ul>'
    return ht