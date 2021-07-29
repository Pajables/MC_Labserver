from flask import Blueprint, request
from functools import wraps
from werkzeug.security import check_password_hash
from . import db
from .models import Robots


robots_api = Blueprint("robots_api", __name__)


def check_robot_login(func):
    # check hash of supplied robot key
    @wraps(func)
    def verify_robot(*args, **kwargs):
        robot_id = request.args[0]
        robot_key = request.args[1]
        robot = Robots.query.filter_by(ROBOT_ID=robot_id).first()
        if robot and check_password_hash(robot.ROBOT_KEY, robot_key):
            return func(*args, **kwargs)
    return verify_robot


@robots_api.route("/", methods=["GET", "POST"])
def index():
    # GET: server responds with synthesis steps - calls synthesis planner
    # POST: server updates relevant tables (robot_status, reaction_status, etc)
    return "Hi there!"
