from app import app, db
from app.models import Oggetto, Location


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Oggetto': Oggetto, 'Location': Location}
