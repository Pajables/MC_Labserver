import os
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from . import synthesis_planner

db = SQLAlchemy()
synth_planner = synthesis_planner.SynthesisPlanner(['azo_synthesis'])

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    app_root = os.path.dirname(os.path.abspath(__file__))
    app.config['UPLOAD_FOLDER'] = os.path.join(app_root, 'static/uploads')
    app.config['PROTOCOL_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'reaction_protocols')
    app.config['REACTION_IMAGE_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'reaction_images')
    app.config['SENT_FILES_FOLDER'] = os.path.join(app_root, 'static/sent_files')
    db.init_app(app)

    with app.app_context():
        db.Model.metadata.reflect(db.engine)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .auth import auth
    app.register_blueprint(auth)

    from .general import general
    app.register_blueprint(general)

    from .robots_api import robots_api
    app.register_blueprint(robots_api, url_prefix='/robots_api')

    return app
