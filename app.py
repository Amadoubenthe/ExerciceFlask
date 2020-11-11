from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_mail import Mail, Message

from db import db

from resources.user import UserRegister, User, UserLogin, UserActivateResource
from resources.project import Project, ProjectList, ArchiveProject, ProjectStat, StatProject
from resources.task import Task, TaskList, Statistic, CompleteTask, StatisticPeriode, BestTaskTermined, BestTaskTerminedInterval

import datetime

# app = Flask(__name__)
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root''@localhost/test_db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['PROPAGATE_EXCEPTIONS'] = True
# # app.config['MAIL_SERVER']="smtp.gmail.com"
# app.config['MAIL_SERVER']="localhost"
# # app.config['MAIL_PORT'] = 465
# app.config['MAIL_PORT'] = 1025
# app.config['MAIL_USERNAME'] = 'benthebagnan@gmail.com'
# app.config['MAIL_PASSWORD'] = 'NeenanDiaraye123@'

# # app.config['MAIL_USE_TLS'] = False
# # app.config['MAIL_USE_SSL'] = True

# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
# app.config['SECRET_KEY'] = "diallo"
# app.config['SECURITY_PASSWORD_SALT']='gfghtt6884@@%68848@$$@yygb'
# app.config['MAIL_DEFAULT_SENDER']='benthebagnan@gmail.com'

# api = Api(app)

# mail = Mail(app)
# mail.init_app(app)

# @app.before_first_request
# def create_tables():
#     db.create_all()

# jwt = JWTManager(app)


from db import db
app = Flask(__name__)
mail = Mail(app)

db.init_app(app)

# # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost:""/db'
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root''@localhost/flask_project'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SECRET_KEY'] = 'nadia@'
# app.config['MAIL_SERVER'] = 'localhost'
# app.config['MAIL_PORT'] = 1025
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USE_SSL'] = False
# app.config['MAIL_USERNAME'] = None
# app.config['MAIL_PASSWORD '] = None
# app.config['MAIL_DEFAULT_SENDER'] = 'nksz.fee00@gmail.com'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data3.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'nadia@'   
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(minutes=60)
app.config['MAIL_SERVER'] = 'localhost'
app.config['MAIL_PORT'] = 1025
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'benthebagnan@gmail.com'
app.config['MAIL_PASSWORD '] = 'NeenanDiaraye123@'
app.config['MAIL_DEFAULT_SENDER'] = 'benthebagnan@gmail.com'
app.config['SECURITY_PASSWORD_SALT'] = 'gfghtt6884@@%68848@$$@yygb'

api = Api(app)
mail.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()
    
jwt = JWTManager(app)




@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({
        'message': 'The token has expired.',
        'error': 'token_expired'
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({
        'message': 'Signature verification failed.',
        'error': 'invalid_token'
    }), 401


@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({
        "description": "Request does not contain an access token.",
        'error': 'authorization_required'
    }), 401


@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
    return jsonify({
        "description": "The token is not fresh.",
        'error': 'fresh_token_required'
    }), 401


@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({
        "description": "The token has been revoked.",
        'error': 'token_revoked'
    }), 401


api.add_resource(UserRegister, '/register')

api.add_resource(StatProject, '/projects/<int:id>/stat')


api.add_resource(UserActivateResource, '/users/activate/<string:token>')
api.add_resource(UserLogin, '/login')
api.add_resource(User, '/users/<int:user_id>')
api.add_resource(ProjectList, '/projects')
api.add_resource(ProjectStat, '/projects/<int:id>/statistic')
api.add_resource(ArchiveProject, '/projects/<int:id>/archive_projects')
api.add_resource(CompleteTask, '/tasks/<int:id>/complete_task')
api.add_resource(BestTaskTermined, '/best_task_termined')
api.add_resource(BestTaskTerminedInterval, '/projects/tasks/<string:date_debut>/<string:date_fin>/stat')
api.add_resource(Statistic, '/projects/tasks')
api.add_resource(StatisticPeriode, '/tasks/<string:date_debut>/<string:date_fin>')
api.add_resource(Project, '/projects', '/projects/<int:id>')
api.add_resource(TaskList, '/tasks')


api.add_resource(Task, '/projects/tasks', '/projects/tasks/<int:id>')

# '/projects/<int:id>/tasks'

if __name__ == '__main__':

    db.init_app(app)
    app.run(port=5000, debug=True)