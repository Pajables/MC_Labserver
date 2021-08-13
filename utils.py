from flask import current_app, redirect, flash
from werkzeug.utils import secure_filename
import os

unit_db_map = {"seconds" : "INT", "minutes": "DOUBLE", "hours": "DOUBLE",
               "ml": "DOUBLE", "ul": "DOUBLE",
               "g": "DOUBLE", "mg": "DOUBLE", "ug": "DOUBLE"}


def allowed_file(filename):
    return '.' in filename and filename.split('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def upload_protocol(request):
    if 'protocol' not in request.files:
        flash('No file added')
        return redirect(request.url)
    file = request.files['protocol']
    filename = sanitise_file(file)
    if filename is None:
        return redirect(request.url)
    file.save(os.path.join(current_app.config['PROTOCOL_FOLDER'], filename))
    return filename


def sanitise_file(file):
    filename = None
    if file.filename == '':
        flash("No file selected")
    elif file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
    return filename


def split_results(data, results_per_page):
    """
    Splits the results from a database query into multiple pages of data
    :param data: The records returned from the database
    :param results_per_page: Number of results per page.
    :return: split_data - list of lists of record rows, i - number of pages generated
    """
    i = 0
    split_data = []
    rows = data.fetchall()
    while len(rows) > results_per_page:
        split_data.append(rows[0:results_per_page])
        rows = rows[results_per_page:]
        i += 1
    if len(rows) > 0:
        split_data.append(rows)

    return split_data, i


def process_queue_form(form):
    """
    Gets all form data for queuing a reaction
    :param form: Flask.Request.form
    :return: reaction_name - the name of the reaction, parameters - the values of the submitted parameters
    """
    parameters = []
    reaction_name = form.get('reaction_name')
    robot = form.get('robot')
    if robot is None:
        return reaction_name, robot, parameters
    else:
        robot = robot.split('$')
    param_no = 0
    while True:
        form_id = f"param{param_no}"
        param = form.get(form_id)
        if param is None:
            break
        elif param == "":
            return reaction_name, robot, []
        else:
            parameters.append(param)
        param_no += 1
    return reaction_name, robot, parameters


def get_avail_robots(db):
    all_robots = db.session.execute("SELECT ROBOT_ID, ROBOT_NAME FROM Robots")
    robots = [(item[0], item[1]) for item in all_robots]
    return robots


def process_reaction_form(form):
    """
    Processes the add_reaction form
    :param form: from returned to server
    :return: reaction_name - string reaction name, parameters - list [['param_name', 'MySQLunits']...]
    """
    parameters = []
    reaction_name = form.get("reaction-name")
    param_no = 1
    while True:
        name = f"param{param_no}name"
        units = f"param{param_no}units"
        param_name = form.get(name)
        param_name = str(param_name)
        param_units = form.get(units)
        if param_name is None or param_name == "":
            break
        elif param_units is None:
            param_units = "None"
            table_units = "VARCHAR(255)"
        else:
            table_units = unit_db_map[param_units]
        param_name = param_name + "$$" + param_units
        parameter = [param_name, table_units]
        parameters.append(parameter)
        param_no += 1
        add_column_formatting(parameters)
    return reaction_name, parameters


def get_avail_reactions(db):
    """
    Get the reactions stored in the database
    :param db: The database engine
    :return: A set of reaction
    """
    all_reactions = db.session.execute("SELECT REACTION_NAME FROM Reactions")
    reaction_list = [item[0] for item in all_reactions]
    return reaction_list


def get_reaction_params(db, reaction_name, pretty=True):
    """
    Extracts the reaction parameters from the columns of the table
    :param db: The database engine object
    :param reaction_name: The name of the reaction to search for
    :param pretty: Whether to reformat for output to HTML
    :return: table_name - name of table formatted for MySQL, reaction_params - a list of the reaction parameter strings
    """
    table_name = reaction_name.replace(" ", "_")
    table_name = table_name.upper()
    reaction_params = []
    columns = db.session.execute(f"SHOW COLUMNS FROM {table_name}")
    columns.fetchone()
    for item in columns:
        reaction_params.append(item[0])
    if pretty:
        remove_column_formatting(reaction_params)
    return table_name, reaction_params


def add_column_formatting(columns):
    """
    Formats column for MySQL
    :param columns: List [['column_name', 'SQL_units']...]
    """
    for i in range(len(columns)):
        columns[i][0] = columns[i][0].replace(" ", "_")


def remove_column_formatting(columns):
    """
    Formats column headings for legibility on HTML pages
    :param columns: list of column headings
    """
    for i in range(len(columns)):
        words = columns[i].split("$$")
        if len(words) > 1:
            unit = words[1]
            name = words[0]
            columns[i] = name + " [" + unit + "]"
        columns[i] = columns[i].replace("_", " ")
