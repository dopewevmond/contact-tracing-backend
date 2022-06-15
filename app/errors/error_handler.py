from app import db
from app.errors import bp

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return {"message": str(error), "data": None, "error": "Internal server error"}, 500

@bp.app_errorhandler(400)
def not_found_error(error):
    return {"message": str(error), "data": None, "error": "Bad request"}, 400

@bp.app_errorhandler(401)
def not_found_error(error):
    return {"message": str(error), "data": None, "error": "Unauthorized to access this resource or perform this action"}, 401

@bp.app_errorhandler(404)
def not_found_error(error):
    return {"message": str(error), "data": None, "error": "Not found"}, 404