from flask import Blueprint, render_template, redirect, request, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Robots
from . import db
from functools import wraps

auth = Blueprint("auth", __name__, template_folder='auth/templates')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('auth/login.html')
    elif request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(USERNAME=username).first()

        if not user or not check_password_hash(user.PASSWORD, password):
            flash("Incorrect user name or password")
            return redirect(url_for('auth.login'))

        login_user(user)
        return redirect(url_for("general.index"))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('general.landing'))


def requires_admin_rights(func):
    @wraps(func)
    def verify_admin(*args, **kwargs):
        if current_user.ADMIN == 1:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('general.robots_display'))
    return verify_admin


@auth.route('/admin')
@login_required
@requires_admin_rights
def admin():
    return render_template('auth/admin_panel.html', name=current_user.USERNAME)


@auth.route('/admin/add_robot', methods=['GET', 'POST'])
@login_required
@requires_admin_rights
def add_robot():
    if request.method == "GET":
        return render_template('auth/add_robot.html')
    elif request.method == "POST":
        robot_id = request.form.get('robot_id')
        robot_key = request.form.get('robot_key')
        robot = Robots.query.filter_by(Robot_key=robot_key).first()

        if robot:
            flash("That robot is already present in the database")
            return redirect(url_for('auth.add_robot'))
        else:
            new_robot = Robots(ROBOT_ID=robot_id, ROBOT_KEY=generate_password_hash(robot_key, method='sha256'))
            db.session.add(new_robot)
            db.session.commit()
            flash(f"Robot {robot_id} added successfully")
            return redirect(url_for('auth.add_robot'))


@auth.route('/admin/add_user', methods=['GET', 'POST'])
@requires_admin_rights
@login_required
def add_user():
    if request.method == "GET":
        return render_template('auth/add_user.html')
    elif request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        admin_flag = request.form.get('admin_check')
        user = User.query.filter_by(USERNAME=username).first()

        if user:
            flash("That robot is already present on the server")
            return redirect(url_for('auth.add_user'))
        else:
            if admin_flag is not None:
                admin_flag = 1
            else:
                admin_flag = 0
            last_id = db.session.execute('SELECT USER_ID FROM Users WHERE USER_ID=(SELECT MAX(USER_ID) FROM Users)')
            new_user = User(USER_ID=last_id+1, USERNAME=username,
                            PASSWORD=generate_password_hash(password, method='sha256'), ADMIN=admin_flag)
            db.session.add(new_user)
            db.session.commit()
