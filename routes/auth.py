from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_hr():
            return redirect(url_for('employee.hr_dashboard'))
        return redirect(url_for('employee.employee_dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        from app import mongo
        user_doc = mongo.db.users.find_one({'email': email})

        if user_doc and check_password_hash(user_doc['password'], password):
            user = User(user_doc)
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            if user.is_hr():
                return redirect(url_for('employee.hr_dashboard'))
            return redirect(url_for('employee.employee_dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))