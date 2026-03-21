from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from bson import ObjectId
from functools import wraps
import uuid

employee_bp = Blueprint('employee', __name__)

def get_mongo():
    from app import mongo
    return mongo

def hr_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_hr():
            flash('Access denied. HR privileges required.', 'danger')
            return redirect(url_for('employee.employee_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@employee_bp.route('/hr/dashboard')
@login_required
@hr_required
def hr_dashboard():
    mongo = get_mongo()
    dept_pipeline = [
        {'$group': {'_id': '$department', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]
    dept_stats = list(mongo.db.employees.aggregate(dept_pipeline))
    proj_pipeline = [{'$group': {'_id': '$status', 'count': {'$sum': 1}}}]
    proj_stats = list(mongo.db.projects.aggregate(proj_pipeline))
    total_employees = mongo.db.employees.count_documents({})
    total_projects = mongo.db.projects.count_documents({})
    return render_template('hr_dashboard.html',
        dept_stats=dept_stats, proj_stats=proj_stats,
        total_employees=total_employees, total_projects=total_projects)

@employee_bp.route('/employee/dashboard')
@login_required
def employee_dashboard():
    if current_user.is_hr():
        return redirect(url_for('employee.hr_dashboard'))
    mongo = get_mongo()
    employee = mongo.db.employees.find_one({'user_id': str(current_user.id)})
    if not employee:
        flash('Employee profile not found. Please contact HR.', 'warning')
        return render_template('employee_dashboard.html', employee=None, projects=[], new_count=0)
    projects = list(mongo.db.projects.find({'employee_id': employee['employee_id']}))
    new_count = sum(1 for p in projects if p.get('is_new', False))
    mongo.db.projects.update_many(
        {'employee_id': employee['employee_id'], 'is_new': True},
        {'$set': {'is_new': False}}
    )
    return render_template('employee_dashboard.html',
        employee=employee, projects=projects, new_count=new_count)

@employee_bp.route('/employees')
@login_required
@hr_required
def employees():
    mongo = get_mongo()
    all_employees = list(mongo.db.employees.find())
    return render_template('employees.html', employees=all_employees)

@employee_bp.route('/employees/add', methods=['GET', 'POST'])
@login_required
@hr_required
def add_employee():
    if request.method == 'POST':
        mongo = get_mongo()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        department = request.form.get('department', '').strip()
        role = request.form.get('role', '').strip()
        salary = request.form.get('salary', '0').strip()
        password = request.form.get('password', '').strip()
        if not all([name, email, department, role, salary, password]):
            flash('All fields are required.', 'danger')
            return render_template('add_employee.html')
        if mongo.db.users.find_one({'email': email}):
            flash('An account with this email already exists.', 'danger')
            return render_template('add_employee.html')
        employee_id = 'EMP-' + str(uuid.uuid4())[:8].upper()
        user_result = mongo.db.users.insert_one({
            'name': name, 'email': email,
            'password': generate_password_hash(password), 'role': 'Employee'
        })
        mongo.db.employees.insert_one({
            'employee_id': employee_id, 'name': name,
            'department': department, 'role': role,
            'salary': float(salary), 'user_id': str(user_result.inserted_id)
        })
        flash(f'Employee {name} added successfully!', 'success')
        return redirect(url_for('employee.employees'))
    return render_template('add_employee.html')

@employee_bp.route('/employees/edit/<employee_id>', methods=['GET', 'POST'])
@login_required
@hr_required
def edit_employee(employee_id):
    mongo = get_mongo()
    employee = mongo.db.employees.find_one({'employee_id': employee_id})
    if not employee:
        flash('Employee not found.', 'danger')
        return redirect(url_for('employee.employees'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        department = request.form.get('department', '').strip()
        role = request.form.get('role', '').strip()
        salary = request.form.get('salary', '0').strip()
        mongo.db.employees.update_one(
            {'employee_id': employee_id},
            {'$set': {'name': name, 'department': department,
                      'role': role, 'salary': float(salary)}}
        )
        mongo.db.users.update_one(
            {'_id': ObjectId(employee['user_id'])},
            {'$set': {'name': name}}
        )
        flash(f'Employee {name} updated successfully.', 'success')
        return redirect(url_for('employee.employees'))
    return render_template('edit_employee.html', employee=employee)

@employee_bp.route('/employees/delete/<employee_id>', methods=['POST'])
@login_required
@hr_required
def delete_employee(employee_id):
    mongo = get_mongo()
    employee = mongo.db.employees.find_one({'employee_id': employee_id})
    if not employee:
        flash('Employee not found.', 'danger')
        return redirect(url_for('employee.employees'))
    mongo.db.projects.delete_many({'employee_id': employee_id})
    mongo.db.users.delete_one({'_id': ObjectId(employee['user_id'])})
    mongo.db.employees.delete_one({'employee_id': employee_id})
    flash('Employee deleted successfully.', 'success')
    return redirect(url_for('employee.employees'))