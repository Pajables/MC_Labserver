from flask_login import UserMixin
from . import db

# each table in the database needs a class to be created for it
# db.model is required - don't change it
# identify all columns by name and data type


class User(UserMixin, db.Model):
    __table__ = db.Model.metadata.tables['Users']

    def get_id(self):
        return self.USER_ID


class Robots(db.Model):
    __table__ = db.Model.metadata.tables['Robots']


class ReactionStatus(db.Model):
    __table__ = db.Model.metadata.tables['Reactions_Status']


class Reactions(db.Model):
    __table__ = db.Model.metadata.tables['Reactions']


class RobotQueue(db.Model):
    __table__ = db.Model.metadata.tables['Robot_Queue']


# todo add RobotQueue model
# RobotQueue will be a table that holds references to files containing synthesis steps.
# For now those files will be JSON, but in the future they will be XDL.
# When a robot sends a GET request to the server, the server will check the queue table to see what the
# earliest (MIN(QUEUE_NUM)) entry for that ROBOT_ID is. If a record is found, the app must delete that
# record from the table after retrieving it.
#  on that, the flask app will look for the
# FILE_NAME in the filesystem and send that file to the robot.
# COL 1: ROBOT_ID, COL2: QUEUE_NUM, COL3: FILE_NAME
