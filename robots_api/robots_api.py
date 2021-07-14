from flask import Blueprint
from .. import db


robots_api = Blueprint("robots_api", __name__)


@robots_api.route("/")
def index():
    return render_template()