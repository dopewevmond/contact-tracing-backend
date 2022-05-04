from app.auth import bp
from app.models import User
from flask import jsonify, make_response, request, current_app
from functools import wraps
import jwt
from app import db


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None

        if 'x-access-tokens' in request.headers:
            token = request.headers['x-access-tokens']
        
        if not token:
            return jsonify({"message": "a valid token is missing"})

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if current_user is None:
                return make_response(jsonify({
                    "message": "Invalid Authentication token",
                    "data": None,
                    "error": "Unauthorized"
                }), 401)
        except:
            return make_response(jsonify({
                "message": "Invalid Authentication token",
                "data": None,
                "error": "Unauthorized"
            }), 401)
        return f(current_user, *args, **kwargs)
    return decorator


@bp.route('/login', methods=['POST'])
def login():
    """
    Accepts a username and password in the body of the request.
    Format should be json.
    Regardless of whether an email or a username is being used to sign in,
    still pass it as the value of the username key.
    """
    try:
        data = request.json
        if not data:
            return make_response(jsonify({
                "message": "Please provide login credentials",
                "data": None,
                "error": "Bad request"
            }), 400)
        user = User.query.filter_by(username=data['username']).first() or User.query.filter_by(email=data['username']).first()
        if user:    
            user_credentials = user.verify_password(data['password'])
        if user_credentials:
            try:
                token = jwt.encode(
                    {"user_id": user.id},
                    current_app.config['SECRET_KEY'],
                    algorithm='HS256'
                )
                return jsonify({
                    "message": "Successfully fetched auth token",
                    "data": token
                })
            except Exception as e:
                return make_response(jsonify({
                    "error": "Something went wrong1",
                    "message": str(e)
                }), 500)
        return make_response(jsonify({
            "message": "Error fetching auth token! invalid username or password",
            "data": None,
            "error": "Unauthorized"
        }), 404)


    except Exception as e:
        return make_response(jsonify({
            "message": "Something went wrong2",
            "error": str(e),
            "data": None
        }), 500)


@bp.route('/signup', methods=['POST'])
def signup():
    """
    Accepts an email and password in the body of the request.
    Format should be json.
    """
    try:
        user = request.json
        # credentials were not found in body of the request as json
        if not user:
            return make_response(jsonify({
                "message": "Please provide user details",
                "data": None,
                "error": "Bad request"
            }), 400)
        
        already_exists = User.query.filter_by(email=user['email']).first()
        if already_exists:
            return make_response(jsonify({
                "message": "User already exists",
                "data": None,
                "error": "Bad request"
            }), 400)
        new_user = User(email=user['email'])
        new_user.hash_password(user['password'])
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({
            "message": "Successfully created new user",
            "data": {"id": new_user.id}
        }), 201)
    except Exception as e:
        return make_response(jsonify({
            "message": "Something went wrong1",
            "error": str(e),
            "data": None
        }), 500)
