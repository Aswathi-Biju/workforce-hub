from flask_login import UserMixin
from bson import ObjectId

class User(UserMixin):

    def __init__(self, user_doc):
        self.id = str(user_doc['_id'])
        self.name = user_doc.get('name', '')
        self.email = user_doc.get('email', '')
        self.password = user_doc.get('password', '')
        self.role = user_doc.get('role', 'Employee')

    def is_hr(self):
        return self.role == 'HR'

    @staticmethod
    def get_by_id(user_id):
        from app import mongo
        try:
            user_doc = mongo.db.users.find_one({'_id': ObjectId(user_id)})
            if user_doc:
                return User(user_doc)
        except Exception:
            pass
        return None

    @staticmethod
    def get_by_email(email):
        from app import mongo
        return mongo.db.users.find_one({'email': email})