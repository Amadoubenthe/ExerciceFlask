import bcrypt
from db import db
class UserModel(db.Model):
     
    __tablename__ = 'users'
 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    confirm_password = db.Column(db.String(80), nullable=False)
    email_confirmed = db.Column(db.Boolean, nullable=True, default=False)
    email_confirmed_on = db.Column(db.DateTime, nullable=True)

    projects = db.relationship('ProjectModel', lazy='dynamic')

    tasks = db.relationship('TaskModel', lazy='dynamic')
 
    def __init__(self, email, password, confirm_password):
        self.email = email
        self.password = password
        self.confirm_password = confirm_password
        self.email_confirmed = False

    def json(self):
        return {
            'id': self.id,
            'email': self.email
        }
            
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()    

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()    

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @staticmethod
    def make_password_hash(password):
        hash = bcrypt.hashpw(password=password.encode('utf-8'), salt=bcrypt.gensalt())
        return hash.decode('utf-8')

    @staticmethod    
    def is_password_valid(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))