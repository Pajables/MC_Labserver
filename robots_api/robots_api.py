from flask import Blueprint
from .. import db


robots_api = Blueprint("robots_api", __name__)


@robots_api.route("/", methods=["GET", "POST"])
def index():
    # GET: server responds with synthesis steps

