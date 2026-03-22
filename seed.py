"""
seed.py — WorkForce Hub Sample Data Seeder
Run this once to populate the database with demo users, employees, and projects.

Usage:
    python seed.py
"""
from app import create_app, mongo
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import uuid


def generate_emp_id():
    """Generate a unique employee ID like EMP-A1B2C3D4."""
    return 'EMP-' + str(uuid.uuid4())[:8].upper()


def seed():
    app = create_app()
    with app.app_context():

        print("🗑️  Clearing existing data...")
        mongo.db.users.drop()
        mongo.db.employees.drop()
        mongo.db.projects.drop()

        # ──────────────────────────────────────────
        # 1. HR Admin account
        # ──────────────────────────────────────────
        hr_user_id = mongo.db.users.insert_one({
            'name': 'Admin HR',
            'email': 'admin@workforce.com',
            'password': generate_password_hash('admin123'),
            'role': 'HR'
        }).inserted_id
        print(f"✅ HR Admin created → admin@workforce.com / admin123")

        # ──────────────────────────────────────────
        # 2. Employee user accounts + employee profiles
        # ──────────────────────────────────────────
        employees_data = [
            {
                'name': 'John Doe',
                'email': 'john@workforce.com',
                'password': 'emp123',
                'department': 'Engineering',
                'role': 'Senior Software Engineer',
                'salary': 95000.0,
            },
            {
                'name': 'Priya Sharma',
                'email': 'priya@workforce.com',
                'password': 'emp123',
                'department': 'Design',
                'role': 'UI/UX Designer',
                'salary': 72000.0,
            },
            {
                'name': 'Rahul Menon',
                'email': 'rahul@workforce.com',
                'password': 'emp123',
                'department': 'Marketing',
                'role': 'Marketing Manager',
                'salary': 68000.0,
            },
            {
                'name': 'Sara Thomas',
                'email': 'sara@workforce.com',
                'password': 'emp123',
                'department': 'Engineering',
                'role': 'Backend Developer',
                'salary': 85000.0,
            },
            {
                'name': 'Arun Kumar',
                'email': 'arun@workforce.com',
                'password': 'emp123',
                'department': 'Finance',
                'role': 'Financial Analyst',
                'salary': 78000.0,
            },
        ]

        inserted_employees = []
        for data in employees_data:
            # Create user account
            user_id = mongo.db.users.insert_one({
                'name': data['name'],
                'email': data['email'],
                'password': generate_password_hash(data['password']),
                'role': 'Employee'
            }).inserted_id

            # Create employee profile
            emp_id = generate_emp_id()
            mongo.db.employees.insert_one({
                'employee_id': emp_id,
                'name': data['name'],
                'department': data['department'],
                'role': data['role'],
                'salary': data['salary'],
                'user_id': str(user_id)
            })
            inserted_employees.append({'emp_id': emp_id, 'name': data['name']})
            print(f"✅ Employee created → {data['email']} / {data['password']}  [{emp_id}]")

        # ──────────────────────────────────────────
        # 3. Sample projects assigned to employees
        # ──────────────────────────────────────────
        hr_id = str(hr_user_id)
        now = datetime.utcnow()

        projects_data = [
            {
                'project_name': 'Customer Portal Redesign',
                'description': 'Complete overhaul of the customer-facing portal using React and a modern design system.',
                'employee': inserted_employees[0],  # John Doe
                'status': 'Ongoing',
                'is_new': True,
                'days_ago': 2
            },
            {
                'project_name': 'Mobile App MVP',
                'description': 'Build the first version of the WorkForce mobile app for iOS and Android using Flutter.',
                'employee': inserted_employees[0],  # John Doe
                'status': 'Ongoing',
                'is_new': False,
                'days_ago': 15
            },
            {
                'project_name': 'Brand Identity Refresh',
                'description': 'Update brand guidelines, logo variants, and create a new design token system.',
                'employee': inserted_employees[1],  # Priya Sharma
                'status': 'Completed',
                'is_new': False,
                'days_ago': 30
            },
            {
                'project_name': 'Q4 Marketing Campaign',
                'description': 'Plan and execute the Q4 digital marketing campaign across social, email, and paid channels.',
                'employee': inserted_employees[2],  # Rahul Menon
                'status': 'Ongoing',
                'is_new': True,
                'days_ago': 1
            },
            {
                'project_name': 'API Gateway Migration',
                'description': 'Migrate legacy REST endpoints to a unified GraphQL API gateway with rate limiting.',
                'employee': inserted_employees[3],  # Sara Thomas
                'status': 'Ongoing',
                'is_new': False,
                'days_ago': 7
            },
            {
                'project_name': 'Annual Budget Forecast',
                'description': 'Prepare the 2025 annual budget forecast and department cost analysis report.',
                'employee': inserted_employees[4],  # Arun Kumar
                'status': 'Completed',
                'is_new': False,
                'days_ago': 45
            },
            {
                'project_name': 'Design System Documentation',
                'description': 'Document all UI components, usage guidelines, and accessibility notes in Storybook.',
                'employee': inserted_employees[1],  # Priya Sharma
                'status': 'Ongoing',
                'is_new': True,
                'days_ago': 0
            },
        ]

        for proj in projects_data:
            mongo.db.projects.insert_one({
                'project_name': proj['project_name'],
                'description': proj['description'],
                'employee_id': proj['employee']['emp_id'],
                'status': proj['status'],
                'is_new': proj['is_new'],
                'assigned_at': now - timedelta(days=proj['days_ago']),
                'assigned_by': hr_id
            })
            print(f"✅ Project '{proj['project_name']}' → {proj['employee']['name']} [{proj['status']}]")

        print("\n" + "="*55)
        print("🎉 WorkForce Hub database seeded successfully!")
        print("="*55)
        print("\n📋 LOGIN CREDENTIALS:")
        print(f"  HR Admin  →  admin@workforce.com  /  admin123")
        for data in employees_data:
            print(f"  Employee  →  {data['email']}  /  {data['password']}")
        print("\n🚀 Run: python app.py  →  http://localhost:5000")


if __name__ == '__main__':
    seed()