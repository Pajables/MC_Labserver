from . import utils
from flask import Blueprint, render_template, url_for, request, redirect, flash
from flask_login import login_required, current_user
from sqlalchemy import exc
from . import db
from . import models

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
    if request.method == 'GET':
        # Get reactions from database and display in a table
        reactions_data = db.session.execute("""SELECT ROBOT_NAME, REACTION_NAME, REACTION_STATUS, LAST_UPDATE_DATE, 
            JOB_COMPLETION_DATE FROM Reactions_Status ORDER BY LAST_UPDATE_DATE DESC""")
        results_per_page = request.args.get('results_per_page')
        if results_per_page is None:
            results_per_page = 20
        pages_data, pages = utils.split_results(reactions_data, results_per_page)
        if not pages_data:
            return render_template('general/reactions_status.html', num_pages=0)
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
    all_reactions = [item for item in set(all_reactions)]
    if reaction_name is None:
        return render_template('general/reaction.html', all_reactions=all_reactions, sel_reaction=False)
    else:
        try:
            form_output = utils.get_reaction_params(db, reaction_name, True)
            table_name = form_output["table_name"]
            reaction_params = form_output["reaction_params"]
            results=form_output["results"]
            specific_reaction = db.session.execute(f"SELECT * FROM {table_name};")
            return render_template('general/reaction.html', all_reactions=all_reactions, sel_reaction=True,
                                   reaction_name=reaction_name, reaction_params=reaction_params, reaction_table=specific_reaction, results=results)
        except exc.ProgrammingError as e:
            flash("Query failed: " + str(e))
            return redirect(url_for('general.display_reactions'))


@general.route("/add_reaction", methods=['GET', 'POST'])
@login_required
def add_reaction():
    if request.method == "GET":
        return render_template('general/reaction_add.html')
    elif request.method == "POST": 
        form_output = utils.process_reaction_form(request.form)
        reaction_name = form_output["reaction_name"]
        parameters = form_output["reaction_parameters"]
        results = form_output["results"]
        filename = utils.upload_protocol(request)
        table_name = reaction_name.replace(" ", "_")
        table_name = table_name.upper()
        all_reactions = utils.get_avail_reactions(db)
        all_reactions = [item for item in set(all_reactions)]
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} (REACTION_ID INT, "
        for parameter in parameters:
            sql += parameter[0] + " " + parameter[1] + ", "
        for result in results:
            sql += result + ", "
        sql += "PRIMARY KEY (REACTION_ID));"
        try:
            db.session.execute(sql)
            sql = f'''INSERT INTO Reactions (REACTION_NAME, TABLE_NAME, FILE_NAME) 
            VALUES ('{reaction_name}', '{table_name}', '{filename}');'''
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
            form_output = utils.get_reaction_params(db, reaction_name, True)
            table_name = form_output["table_name"]
            reaction_params = form_output["reaction_parameters"]
            all_robots = utils.get_avail_robots(db)
            return render_template('general/queue_reaction.html', all_reactions=all_reactions, sel_reaction=True, reaction_name=reaction_name, reaction_params=reaction_params, all_robots=all_robots)
    elif request.method == "POST":
        reaction_name = request.form.get("reaction_name")
        form_output = utils.get_reaction_params(db, reaction_name, False)
        table_name = form_output["table_name"]
        reaction_params = form_output["reaction_parameters"]
        robot, parameters = utils.process_queue_form(request.form, reaction_params)
        if parameters and robot:
            try:
                reaction_id = db.session.execute(
                    f"SELECT REACTION_ID FROM {table_name} WHERE REACTION_ID=(SELECT MAX(REACTION_ID) FROM {table_name})").fetchone()
                if reaction_id is None:
                    reaction_id = 1
                else:
                    reaction_id = reaction_id[0] + 1
                queued_item = models.RobotQueue(USER_ID=current_user.USER_ID, ROBOT_ID=robot[0], REACTION_NAME=reaction_name, REACTION_ID=reaction_id)
                db.session.add(queued_item)
                sql_pre = f"INSERT INTO {table_name} ("
                sql_post = f" VALUES ("
                for i in range(len(reaction_params)):
                    sql_pre += f"{reaction_params[i]}, "
                    sql_post += f"{parameters[i]}, "
                sql_pre = sql_pre[:-2]
                sql_post = sql_post[:-2]
                sql_pre += ")"
                sql_post += ");"
                db.session.execute(sql_pre + sql_post)
                reaction_status = models.ReactionStatus(REACTION_ID=reaction_id, ROBOT_ID=robot[0], ROBOT_NAME=robot[1], REACTION_NAME=reaction_name, REACTION_STATUS="QUEUED", TABLE_NAME=table_name)
                db.session.add(reaction_status)
                db.session.commit()
                flash(f"Successfully queued {reaction_name}")
                return redirect(url_for('general.queue_reaction'))
            except exc.ProgrammingError as e:
                flash("Query failed: " + str(e))
                return redirect(url_for('general.queue_reaction'))
        flash(f"")
        return redirect(url_for('general.queue_reaction'))

