from .utils import split_results
from flask import Blueprint, render_template, url_for, request, redirect
from flask_login import login_required, current_user
from . import db

general = Blueprint('general', __name__, template_folder='general/templates')


@general.route('/')
def landing():
    if current_user.is_active:
        return redirect(url_for("general.index"))
    else:
        return render_template("general/landing.html")


@general.route('/index')
@login_required
def index():
    if current_user.ADMIN == 1:
        return render_template('general/index_admin.html')
    else:
        return render_template('general/index.html')


@general.route("/display_robots", methods=["GET", 'POST'])
@login_required
def display_robots():
    # Get robots from database and display in a table
    robots_data = db.session.execute("""SELECT ROBOT_NAME, IP_ADDRESS, ROBOT_STATUS, CURRENT_JOB, LAST_UPDATE_DATE FROM
                                     Robots""")

    if request.method == "GET":
        return render_template('general/robots_display.html', robots_data=robots_data)


@general.route("/reactions", methods=['GET', 'POST'])
@login_required
def reactions():
    # Get reactions from database and display in a table
    reactions_data = db.session.execute("""SELECT ROBOT_NAME, REACTION_NAME, REACTION_STATUS, LAST_UPDATE_DATE, 
    JOB_COMPLETION_DATE FROM Reactions ORDER BY LAST_UPDATE_DATE DESC""")
    num_pages = request.args.get('num_pages')
    if num_pages is None:
        num_pages = 20
    pages_data, pages = split_results(reactions_data, num_pages)
    if request.method == 'GET':
        page_nr = request.args.get('page_nr')
        if page_nr is None:
            page_nr = 0
        else:
            page_nr = int(page_nr)
        return render_template('general/reactions_status.html', reactions_data=pages_data[page_nr], cur_page=page_nr,
                               num_pages=pages)


@general.route("/reactions/display", methods=['GET', 'POST'])
@login_required
def reactions_display():
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


@general.route("/add_reaction", methods=['GET', 'POST'])
@login_required
def add_reaction():
    if request.method == "GET":
        return render_template('general/add_reaction.html')


@general.route("/queue_reaction", methods=['GET', 'POST'])
@login_required
def queue_reaction():
    if request.method == "GET":
        return render_template('general/queue_reaction.html')