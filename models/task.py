from sqlalchemy.orm import backref
from db import db

class TaskModel(db.Model):
    __tablename__ = 'tasks'
 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task_name = db.Column(db.String(80), nullable=False)
    status = db.Column(db.Boolean, default=True)
    termined_at = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    users = db.relationship('UserModel')

    project_id = db.Column(db.Integer, db.ForeignKey("projects.id", ondelete="cascade"))
    projects = db.relationship('ProjectModel', back_populates="tasks")

    def __init__(self, task_name, status, project_id):
        self.task_name = task_name
        self.status = status
        self.project_id = project_id


    def json(self):
        return {
            'task_id': self.id,
            'project_id': self.project_id,
            'task_name': self.task_name,
            'status': self.status
        }

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()      