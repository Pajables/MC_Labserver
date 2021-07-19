from flask_login import UserMixin
from . import db


class User(UserMixin, db.model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Robot(db.model):
    robot_id = db.Column(db.Integer, primary_key=True)
    robot_name = db.Column(db.String(100), unique=True)
    robot_psk = db.Column(db.String(100))
