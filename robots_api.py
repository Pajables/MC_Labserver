from . import synthesis_planner
from flask import Blueprint, request, send_from_directory
from functools import wraps
from werkzeug.security import check_password_hash
from . import db
from .models import Robots, RobotQueue, Reactions
from . import utils
from . import synth_planner


robots_api = Blueprint("robots_api", __name__)

def check_robot_login(func):
    # check hash of supplied robot key
    @wraps(func)
    def verify_robot(*args, **kwargs):
        robot_id = request.args.get('robot_id')
        robot_key = request.args.get('robot_key')
        robot = Robots.query.filter_by(ROBOT_ID=robot_id).first()
        if robot and check_password_hash(robot.ROBOT_KEY, robot_key):
            return func(*args, **kwargs)
        else:
            return {'conn_status': 'refuse'}
    return verify_robot


@robots_api.route("/", methods=["GET", "POST"])
@check_robot_login
def index():
    # GET: server responds with synthesis steps - calls synthesis planner
    # POST: server updates relevant tables (robot_status, reaction_status, etc)
    return {'conn_status': 'accept'}

@robots_api.route("/status", methods=['POST'])
@check_robot_login
def status():
    if request.method == 'POST':
        robot_id = request.args.get('robot_id')
        robot = Robots.query.filter_by(ROBOT_ID=robot_id).first()
        robot.ROBOT_STATUS = request.args.get('robot_status')
        db.session.commit()
        return {'robot_status': 'updated'}

@robots_api.route('/reaction', methods=['GET'])
@check_robot_login
def reactions():
    if request.method == 'GET':
        robot_id = request.args.get('robot_id')
        next_item = RobotQueue.query.filter_by(ROBOT_ID=robot_id).order_by(RobotQueue.QUEUE_NUM.asc()).first()
        reaction_info = Reactions.query.filter_by(REACTION_NAME=next_item.REACTION_NAME).first()
        reaction_name = reaction_info.REACTION_NAME
        table = reaction_info.TABLE_NAME
        xdl_file = reaction_info.FILE_NAME
        reaction_info = db.session.execute(f'SELECT * FROM {table} where REACTION_ID = {next_item.REACTION_ID}')
        reaction_info = reaction_info.fetchone()
        table, reaction_params = utils.get_reaction_params(db, reaction_name, True)
        parameters = []
        for i in range(len(reaction_params)):
            parameters.append([reaction_params[i], reaction_info[i+1]])
        xdl = synthesis_planner.SynthesisPlanner.update_xdl(parameters, xdl_file)
        return {"protocol": xdl,  'xdl_file': xdl_file, 'REACTION_ID': reaction_info[0], "parameters": [(item[0], item[1]) for item in parameters] }
