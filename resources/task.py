from flask_restful import Resource, reqparse
from sqlalchemy import func, desc
from flask_jwt_extended import jwt_required, get_jwt_identity

import datetime

from db import db

from models.task import TaskModel
from models.project import ProjectModel


class Task(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument(
                        'task_name',
                        type=str,
                        required=False,
                        nullable=False,
                    )
              
    parser.add_argument("status",
                        type=bool,
                        required=False,
                        nullable=False,
                        )

    parser.add_argument(
                        'project_id',
                        type=int,
                        required=False,
                        nullable=False,
                    )                                    
    @jwt_required
    def get(self, id):
        current_user_id = get_jwt_identity()
        task = TaskModel.find_by_id(id)
        if not task:
            return {"message": "task not found"}, 404
        if current_user_id == task.user_id:
            task_id = task.id
            task_name = task.task_name
            return {
                "task_id": task_id,
                "task_name": task_name
            }, 200
        return {"message": "Unauthorized"}, 401

    @jwt_required
    def post(self):

        data = Task.parser.parse_args()
        current_user_id = get_jwt_identity()
        

        task_name = data["task_name"] 
        if not task_name:
            return {"message": "Please enter the name of task 'task_name' "}

        status = data["status"]   

        project_id = data["project_id"] 
        if not project_id:
            return {"message": "Please enter the id of project 'project_id' "}   

        project = ProjectModel.find_by_id(project_id)
        
        if not project:
            return {"message": "project not found"}, 404

        if current_user_id != project.user_id:
            return {"message": "Unauthorized"}, 401

            
        if project.is_archived == True:
            return {"message": "Project Closed"}, 401

        try:
            task = TaskModel(**data)
            task.user_id = get_jwt_identity()
            task.save_to_db()

        except:
            return {"message": "An error occured creating the Task"}, 500

        task_id = task.id    
        task_name = task.task_name
        status = task.status
        return {
            "task_id": task_id,
            "task_name": task_name,
            "status": status
        }, 201

    @jwt_required    
    def put(self, id):
        current_user_id = get_jwt_identity()
        task = TaskModel.find_by_id(id)
        if not task:
            return {"message": "task not found"}, 404
        if current_user_id != task.user_id:
            return {"message": "Unauthorized"}, 401

        data = Task.parser.parse_args()

        task_name = data['task_name']    
        if not task_name:
            task_name = task.task_name

        project_id = task.project_id

        project = ProjectModel.find_by_id(project_id)
        if not project:
            return {"message": "project not found"}, 404

        print("Projet archiver",project.is_archived)

        if project.is_archived:
            return {"message": "Close Unauthorized"}, 401

        status = data['status']

        if status:
            task.status = status

        status = task.status

        try:
            task.task_name = task_name
            task.status = status
            task.save_to_db()
        except :
            return {"message": "An error occured creating the Project"}, 500

        project_id = task.project_id    
        status = task.status
        task_name = task.task_name    
        return {
            "project_id": project_id,
            "task_name": task_name,
            "status": status
            }, 201

    @jwt_required
    def delete(self, id):
        current_user_id = get_jwt_identity()
        task = TaskModel.find_by_id(id)
        if not task:
            return {"message": "task not found"}, 404
        if task.user_id != current_user_id:
            return {"message": "Unauthorized"}, 401
        task.delete_from_db()
        return {"message": "Task deleted"}


class CompleteTask(Resource):
    @jwt_required
    def get(self, id):
        current_user_id = get_jwt_identity()
        task = TaskModel.find_by_id(id)
        if not task:
            return {"message": "task not found"}, 404
        if task.status == False:
            return {"message": "Task aleready completed"} 
        if task.user_id != current_user_id:
            return {"message": "Unauthorized"}, 401
        task.status = False
        task.termined_at = datetime.datetime.now()
        task.save_to_db()
        return {"message": "Task completed"}

class TaskList(Resource):
    @jwt_required
    def get(self):
        current_user_id = get_jwt_identity()
        if current_user_id:
            tasks = [x.json() for x in TaskModel.query.filter(TaskModel.user_id==current_user_id).all()]
            nomber_task = len(tasks)
            return {
                "nomber_task": nomber_task,
                "tasks": tasks
            }, 200

class Statistic(Resource):
    @jwt_required
    def get(self):
        current_user_id = get_jwt_identity()
        print(current_user_id)

        qry = (db.session.query(ProjectModel.project_name.label('project_name'),
                func.count(TaskModel.status).label('total_task_termined'))
                .join(ProjectModel, TaskModel.project_id == ProjectModel.id).filter(TaskModel.status == False)
                .filter(TaskModel.user_id==current_user_id)
                .group_by(TaskModel.project_id)
                .order_by(desc('total_task_termined')).all()
                )


        project_task_termined = [r._asdict() for r in qry]      
        return {
            "project_task_termined": project_task_termined,
        }, 200

class StatisticPeriode(Resource):
    @jwt_required
    def get(self, date_debut, date_fin):
        current_user_id = get_jwt_identity()
        qry = (db.session.query(ProjectModel.project_name.label('project_name'),
                func.count(TaskModel.status).label('total_task_termined'))
                .join(ProjectModel, TaskModel.project_id == ProjectModel.id).filter(TaskModel.status==False)
                .filter(TaskModel.termined_at.between(date_debut,date_fin))
                .filter(TaskModel.user_id==current_user_id)
                .group_by(TaskModel.project_id)
                .order_by(desc('total_task_termined')).all()
                )

        project_task_termined = [r._asdict() for r in qry]        
        return {"project_task_termined": project_task_termined}, 200   

class BestTaskTermined(Resource):
    @jwt_required
    def get(self):
        current_user_id = get_jwt_identity()
        qry = (db.session.query(ProjectModel.project_name,ProjectModel.description.label('project_name'),
                func.count(TaskModel.status).label('total_task_termined'))
                .join(ProjectModel, TaskModel.project_id == ProjectModel.id).filter(TaskModel.status == False)
                .filter(TaskModel.user_id==current_user_id)
                .group_by(TaskModel.project_id)
                .order_by(desc('total_task_termined')).limit(1).all()
                )

        best_project = {}        
        for row in qry:
            best_project = {"project_name":row[0], "project_description":row[1], "task_termined":row[2]}

        return {
            "best_project": best_project,
            }, 200

class BestTaskTerminedInterval(Resource):
    @jwt_required
    def get(self, date_debut, date_fin):
        current_user_id = get_jwt_identity()

        qry = (db.session.query(ProjectModel.project_name,ProjectModel.description.label('project_name'),
                func.count(TaskModel.status).label('total_task_termined'))
                .join(ProjectModel, TaskModel.project_id == ProjectModel.id).filter(TaskModel.status == False)
                .filter(TaskModel.termined_at.between(date_debut,date_fin))
                .filter(TaskModel.user_id==current_user_id)
                .group_by(TaskModel.project_id)
                .order_by(desc('total_task_termined')).limit(1).all()
                )           

        best_project = {}
        for row in qry:
            best_project = {"project_name":row[0], "project_description":row[1], "task_termined":row[2]}

        return {
            "best_project": best_project,
            }, 200