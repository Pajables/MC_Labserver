from . import synthesis_planner
from flask import Blueprint, request, send_from_directory, jsonify
from functools import wraps
from werkzeug.security import check_password_hash
from . import db
from .models import Robots, RobotQueue, Reactions
from . import utils
from . import synth_planner


robots_api = Blueprint("robots_api", __name__)

def  requires_robot_login(func):
    # check hash of supplied robot key
    @wraps(func)
    def verify_robot(*args, **kwargs):
        json_args = request.get_json()
        if json_args is None:
            return jsonify({'conn_status': 'refused - invalid JSON'})
        robot_id = json_args.get('robot_id')
        robot_key = json_args.get('robot_key')
        robot = Robots.query.filter_by(ROBOT_ID=robot_id).first()
        if robot and check_password_hash(robot.ROBOT_KEY, robot_key):
            return func(*args, **kwargs)
        else:
            return jsonify({'conn_status': 'refused - invalid id/key'})
    return verify_robot


@robots_api.route("/", methods=["GET", "POST"])
@requires_robot_login
def index():
    # GET: server responds with synthesis steps - calls synthesis planner
    # POST: server updates relevant tables (robot_status, reaction_status, etc)
    json_args = request.get_json()
    robot_id = json_args.get('robot_id')
    robot = Robots.query.filter_by(ROBOT_ID=robot_id).first()
    robot.IP_ADDRESS = json_args.get('ip')
    db.session.commit()
    return jsonify({'conn_status': 'accepted'})

@robots_api.route("/status", methods=['GET','POST'])
@requires_robot_login
def status():
    json_args = request.get_json()
    robot_id = json_args.get('robot_id')
    robot = Robots.query.filter_by(ROBOT_ID=robot_id).first()
    cmd = json_args.get('cmd')
    if request.method == 'POST':
        if cmd == "robot_status":
            robot_status = json_args.get('robot_status')
            robot.ROBOT_STATUS = robot_status
            if robot_status == "ERROR":
                robot.ERROR_STATE = 1
            db.session.commit()
            return jsonify({'robot_status': 'updated'})
    elif request.method == "GET":
        if cmd == "robot_execute":
            return jsonify({"action": robot.EXECUTE})
        elif cmd == "error_state":
            return jsonify({"error_state": robot.ERROR_STATE})
    return jsonify({"conn_status": "refused"})

@robots_api.route('/reaction', methods=['GET'])
@requires_robot_login
def reactions():
    if request.method == 'GET':
        json_args = request.get_json()
        robot_id = json_args.get('robot_id')
        next_item = RobotQueue.query.filter_by(ROBOT_ID=robot_id).order_by(RobotQueue.QUEUE_NUM.asc()).first()
        reaction_data = Reactions.query.filter_by(REACTION_NAME=next_item.REACTION_NAME).first()
        reaction_name = reaction_data.REACTION_NAME
        table = reaction_data.TABLE_NAME
        xdl_file = reaction_data.FILE_NAME
        reaction_data = db.session.execute(f'SELECT * FROM {table} where REACTION_ID = {next_item.REACTION_ID}')
        reaction_data = reaction_data.fetchone()
        reaction_class_info = utils.get_reaction_params(db, reaction_name, True)
        reaction_params = reaction_class_info['reaction_params']
        parameters = []
        for i in range(len(reaction_params)):
            # offset reaction data to account for last_update, reaction_id, user_id columns
            parameters.append([reaction_params[i], reaction_data[i+3]])
        xdl = synthesis_planner.SynthesisPlanner.update_xdl(parameters, xdl_file)
        if xdl[0]:
            return jsonify({"name": reaction_name,"protocol": xdl[1],  'xdl_file': xdl_file, 'REACTION_ID': reaction_data[1], "parameters": [(item[0], item[1]) for item in parameters] })
        else:
            return jsonify({"error": xdl[1]})
