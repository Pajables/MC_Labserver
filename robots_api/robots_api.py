from flask import Blueprint, request
from werkzeug.security import check_password_hash
from . import db


robots_api = Blueprint("robots_api", __name__)


def robot_login_required():
    # check hash of supplied robot key
    @auth.verify_password
    def verify_password(username, password):
        user = User.query.filter_by(Username=username).first()
        if user and passlib.hash.sha256_crypt.verify(password, user.password_hash)
            return user

# todo set up @robot_login_required
@robots_api.route("/", methods=["GET", "POST"])
def index():
    # GET: server responds with synthesis steps - calls synthesis planner
    # POST: server updates relevant tables (robot_status, reaction_status, etc)
    return "Hi there, {}!".format(auth.username())


