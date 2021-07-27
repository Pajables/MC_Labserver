from flask_login import UserMixin
from . import db

# each table in the database needs a class to be created for it
# db.model is required - don't change it
# identify all columns by name and data type


class User(UserMixin, db.Model):
    __table__ = db.Model.metadata.tables['Users']

    def get_id(self):
        return self.USER_ID

class RobotStatus(db.Model):
    __table__ = db.Model.metadata.tables['Robot_Status']


class ReactionStatus(db.Model):
    __table__ = db.Model.metadata.tables['Reaction_Status']


class ReactionParameters(db.Model):
    __table__ = db.Model.metadata.tables['Reaction_Parameters']


class UJRobotsCommunication(db.Model):
    __table__ = db.Model.metadata.tables['UJ_Robots_Communication']

# robots model for connection and authentication
class Robots(db.model):
    __table__ = db.Model.metadata.tables['Robots']
