from . import utils
from flask import Blueprint, render_template, url_for, request, redirect, flash, send_from_directory, abort
from flask_login import login_required, current_user
from sqlalchemy import exc, delete
from . import db
from . import models
from datetime import datetime
import sys

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
    robots_data = db.session.execute("""SELECT ROBOT_ID, ROBOT_NAME, IP_ADDRESS, ROBOT_STATUS, CURRENT_JOB, EXECUTE, LAST_UPDATE_DATE FROM
                                     Robots""")
    if request.method == "GET":
        return render_template('general/robots.html', robots_data=robots_data)

@general.route("/robots/clear_error", methods=["GET"])
@login_required
def clear_error():
    robot_id = request.args.get("robot_id")
    robot = models.Robots.query.filter_by(ROBOT_ID=robot_id).first()
    robot.ERROR_STATE = 0
    db.session.commit()
    return redirect(url_for('general.robots'))

@general.route("/robots/execute", methods=["GET"])
@login_required
def execute():
    robot_id = request.args.get('robot_id')
    cmd = request.args.get('cmd')
    if cmd is None or robot_id is None:
        flash("Please try again")
    else:
        try:
            cmd = int(cmd)
            if cmd > 0:
                message = 'run'
            else:
                message = 'stop'
            robot = models.Robots.query.filter_by(ROBOT_ID=robot_id).first()
            robot.EXECUTE = cmd
            db.session.commit()
            flash(f"Set {robot.ROBOT_NAME} to {message}")
        except exc.ProgrammingError as e:
            flash("Query failed, " + str(e))
    return redirect(url_for('general.robots'))


@general.route("/reactions", methods=['GET', 'POST'])
@login_required
def reactions():
    if request.method == 'GET':
        # Get reactions from database and display in a table
        reactions_data = db.session.execute("SELECT  * FROM Reactions_Status ORDER BY LAST_UPDATE_DATE")
        pages_data, pages, page_nr = split_results(request, reactions_data)
        if not pages_data:
            return render_template('general/reactions_status.html', num_pages=0)
        return render_template('general/reactions_status.html', reactions_data=pages_data[page_nr], cur_page=page_nr,
                               num_pages=pages, results_per_page=request.args.get('results_per_page'))


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
            reaction_info = utils.get_reaction_params(db, reaction_name, True)
            table_name = reaction_info["table_name"]
            reaction_params = reaction_info["reaction_params"]
            results=reaction_info["results"]
            specific_reaction = db.session.execute(f"SELECT * FROM {table_name};")
            pages_data, pages, page_nr = split_results(request, specific_reaction)
            if len(pages_data) == 0:
                page_data = []
            else:
                page_data = pages_data[page_nr]
            return render_template('general/reaction.html', all_reactions=all_reactions, sel_reaction=True,
                                   reaction_name=reaction_name, reaction_params=reaction_params, results=results,
                                    reaction_data=page_data, cur_page=page_nr, num_pages=pages,
                                    results_per_page=request.args.get('results_per_page'))
        except exc.ProgrammingError as e:
            flash("Query failed: " + str(e))
            return redirect(url_for('general.display_reactions'))

@general.route('/export_csv', methods=['GET'])
@login_required
def export_csv():
    if request.method == "GET":
        reaction_name = request.args.get('reaction_name')
        if reaction_name is None:
            return redirect(url_for('general.display_reactions'))
        try:
            reaction_info = utils.get_reaction_params(db, reaction_name, True)
            table_name = reaction_info['table_name']
            reaction_params = reaction_info['reaction_params']
            results = reaction_info['results']
            reaction_data = db.session.execute(f"SELECT * FROM {table_name};")
            file, directory = utils.write_csv(reaction_name, reaction_params, results, reaction_data)
            return send_from_directory(directory, file, as_attachment=True)
        except  FileNotFoundError:
            abort(404)

@general.route("/add_reaction", methods=['GET', 'POST'])
@login_required
def add_reaction():
    if request.method == "GET":
        return render_template('general/reaction_add.html')
    elif request.method == "POST": 
        form_output = utils.process_reaction_form(request.form)
        reaction_name = form_output["reaction_name"]
        parameters = form_output["reaction_params"]
        results = form_output["results"]
        filename, e = utils.upload_protocol(request, 'protocol')
        if filename is None:
            flash("Failed to add file: " + str(e))
            return render_template("general/reaction_add.html")
        table_name = reaction_name.replace(" ", "_")
        table_name = table_name.upper()
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} (LAST_UPDATE_DATE TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, REACTION_ID INT, USER_ID INT, CLEAN_STEP INT,"
        # REACTION_ID | USER_ID | CLEAN_STEP | PARAM1 | PARAM2 | PARAM3 | ....| RESULTS1| RESULTS2| RESULTS3|
        for parameter in parameters:
            sql += parameter[0] + " " + parameter[1] + ", "
        for result in results:
            sql += result[0] + " " + result[1]  + ", "
        sql += "PRIMARY KEY (REACTION_ID));"
        try:
            db.session.execute(sql)
            sql = f'''INSERT INTO Reactions (REACTION_NAME, TABLE_NAME, FILE_NAME) 
            VALUES ('{reaction_name}', '{table_name}', '{filename}');'''
            db.session.execute(sql)
            db.session.commit()
            flash(f"Successfully added table {table_name}")
            return redirect(url_for('general.add_reaction'))
        except (exc.ProgrammingError, exc.IntegrityError) as e:
            flash(f"Failed to add table {table_name}" + str(e))
            return redirect(url_for('general.add_reaction'))

@general.route("/batch_add_reaction", methods=["GET", "POST"])
@login_required
def batch_add_reaction():
    avail_robots = utils.get_avail_robots(db)
    if request.method == "GET":
        return render_template("general/reaction_batch_add.html", avail_robots=avail_robots, num_bots=len(avail_robots))
    elif request.method == "POST":
        avail_robots = utils.get_avail_robots(db)
        reaction_name = request.form.get('reaction_name')
        csv_delim = request.form.get('csv_delim')
        clean_step = request.form.get("clean-step")
        if clean_step is None:
            clean_step = 0
        else:
            clean_step = 1
        csv_filename, e = utils.upload_protocol(request, "reaction_csv")
        if csv_filename is None:
            flash(f'Failed to add csv {csv_filename} file.' + e)
            return render_template("general/reaction_batch_add.html", avail_robots=avail_robots, num_bots=len(avail_robots))
        xdl_filename, e = utils.upload_protocol(request, "protocol")
        if xdl_filename is None:
            flash(f"Failed to add xdl {xdl_filename} file" + e)
            return render_template("general/reaction_batch_add.html", avail_robots=avail_robots, num_bots=len(avail_robots))
        last_reaction_id = db.session.execute("SELECT REACTION_ID FROM Reactions_Status WHERE REACTION_ID=(SELECT MAX(REACTION_ID) FROM Reactions_Status)").fetchone()
        reaction_id = None
        if last_reaction_id is None:
            reaction_id = 1
        else:
            reaction_id = last_reaction_id[0] + 1
        columns, reaction_data = utils.extract_from_csv(csv_filename=csv_filename, delimiter=csv_delim)
        insert_cols = []
        num = 0
        table_name = reaction_name.replace(" ", "_").upper()
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} (LAST_UPDATE_DATE TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, REACTION_ID INT, USER_ID INT, CLEAN_STEP INT,"
        insert_sql = f"INSERT INTO {table_name} (REACTION_ID, USER_ID, CLEAN_STEP, "
        for column in columns:
            create_sql += column[0] + " " + column[1] + ", "
            if "$result$" not in column[0]:
                insert_cols.append(num)
                insert_sql += column[0] + ", "
            num += 1
        create_sql += "PRIMARY KEY (REACTION_ID));"
        insert_sql = insert_sql[:-2]
        insert_sql += ") "
        try:
            db.session.execute(create_sql)
            sql = f'''INSERT INTO Reactions (REACTION_NAME, TABLE_NAME, FILE_NAME)
            VALUES ('{reaction_name}', '{table_name}', '{xdl_filename}');'''
            db.session.execute(sql)
        except exc.ProgrammingError as e:
            flash(f"Failed to create {table_name} " +str(e))
        try:
            # divide reactions between available robots
            robots_participating = []
            for i in range(len(utils.get_avail_robots(db))):
                robot = request.form.get(f"robot{i}")
                if robot is not None:
                    robot = robot.split("$")
                    robots_participating.append([robot[0], robot[1]])
            total_reactions = len(reaction_data)
            next_robot = get_next_robot(robots_participating, total_reactions)
            for row in reaction_data:
                final_insert_sql = insert_sql + f"VALUES ({reaction_id}, {current_user.USER_ID}, {clean_step}, "
                reaction_id += 1
                robot = next(next_robot)
                for i in range(len(row)):
                    if i in insert_cols:
                        row[i] = row[i].replace(',', '.')
                        final_insert_sql += row[i] + ', '
                final_insert_sql = final_insert_sql[:-2]
                final_insert_sql += ");"
                db.session.execute(final_insert_sql)
                queued_item = models.RobotQueue(USER_ID=current_user.USER_ID, ROBOT_ID=robot[0],
                                                                        REACTION_NAME=reaction_name, REACTION_ID=reaction_id)
                db.session.add(queued_item)
                reaction_status = models.ReactionStatus(REACTION_ID=reaction_id, ROBOT_ID=robot[0],
                 ROBOT_NAME=robot[1], REACTION_NAME=reaction_name, REACTION_STATUS="QUEUED",
                  TABLE_NAME=table_name)
                db.session.add(reaction_status)
                db.session.commit()
            db.session.commit()
            flash(f"Successfully added table {table_name}")
            return redirect(url_for('general.add_reaction'))
        except (exc.ProgrammingError, exc.IntegrityError) as e:
            flash("Failed to insert data" + str(e))
            return redirect(url_for('general.add_reaction'))
                 

@general.route("/manual_input", methods=['GET', 'POST'])
@login_required
def manual_input():
    if request.method == 'GET':
        reaction_id = request.args.get('reaction_id')
        user_id = request.args.get('user_id')
        if reaction_id is None or user_id is None:
            flash("Please select a reaction to edit:")
            return redirect(url_for('general.display_reactions'))
        if current_user.USER_ID == int(user_id) or current_user.ADMIN:
            # todo get reaction from id and present fields
            reaction_name = request.args.get('reaction_name')
            reaction_info = utils.get_reaction_params(db, reaction_name, True)
            table_name = reaction_info["table_name"]
            reaction_params = reaction_info["reaction_params"]
            results=reaction_info["results"]
            reaction_params = reaction_params + results
            # -1 reaction id signifies new manually input reaction
            if int(reaction_id) != -1:
                specific_reaction = db.session.execute(f"SELECT * FROM {table_name} WHERE REACTION_ID={reaction_id}").fetchone()
                new_reaction = False
            else:
                new_reaction = True
                specific_reaction = {}
                for item in reaction_params:
                    specific_reaction[item] = item
            return render_template("general/reaction_manual_input.html", reaction_id=reaction_id, reaction_name=reaction_name, new_reaction=new_reaction, reaction_params=reaction_params, specific_reaction=specific_reaction)
        else:
            flash("You are not authenticated to edit this reaction. Please contact an admin")
            return redirect(url_for('general.display_reactions'))
    elif request.method == "POST":
        new_reaction = request.form.get('new_reaction')
        reaction_name = request.form.get('reaction_name')
        reaction_info = utils.get_reaction_params(db, reaction_name, False)
        table_name = reaction_info['table_name']
        reaction_params = reaction_info['reaction_params']
        total_params = reaction_params + reaction_info['results']
        updates = utils.process_manual_input(request.form, total_params, int(request.form['num_params']))
        if new_reaction is None:
            # This reaction already exists in the database
            reaction_id = request.form.get('reaction_id')
            try:
                if len(updates) == 0:
                    flash("No parameters updated")
                    return redirect(url_for('general.display_reactions'))
                sql = f"UPDATE {table_name} \nSET "
                for item in updates:
                    sql += item[0] + " = " + item[1] + ", "
                sql = sql[:-2]
                sql += f"\nWHERE REACTION_ID={reaction_id};"
                print(sql, file=sys.stderr)
                db.session.execute(sql)
                db.session.commit()
            except exc.ProgrammingError as e:
                flash("Query failed: " + str(e))
                return redirect(url_for('general.display_reactions'))
        else:
            # This is a new reaction 
            reaction_id = db.session.execute("SELECT REACTION_ID FROM Reactions_Status WHERE REACTION_ID=(SELECT MAX(REACTION_ID) FROM Reactions_Status)").fetchone()
            if reaction_id is None:
                reaction_id = 1
            else:
                reaction_id = reaction_id[0] + 1
            if len(updates) < len(reaction_params):
                flash("Please update all the parameters")
                return redirect(url_for('general.manual_input', reaction_id=-1, reaction_name=reaction_name, user_id=current_user.USER_ID))
            parameters = [item[1] for item in updates]
            try:
                insert_into_rt(table_name, reaction_id, total_params, parameters, len(reaction_params))
                reaction_status = models.ReactionStatus(REACTION_ID=reaction_id, ROBOT_ID='Manual',
                 ROBOT_NAME='Manual', REACTION_NAME=reaction_name, REACTION_STATUS='Complete',
                  TABLE_NAME=table_name, JOB_COMPLETION_DATE=datetime.today().strftime('%Y%m%d'))
                db.session.add(reaction_status)
                db.session.commit()
            except exc.ProgrammingError as e:
                flash("Query failed: " + str(e))
                return redirect(url_for('general.manual_input', reaction_id=-1, reaction_name=reaction_name, user_id=current_user.USER_ID))
        flash(f"Successfully added reaction data for {reaction_name}")
        return redirect(url_for('general.display_reactions'))


@general.route("/show_queue", methods=["GET"])
@login_required
def show_queue():
    try:
        columns_data = db.session.execute("SHOW COLUMNS FROM Robot_Queue")
        columns = []
        for item in columns_data:
            column = item[0]
            column = column.replace("_", " ")
            column = column.lower()
            column = column.capitalize()
            column = column.replace("id", "ID")
            columns.append(column)
        queue_items = db.session.execute("SELECT * FROM Robot_Queue")
        pages_data, pages, page_nr = split_results(request, queue_items)
        if not pages_data:
            return render_template('general/queue_show.html', columns=columns, cur_page=1, queue_items=[], num_pages=1, results_per_page=request.args.get('results_per_page'))
        return render_template('general/queue_show.html', columns=columns, queue_items=pages_data[page_nr],
                                            cur_page=page_nr, num_pages=pages,
                                            results_per_page=request.args.get('results_per_page'))
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
            reaction_params = form_output["reaction_params"]
            all_robots = utils.get_avail_robots(db)
            return render_template('general/queue_reaction.html', all_reactions=all_reactions, sel_reaction=True, reaction_name=reaction_name, reaction_params=reaction_params, all_robots=all_robots)
    elif request.method == "POST":
        reaction_name = request.form.get("reaction_name")
        reaction_info = utils.get_reaction_params(db, reaction_name, False)
        table_name = reaction_info["table_name"]
        reaction_params = reaction_info["reaction_params"]
        form_output = utils.process_queue_form(request.form, reaction_params)
        robot = form_output["robot"]
        parameters = form_output["parameters"]
        if len(parameters) == len(reaction_params) and robot:
            try:
                reaction_id = db.session.execute("SELECT REACTION_ID FROM Reactions_Status WHERE REACTION_ID=(SELECT MAX(REACTION_ID) FROM Reactions_Status)").fetchone()
                if reaction_id is None:
                    reaction_id = 1
                else:
                    reaction_id = reaction_id[0] + 1
                queued_item = models.RobotQueue(USER_ID=current_user.USER_ID, ROBOT_ID=robot[0],
                 REACTION_NAME=reaction_name, REACTION_ID=reaction_id)
                db.session.add(queued_item)
                insert_into_rt(table_name, reaction_id, reaction_params, parameters)
                reaction_status = models.ReactionStatus(REACTION_ID=reaction_id, ROBOT_ID=robot[0],
                 ROBOT_NAME=robot[1], REACTION_NAME=reaction_name, REACTION_STATUS="QUEUED",
                  TABLE_NAME=table_name)
                db.session.add(reaction_status)
                db.session.commit()
                flash(f"Successfully queued {reaction_name}")
                return redirect(url_for('general.queue_reaction'))
            except exc.ProgrammingError as e:
                flash("Query failed: " + str(e))
                return redirect(url_for('general.queue_reaction'))
        else:
            flash("Incorrect parameters supplied")
            return redirect(url_for('general.queue_reaction'))
    
@general.route('/unqueue', methods=['GET'])
@login_required
def unqueue():
    if request.method == 'GET':
        reaction_id = request.args.get('reaction_id')
        reaction_name = request.args.get('reaction_name')
        if reaction_id is None:
            return redirect(url_for('general.show_queue'))
        else:
            try:
                db.session.execute(delete(models.RobotQueue).where(models.RobotQueue.REACTION_ID == int(reaction_id)))
                db.session.commit()
                flash(f'Removed queued {reaction_name} reaction')
            except exc.ProgrammingError as e:
                flash("Query failed " + str(e))
            return redirect(url_for('general.show_queue'))

        
def insert_into_rt(table_name, reaction_id, reaction_params, parameters, amnt=None):
    if amnt is None:
        amnt = len(reaction_params)
    sql_pre = f"INSERT INTO {table_name} (REACTION_ID, USER_ID, "
    sql_post = f" VALUES ({reaction_id}, {current_user.USER_ID}, "
    for i in range(amnt):
        sql_pre += f"{reaction_params[i]}, "
        sql_post += f"{parameters[i]}, "
    sql_pre = sql_pre[:-2]
    sql_post = sql_post[:-2]
    sql_pre += ")"
    sql_post += ");"
    db.session.execute(sql_pre + sql_post)

def split_results(request, data):
    results_per_page = request.args.get('results_per_page')
    if results_per_page is None:
        results_per_page = 20
    pages_data, pages = utils.split_results(data, int(results_per_page))
    page_nr = request.args.get('page_nr')
    if page_nr is None:
        page_nr = 0
    else:
        page_nr = int(page_nr)
    return pages_data, pages, page_nr

def get_next_robot(robots_participating, total_reactions):
    for i in range(total_reactions):
        yield robots_participating[i % len(robots_participating)]
        
