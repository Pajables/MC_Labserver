from flask import current_app, redirect, flash
from werkzeug.utils import secure_filename
import os
import sys
import random
import string
import csv
from .synthesis_planner import SynthesisPlanner

unit_db_map = {"seconds": "INT", "minutes": "DOUBLE", "hours": "DOUBLE",
               "ml": "DOUBLE", "ul": "DOUBLE", "g": "DOUBLE", "mg": "DOUBLE",
                "ug": "DOUBLE", "°C": "DOUBLE", "K": "DOUBLE", "hex": "INT"}


def generate_img_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=24))

def allowed_file(filename):
    return '.' in filename and filename.split('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def upload_protocol(request, protocol_type):
    e = ''
    if protocol_type not in request.files:
        e =f"{protocol_type} file not found"
        return None, e
    file = request.files[protocol_type]
    filename = sanitise_file(file)
    if filename is None:
        e = "That file extension is not recognised"
        return None, e
    if protocol_type == 'protocol':
        xdl = file.read()
        protocol, error = SynthesisPlanner.load_xdl_string(xdl)
        if protocol is None:
            return None, error
        with open(os.path.join(current_app.config['PROTOCOL_FOLDER'], filename), 'w+', encoding="UTF-8") as file:
            file.write(xdl.decode('UTF-8'))
    else:
        file.save(os.path.join(current_app.config['PROTOCOL_FOLDER'], filename))
    return filename, e

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
        i += 1
    return split_data, i


def process_queue_form(form, reaction_params):
    """
    Gets all form data for queuing a reaction
    :param reaction_params:
    :param form: Flask.Request.form
    :return: reaction_name - the name of the reaction, parameters - the values of the submitted parameters
    """
    parameters = []
    robot = form.get('robot')
    if robot is None:
        return robot, parameters
    else:
        robot = robot.split('$')
    param_no = 0
    while True:
        form_id = f"param{param_no}"
        param = form.get(form_id)
        if param is None:
            break
        elif param == "":
            return robot, []
        else:
            param_units = reaction_params[param_no].split("$$")[1]
            units = unit_db_map[param_units]
            if units == 'DOUBLE':
                param = float(param)
            elif units == 'INT':
                param = int(param)
            parameters.append(param)
        param_no += 1
    return {"robot": robot, "parameters": parameters}

def process_manual_input(form, reaction_params, num_params):
    parameters = []
    print(reaction_params, file=sys.stderr)
    for i in range(num_params):
        param = form.get(f'param{i}')
        if param is None or param == "":
            continue
        else:
            parameters.append((reaction_params[i], param))
    return parameters

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
    results = []
    reaction_name = form.get("reaction-name")
    clean_step = form.get("clean-step")
    if clean_step is None:
        clean_step = 0
    else:
        clean_step = 1
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
            table_units = "TEXT"
        else:
            table_units = unit_db_map[param_units]
        param_name = param_name + "$$" + param_units
        parameter = [param_name, table_units]
        parameters.append(parameter)
        param_no += 1
        add_column_formatting(parameters)
    results_num = 1
    while True:
        results_name = form.get(f"results{results_num}")
        results_units = form.get(f"results{results_num}units")
        if results_name is None or results_name == "":
            break
        elif results_units is None:
            results.append([results_name + "$result$", "FLOAT"])
        else:
            table_units = unit_db_map[results_units]
            results.append([results_name + '$result$' + results_units, table_units])
            results_num += 1
    return {"reaction_name": reaction_name, "clean_step": clean_step,  "reaction_params": parameters, "results": results}


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
    results = []
    columns = db.session.execute(f"SHOW COLUMNS FROM {table_name}")
    for item in columns:
        if "$result$" in item[0]:
            results.append(item[0])
        elif "$$" in item[0]:
            reaction_params.append(item[0])
    if pretty:
        remove_column_formatting(reaction_params, "$$")
        remove_column_formatting(results, "$result$")
    return {"table_name": table_name, "reaction_params": reaction_params, "results": results}


def add_column_formatting(columns):
    """
    Formats column for MySQL
    :param columns: List [['column_name', 'SQL_units']...]
    """
    for i in range(len(columns)):
        columns[i][0] = columns[i][0].replace(" ", "_")
        columns[i][0] = columns[i][0].replace("-", "_")


def remove_column_formatting(columns, split_term):
    """
    Formats column headings for legibility on HTML pages
    :param columns: list of column headings
    """
    for i in range(len(columns)):
        words = columns[i].split(split_term)
        if len(words) > 1:
            unit = words[1]
            name = words[0]
            columns[i] = name + " [" + unit + "]"
        columns[i] = columns[i].replace("_", " ")

def extract_from_csv(csv_filename, delimiter=';'):
    data = []
    with open(os.path.join(current_app.config['PROTOCOL_FOLDER'], csv_filename)) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter)
        for row in csv_reader:
            data.append(row)
    columns = []
    for i in range(len(data[0])):
        col_name = data[0][i].split('[')
        units = col_name[-1][:-1]
        # if there are no units this must be a results column
        if data[1][i] == '':          
            columns.append([col_name[0] + "$result$" + units, unit_db_map.get(units)])
        else:
            columns.append([col_name[0] + "$$" + units, unit_db_map.get(units)])
    add_column_formatting(columns)
    return [columns, data[1:]]
            
def write_csv(reaction_name, reaction_params, results, reaction_data):
    file = f"{reaction_name}.csv"
    path = current_app.config['SENT_FILES_FOLDER']
    filepath = os.path.join(path, file)
    with open(filepath, 'w+') as csv_file:
        writer = csv.writer(csv_file, delimiter=';')
        writer.writerow(reaction_params+results)
        for row in reaction_data:
            writer.writerow(row[3:])
    return file, path
    
