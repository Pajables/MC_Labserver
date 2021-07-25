# import db_retrieve
from flask import Blueprint, render_template, url_for, request
from flask_login import login_required, current_user
from . import db

# file to hold general pages not requiring a login.

general = Blueprint('general', __name__, template_folder='general/templates')


@general.route('/')
def index():
    return render_template("general/index.html")


@general.route("/robots", methods=["GET", 'POST'])
@login_required
def robots_display():
    # Get robots from database and display in a table
    robots_data = db.session.execute("SELECT * FROM Robot_Status")

    if request.method == "GET":
        return render_template('general/robots_display.html', robots_data=robots_data)
        # render a template using robots_list


@general.route("/reactions", methods=['GET', 'POST'])
@login_required
def reactions_display():
    # Get reactions from database and display in a table
    reactions_data = db.session.execute("SELECT * FROM Reaction_Status")

    if request.method == 'GET':
        # todo create a reactions.html file and code for the arrangement of styles for the main page(__init__.py)
        return render_template('general/reactions.html', reactions_data=reactions_data)
        # render a template using reactions_list
        # show links to specific reaction tables


@general.route("/reactions/display", methods=['GET', 'POST'])
@login_required
def reaction_table_display():
    # display only entries from specific reaction
    reaction_data = db.session.execute("SELECT * FROM REACTION_STATUS WHERE REACTION_NAME = 'Aspirin Synthesis' AND REACTION_STATUS ='COMPLETE'")

    if request.method == 'POST':
        # todo create a reactions/display.html file and code for the arrangement of styles for the main page(__init__.py)
        return render_template('general/reaction_params.html', reaction_data=reaction_data)

