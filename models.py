from flask_login import UserMixin
from . import db

# each table in the database needs a class to be created for it
# db.model is required - don't change it
# identify all columns by name and data type
class User(UserMixin, db.model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Robot_Status(db.model):
    robot_id = db.Column(db.String(100), primary_key=True)
    robot_name = db.Column(db.String(100), unique=True)
    ip_address = db.Column(db.String(100))
    robot_status = db.column(db.String(100))
    current_job = db.column(db.String(100))
    last_update_date = db.Column(db.String(100))

class Reaction_Status(db.model):
    robot_id = db.Column(db.String(100), primary_key=True)
    robot_name = db.Column(db.String(100), unique=True)
    reaction_name = db.Column(db.String(100))
    reaction_status = db.Column(db.String(100))
    last_update_date = db.Column(db.String(100))
    job_completion_date = db.Column(db.String(100))

class Reaction_Parameters(db.model):
    reaction_name = db.Column(db.String(100))
    robot_id = db.Column(db.String(100), primary_key=True)
    robot_name = db.Column(db.String(100), unique=True)
    parm1 = db.Column(db.String(100))
    parm1_value = db.column(db.String(100))
    last_update_date = db.Column(db.String(100))

class UJ_Robots_Communication(db.model):
    robot_id = db.Column(db.String(100), primary_key=True)
    robot_name = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(100))
    execute = db.Column(db.Integer)
    last_update_date = db.Column(db.String(100))
