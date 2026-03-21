from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from functools import wraps
from bson import ObjectId

project_bp = Blueprint('project', __name__)

def get_mongo():
    from app import mongo
    return mongo

def hr_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_hr():
            flash('Access denied.', 'danger')
            return redirect(url_for('employee.employee_dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@project_bp.route('/projects')
@login_required
@hr_required
def projects():
    mongo = get_mongo()
    all_projects = list(mongo.db.projects.find())
    for project in all_projects:
        emp = mongo.db.employees.find_one({'employee_id': project.get('employee_id')})
        project['employee_name'] = emp['name'] if emp else 'Unknown'
        project['employee_dept'] = emp['department'] if emp else 'Unknown'
    return render_template('projects.html', projects=all_projects)

@project_bp.route('/projects/add', methods=['GET', 'POST'])
@login_required
@hr_required
def add_project():
    mongo = get_mongo()
    all_employees = list(mongo.db.employees.find())
    if request.method == 'POST':
        project_name = request.form.get('project_name', '').strip()
        description = request.form.get('description', '').strip()
        employee_id = request.form.get('employee_id', '').strip()
        status = request.form.get('status', 'Ongoing')
        if not all([project_name, description, employee_id]):
            flash('All fields are required.', 'danger')
            return render_template('add_project.html', employees=all_employees)
        employee = mongo.db.employees.find_one({'employee_id': employee_id})
        if not employee:
            flash('Selected employee not found.', 'danger')
            return render_template('add_project.html', employees=all_employees)
        mongo.db.projects.insert_one({
            'project_name': project_name, 'description': description,
            'employee_id': employee_id, 'status': status,
            'is_new': True, 'assigned_at': datetime.utcnow(),
            'assigned_by': str(current_user.id)
        })
        flash(f'Project "{project_name}" assigned successfully!', 'success')
        return redirect(url_for('project.projects'))
    return render_template('add_project.html', employees=all_employees)

@project_bp.route('/projects/edit/<project_id>', methods=['GET', 'POST'])
@login_required
@hr_required
def edit_project(project_id):
    mongo = get_mongo()
    proj = mongo.db.projects.find_one({'_id': ObjectId(project_id)})
    if not proj:
        flash('Project not found.', 'danger')
        return redirect(url_for('project.projects'))
    all_employees = list(mongo.db.employees.find())
    if request.method == 'POST':
        project_name = request.form.get('project_name', '').strip()
        description = request.form.get('description', '').strip()
        employee_id = request.form.get('employee_id', '').strip()
        status = request.form.get('status', 'Ongoing')
        is_new = True if employee_id != proj.get('employee_id') else proj.get('is_new', False)
        mongo.db.projects.update_one(
            {'_id': ObjectId(project_id)},
            {'$set': {'project_name': project_name, 'description': description,
                      'employee_id': employee_id, 'status': status, 'is_new': is_new}}
        )
        flash(f'Project updated successfully.', 'success')
        return redirect(url_for('project.projects'))
    return render_template('edit_project.html', project=proj, employees=all_employees)

@project_bp.route('/projects/delete/<project_id>', methods=['POST'])
@login_required
@hr_required
def delete_project(project_id):
    mongo = get_mongo()
    result = mongo.db.projects.delete_one({'_id': ObjectId(project_id)})
    if result.deleted_count:
        flash('Project deleted successfully.', 'success')
    else:
        flash('Project not found.', 'danger')
    return redirect(url_for('project.projects'))