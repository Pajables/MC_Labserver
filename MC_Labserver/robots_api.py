import sys
import datetime
from . import synthesis_planner
from flask import Blueprint, request, send_from_directory, jsonify
from functools import wraps
from werkzeug.security import check_password_hash
from sqlalchemy import exc
from . import db
from .models import Robots, RobotQueue, Reactions, ReactionStatus
from . import utils
from . import synth_planner



robots_api = Blueprint("robots_api", __name__)
img_metadata = {}

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
            reaction_complete = json_args.get('reaction_complete')
            try:
                if reaction_complete:
                    reaction_id = json_args.get('reaction_id')
                    today = datetime.date.today()
                    RobotQueue.query.filter_by(REACTION_ID=reaction_id).delete()
                    status = ReactionStatus.query.filter_by(REACTION_ID=reaction_id).first()
                    status.REACTION_STATUS = 'COMPLETE'
                    status.JOB_COMPLETION_DATE = f"{today.year}-{today.month}-{today.day}"
                robot.ROBOT_STATUS = robot_status
                if robot_status == "ERROR":
                    robot.ERROR_STATE = 1
                db.session.commit()
                return jsonify({'robot_status': 'updated'})
            except (exc.ProgrammingError, exc.exc.IntegrityError) as e:
                return jsonify({"error": f"{e}"})
    elif request.method == "GET":
        if cmd == "robot_execute":
            return jsonify({"action": robot.EXECUTE})
        elif cmd == "error_state":
            return jsonify({"error_state": robot.ERROR_STATE})
    return jsonify({"conn_status": "refused"})

@robots_api.route("/complete_reaction", methods=['POST'])
@requires_robot_login
def complete_reaction():
    if request.method == "POST":
        json_args = request.get_json()
        reaction_id = json_args.get('reaction_id')
        ReactionStatus.query.filter_by(REACTION_ID=reaction_id).delete()
        db.session.commit()

@robots_api.route('/reaction', methods=['GET'])
@requires_robot_login
def reactions():
    if request.method == 'GET':
        json_args = request.get_json()
        robot_id = json_args.get('robot_id')
        next_item = RobotQueue.query.filter_by(ROBOT_ID=robot_id).order_by(RobotQueue.QUEUE_NUM.asc()).first()
        print(next_item, file=sys.stderr)
        if next_item is None:
            return jsonify({"info": f"No reactions for {robot_id} remain in queue"})
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
            parameters.append([reaction_params[i], reaction_data[i+4]])
        xdl = synthesis_planner.SynthesisPlanner.update_xdl(parameters, xdl_file)
        clean_step = reaction_data[3]
        if xdl[0]:
            return jsonify({"name": reaction_name, "reaction_id": next_item.REACTION_ID, "protocol": xdl[1],  'xdl_file': xdl_file, "parameters": [(item[0], item[1]) for item in parameters], "clean_step": clean_step})
        else:
            return jsonify({"error": xdl[1]})

@robots_api.route('/send_image', methods=['POST'])
def get_image():
    if request.method == 'POST':
        request_id = request.args.get('request_id')
        #first get metadata and reply with a unique ID
        if request_id is None:
            json_args = request.get_json()
            if json_args is None:
                return jsonify({"error": "No json supplied"})
            cur_img_metadata = {"reaction_id": json_args.get('reaction_id'),
            "img_number": json_args.get('img_number'), 'reaction_name': json_args.get('reaction_name'),
            "img_processing": json_args.get('img_processing'), "img_roi": json_args.get('img_roi')}
            request_id = utils.generate_img_id()
            img_metadata[request_id] = cur_img_metadata
            return jsonify({"request_id": request_id})
        #check that our ID matches metadata on file, if so then finalise upload.
        else:
            request_id = request.args.get('request_id')
            cur_img_metadata = img_metadata.get(request_id)
            if cur_img_metadata is None:
                return jsonify({'error': "invalid metadata or request id"})
            else:
                del img_metadata[request_id]
                processing = cur_img_metadata.get('img_processing')
                if processing != "":
                    if processing == "azo":
                        img_hex_colour = synth_planner.upload_reaction_img(request.data, cur_img_metadata)
                        try:
                            img_number = cur_img_metadata.get('img_number')
                            reaction_id = cur_img_metadata.get('reaction_id')
                            reaction_data = Reactions.query.filter_by(REACTION_NAME=cur_img_metadata['reaction_name']).first()
                            table = reaction_data.TABLE_NAME
                            db.session.execute(f"UPDATE {table} SET colour{img_number}_$result$hex = {img_hex_colour}  WHERE REACTION_ID = {reaction_id};")
                            db.session.commit()
                            return jsonify({"status": "image accepted"})
                        except (exc.ProgrammingError, AttributeError) as e:
                            return jsonify({"error": str(e)})
                else:
                    image_size = synth_planner.upload_reaction_img(request.data, cur_img_metadata)
                    return jsonify({'image_size': image_size})
