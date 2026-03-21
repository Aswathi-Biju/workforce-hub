from flask import Flask, render_template
from flask_pymongo import PyMongo
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'workforce-hub-secret-key-123')
app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/workforce_hub')

mongo = PyMongo(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

from routes.auth import auth_bp
from routes.employee import employee_bp
from routes.project import project_bp

app.register_blueprint(auth_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(project_bp)

@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=False)
