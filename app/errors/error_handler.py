from app import db
from app.errors import bp

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return {"message": str(error), "data": None, "error": "Internal server error"}, 500
