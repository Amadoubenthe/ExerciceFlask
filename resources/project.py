from flask import jsonify
from flask_restful import Resource, reqparse
from sqlalchemy import func, desc
from flask_jwt_extended import jwt_required, get_jwt_identity

from db import db

from models.project import ProjectModel
from models.task import TaskModel

class Project(Resource):

    parser = reqparse.RequestParser()

    parser.add_argument(
                        'project_name',
                        type=str,
                        required=False,
                        nullable=True
                        )

    parser.add_argument(
                        'description',
                        type=str,
                        required=False,
                        nullable=True
                        )

    @jwt_required                   
    def get(self, id) :
        project = ProjectModel.find_by_id(id)
        current_user_id = get_jwt_identity()

        if not project:
            return {"message": "project not found"}, 404

        if current_user_id == project.user_id:
            project_id = project.id
            preject_name = project.project_name
            description = project.description
            is_archived = project.is_archived
            return {
                "project_id": project_id,
                "project_name": preject_name,
                "description": description,
                "is_archived": is_archived
            }, 200

        return {"message": "Unauthorized"}, 401

    @jwt_required    
    def post(self):
        data = Project.parser.parse_args()
        current_user_id = get_jwt_identity()

        project_name = data["project_name"] 
        if not project_name:
            return {"message": "Please enter the project name"}

        description = data['description']

        try:
            project = ProjectModel(**data)
            project.user_id = get_jwt_identity()
            project.is_archived = False
            project.save_to_db()
            print("moi", project.user_id)
        except:
            return {"message": "An error occured creating the Project"}, 500

        project_id = project.id    
        project_name = project.project_name
        description = project.description 
        is_archived = project.is_archived  
        return {
            "project_id": project_id,
            "project_name": project_name,
            "description": description,
            "is_archived": is_archived
        }, 201

    @jwt_required        
    def put(self, id):
        current_user_id = get_jwt_identity()
        project = ProjectModel.find_by_id(id)
        if not project:
            return {"message": "project not found"}, 404
        if current_user_id != project.user_id:
            return {"message": "Unauthorized"}, 401

        data = Project.parser.parse_args()
        project_name = data["project_name"] 
        if not project_name:
            project_name = project.project_name

        description = data['description']    
        if not description:
            description = project.description  

        try:
            project.project_name = project_name
            project.description = description
            project.save_to_db()
        except:
            return {"message": "An error occured updating the Project"}, 500

        project_id = project.id    
        project_name = project.project_name
        description = project.description 
        is_archived = project.is_archived 
        return {
            "project_id": project_id,
            "project_name": project_name,
            "description": description,
            "is_archived": is_archived
        }, 201    
    
    @jwt_required
    def delete(self, id):
        current_user_id = get_jwt_identity()
        project = ProjectModel.find_by_id(id)
        if not project:
            return {"message": "project not found"}, 404

        if project.user_id != current_user_id:
            return {"message": "Unauthorized"}, 401
            
        project.delete_from_db()

        return {"message": "Project deleted"}, 200    

class ProjectList(Resource):
    @jwt_required
    def get(self):
        current_user_id = get_jwt_identity()

        if current_user_id:
            projects = [x.json() for x in ProjectModel.query.filter(ProjectModel.user_id==current_user_id).all()]

            nomber_project = len(projects)
            return {
                "nomber_project": nomber_project,
                "project": projects
            }, 200

class ProjectStat(Resource):
    @jwt_required
    def get(self, id):

        current_user_id = get_jwt_identity()
        project = ProjectModel.find_by_id(id)

        if not project:
            return {"message": "project not found"}, 404

        if project.user_id != current_user_id:
            return {"message": "Unauthorized"}, 401
        
        number_tasks = (db.session.query(
                func.count(TaskModel.id).label('total_task'))
                .join(ProjectModel, TaskModel.project_id == ProjectModel.id)
                .filter(TaskModel.project_id == project.id)
                .filter(TaskModel.user_id==current_user_id)
                .scalar()
                )

        number_tasks_termined = (db.session.query(
                func.count(TaskModel.id).label('total_task_temined'))
                .filter(TaskModel.project_id == project.id)
                .filter(TaskModel.status == False)
                .filter(TaskModel.user_id==current_user_id)
                .scalar()
                )
        
        if number_tasks == 0:
            return {"message": "Not task"}
            
        percentage = number_tasks_termined*100/number_tasks
        
        return {
            "number_tasks": number_tasks,
            "number_tasks_termined": number_tasks_termined,
            "percentage": percentage

        }, 200

class ArchiveProject(Resource):
    @jwt_required
    def get(self, id):

        current_user_id = get_jwt_identity()
        project = ProjectModel.find_by_id(id)

        if not project:
            return {"message": "project not found"}, 404

        if project.is_archived == True:
            return {"message": "project already archived"} 

        if project.user_id != current_user_id:
            return {"message": "Unauthorized"}, 401

        project.is_archived = True
        project.save_to_db()
        
        return {"message": "Project Archived"}, 200


class StatProject(Resource):
    @jwt_required
    def get(self, id):
        current_user_id = get_jwt_identity()
        project = ProjectModel.find_by_id(id)
        if not project:
            return {"message": "project not found"}, 404
        if project.is_archived == True:
            return {"message": "project already archived"}  
        if project.user_id != current_user_id:
            return {"message": "Unauthorized"}, 401

        # tasks = Comment.query.filter_by(thread_id=thread.id)\
        #                         .order_by(Comment.created_at.desc())\
        #                         .all() 


        tasks = TaskModel.query.filter(TaskModel.project_id==id)\
                                .all()

        print(tasks)                                           

        # current_user_id = get_jwt_identity()
        # if current_user_id:
        #     tasks = [x.json() for x in TaskModel.query.filter(TaskModel.user_id==current_user_id).all()]
        # 

        # task_termined = [r._asdict() for r in tasks]

        for row in tasks:
            print(row)


        return {"message":"project_task_termined"}, 200                                                   
        
        # return jsonify(tasks), 200
