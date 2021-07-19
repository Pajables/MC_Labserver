# import db_retrieve
from flask import Blueprint, render_template, url_for, request
from flask_login import login_required, current_user

# file to hold general pages not requiring a login.

general = Blueprint('general', __name__)


@general.route('/')
def index():
    return render_template("general/index.html")


@general.route("/robots", methods=["GET", 'POST'])
@login_required
def robots_display():
    # todo get robots from database and display in a table
    if request.method == "GET":
        # robots_list = robots_update()
        # render a template using robots_list


@general.route("/reactions", methods=['GET', 'POST'])
@login_required
def reactions_display():
    # todo get reactions from database and display in a table.
    if request.method = 'GET':
        # reactions_list = reactions_update()
        # render a template using reactions_list
        # show links to specific reaction tables

@general.route("/reactions/display", methods=['GET', 'POST'])
@login_required
def reaction_table_display():
    pass
    # display only entries from specific reaction
