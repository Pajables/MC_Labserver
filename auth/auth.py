from flask import Blueprint, render_template, redirect, request, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from .models import User
from . import db

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
            return redirect(url_for('auth.login'))

        login_user(user)
        return redirect(url_for("general.robots_display"))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('general.index'))


@auth.route('/admin')
@login_required(role='admin')
def admin():
    return "Hello {}, you are an admin!".format(auth.current_user())


@auth.route('admin/add_robot', methods =['GET', 'POST'])
@login_required
def add_robot():
    if request.method == "GET":
        return render_template('auth/login.html')
    elif request.method == "POST":
        robot_id = request.form.get('robot_id')
        robot_key = request.form.get('robot_key')

    user = User.query.filter_by(Robot_key=robot_key).first()

    if user:
        # todo create a robots.html file and code for the arrangement of styles for the main page (__init__.py)
        return redirect(url_for('general.robots'))

    new_user = User(Robot_id=robot_id, password=generate_password_hash(password, method='sha256')

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))


@auth.route('admin/add_user', methods =['GET', 'POST'])
@login_required
def add_user():
    if request.method == "GET":
        return render_template('auth/login.html')
    elif request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

    user = User.query.filter_by(Username=username).first()

    if user:
        # todo create a robot_users.html file and code for the arrangement of styles for the main page (__init__.py)
        return redirect(url_for('general.robot_users'))

    new_user = User(Username=username, password=generate_password_hash(password,method='sha256')

    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))
