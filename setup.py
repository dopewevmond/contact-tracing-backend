from app import create_app, db
from app.models import User, Location, Test, TestingCenter, Visited

app = create_app()
@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Location': Location, 'Test': Test, 'TestingCenter': TestingCenter, 'Visited': Visited}