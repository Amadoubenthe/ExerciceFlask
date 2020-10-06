from sqlalchemy.orm import backref
from db import db


class ProjectModel(db.Model):
    __tablename__ = 'projects'

    __table_args__ = (
        db.UniqueConstraint('user_id', 'project_name', name='unique_project_name'),
    )

    id = db.Column(db.Integer, primary_key=True)
    project_name = db.Column(db.String(80))
    description = db.Column(db.String(80))
    is_archived = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    users = db.relationship('UserModel')
    
    tasks = db.relationship("TaskModel", back_populates="projects", cascade="all, delete")

    def __init__(self, project_name, description):
        self.project_name = project_name
        self.description = description
        self.is_archived = False

    def json(self):
        return {
            "project_id": self.id,
            "project_name": self.project_name,
            "description": self.description,
            "is_archived": self.is_archived,
        }

    def jsonTasks(self):
        return {
            'tasks': [task.json() for task in self.tasks]
        }          

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_by_name(cls, project_name):
        return cls.query.filter_by(project_name=project_name).first()    
    
    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
       