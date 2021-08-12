from . import utils
from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_required, current_user
from sqlalchemy import exc
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
    return render_template('general/index.html')


@general.route("/robots", methods=["GET", 'POST'])
@login_required
def robots():
    # Get robots from database and display in a table
    robots_data = db.session.execute("""SELECT ROBOT_NAME, IP_ADDRESS, ROBOT_STATUS, CURRENT_JOB, LAST_UPDATE_DATE FROM
                                     Robots""")

    if request.method == "GET":
        return render_template('general/robots.html', robots_data=robots_data)


@general.route("/reactions", methods=['GET', 'POST'])
@login_required
def reactions():
    # Get reactions from database and display in a table
    reactions_data = db.session.execute("""SELECT ROBOT_NAME, REACTION_NAME, REACTION_STATUS, LAST_UPDATE_DATE, 
    JOB_COMPLETION_DATE FROM Reactions_Status ORDER BY LAST_UPDATE_DATE DESC""")
    num_pages = request.args.get('num_pages')
    if num_pages is None:
        num_pages = 20
    pages_data, pages = utils.split_results(reactions_data, num_pages)
    if request.method == 'GET':
        page_nr = request.args.get('page_nr')
        if page_nr is None:
            page_nr = 0
        else:
            page_nr = int(page_nr)
        return render_template('general/reactions_status.html', reactions_data=pages_data[page_nr], cur_page=page_nr,
                               num_pages=pages)


@general.route("/display_reactions", methods=['GET'])
@login_required
def display_reactions():
    reaction_name = request.args.get('reaction_name')
    all_reactions = utils.get_avail_reactions(db)
    if reaction_name is None:
        return render_template('general/reaction.html', all_reactions=all_reactions, sel_reaction=False)
    else:
        try:
            table_name, reaction_params = utils.get_reaction_params(db, reaction_name)
            specific_reaction = db.session.execute(f"SELECT * FROM {table_name};")
            return render_template('general/reaction.html', all_reactions=all_reactions, sel_reaction=True,
                                   reaction_name=reaction_name, reaction_params=reaction_params, reaction_table=specific_reaction)
        except exc.ProgrammingError as e:
            flash("Query failed: " + str(e))
            return redirect(url_for('general.display_reactions'))


@general.route("/add_reaction", methods=['GET', 'POST'])
@login_required
def add_reaction():
    if request.method == "GET":
        return render_template('general/reaction_add.html')
    elif request.method == "POST":
        reaction_name, parameters = utils.process_reaction_form(request.form)
        table_name = reaction_name.replace(" ", "_")
        table_name = table_name.upper()
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
        for parameter in parameters:
            sql += parameter[0] + " " + parameter[1] + ", "
        sql = sql[:-2]
        sql += ");"
        try:
            db.session.execute(sql)
            sql = f'''INSERT INTO Reactions (REACTION_NAME, TABLE_NAME) 
            VALUES ('{reaction_name}', '{table_name}');'''
            db.session.execute(sql)
            db.session.commit()
            flash(f"Successfully added table {table_name}")
            return redirect(url_for('general.add_reaction'))
        except exc.ProgrammingError as e:
            flash(f"Failed to add table {table_name}" + str(e))
            return redirect(url_for('general.add_reaction'))


@general.route("/manual_input", methods=['GET', 'POST'])
@login_required
def manual_input():
    if request.method == 'GET':
        all_reactions = utils.get_avail_reactions(db)
        if request.args['reaction-name'] is None:
            return render_template('general/reaction_manual_input.html', all_reactions=all_reactions)


@general.route("/show_queue", methods=["GET"])
@login_required
def show_queue():
    try:
        columns_data = db.session.execute("SHOW COLUMNS FROM Robot_Queue")
        columns = ["ROBOT_ID", "REACTION_NAME", "REACTION_ID", "QUEUE_NUM"]
        for num, item in enumerate(columns_data):
            if item[0] in columns:
                column = item[0]
                column = column.replace("_", " ")
                column = column.lower()
                column = column.capitalize()
                column = column.replace("id", "ID")
                columns[columns.index(item[0])] = column
        queue_items = db.session.execute("SELECT ROBOT_ID, REACTION_NAME, REACTION_ID, QUEUE_NUM FROM Robot_Queue")
        return render_template('general/queue_show.html', columns=columns, queue_items=queue_items)
    except exc.ProgrammingError as e:
        flash("Query failed: " + str(e))
        return redirect(url_for('general.index'))


@general.route("/queue_reaction", methods=['GET', 'POST'])
@login_required
def queue_reaction():
    if request.method == "GET":
        all_reactions = utils.get_avail_reactions(db)
        reaction_name = request.args.get('reaction_name')
        reaction_params = None
        if reaction_name is None:
            return render_template('general/queue_reaction.html', all_reactions=all_reactions, sel_reaction=False)
        else:
            table_name, reaction_params = utils.get_reaction_params(db, reaction_name)
            all_robots = utils.get_avail_robots(db)
            return render_template('general/queue_reaction.html', all_reactions=all_reactions, sel_reaction=True, reaction_name=reaction_name, reaction_params=reaction_params)
    elif request.method == "POST":
        utils.process_queue_form(request.form)
