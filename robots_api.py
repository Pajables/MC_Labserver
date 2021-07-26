from flask import Blueprint, request
from werkzeug.security import check_password_hash
from . import db


robots_api = Blueprint("robots_api", __name__)


def robot_login_required():
    # check hash of supplied robot key
    pass


# todo set up @robot_login_required
@robots_api.route("/", methods=["GET", "POST"])
def index():
    # GET: server responds with synthesis steps - calls synthesis planner
    # POST: server updates relevant tables (robot_status, reaction_status, etc)
    return "Hi there!"
