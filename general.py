# import db_retrieve
from flask import Blueprint, render_template, url_for, request
from flask_login import login_required, current_user
from . import db

general = Blueprint('general', __name__, template_folder='general/templates')


@general.route('/')
def landing():
    return render_template("general/landing.html")


@general.route('/index')
@login_required
def index():
    if current_user.ADMIN == 1:
        return render_template('general/index_admin.html')
    else:
        return render_template('general/index.html')


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
        return render_template('general/reactions_status.html', reactions_data=reactions_data)


@general.route("/add_reaction", methods=['GET', 'POST'])
@login_required
def add_reaction():
    if request.method == "GET":
        return render_template('general/add_reaction.html')


@general.route("/reactions/display", methods=['GET', 'POST'])
@login_required
def reaction_table_display():
    # display only entries from specific reaction
    reaction = request.args.get('reaction_name')
    all_reactions = db.session.execute("SELECT REACTION_NAME FROM Reaction_Status")
    all_reactions = set(all_reactions)
    if reaction is None:
        return render_template('general/reaction.html', all_reactions=all_reactions)
    else:
        columns = db.session.execute(f"SHOW COLUMNS FROM {reaction}")
        specific_reaction = db.session.execute(f"SELECT * FROM {reaction}")
        return render_template('general/reaction.html', all_reactions=all_reactions, reaction_table=specific_reaction,
                               columns=columns)

