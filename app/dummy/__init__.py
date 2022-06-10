from flask import Blueprint

bp = Blueprint('dummy', __name__)

from . import routes