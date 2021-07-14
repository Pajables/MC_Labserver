from flask import Blueprint, render_template, redirect, request, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
from models import User
from .. import db

auth = Blueprint("auth", __name__, template_folder='templates')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('auth/login.html')
    elif request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(user=username).first()

        if not user or not check_password_hash(user.password, password):
            return redirect(url_for('auth.login'))

        login_user(user)
        return redirect(url_for("general.robots_display"))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('general'))
