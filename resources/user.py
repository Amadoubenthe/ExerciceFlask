from flask import url_for
from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
import datetime
from itsdangerous import URLSafeTimedSerializer
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
)
import bcrypt
import re
from models.user import UserModel
from email_token import confirm_token, generate_confirmation_token
from send_emails import send_email


_user_parser = reqparse.RequestParser()
_user_parser.add_argument('email',
                    type=str,
                    required=True,
                    nullable=False,
                    )

_user_parser.add_argument('password',
                    type=str,
                    required=True,
                    nullable=False
                    )

_user_parser.add_argument('confirm_password',
                    type=str,
                    required=True,
                    nullable=False
                    )                   

class UserRegister(Resource):


    def post(self):

        data = _user_parser.parse_args()

        email = data['email']
        if not email:
            return {"message": "The email field is empty"}

        if UserModel.find_by_email(data['email']):
            return {"message": "A user with that email already exists"}, 400

        match_email = re.search(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email)
        if not match_email:
            return {"message": "Movaise email address"}    
            
        password = data['password']
        if not password:
            return {"message": "The password field is empty"}

        special_sym=['$','@','#']
 
        if len(password) < 8:
            return {"message": "the length of password should be at least 8 char long"}
        if not any(char.isdigit() for char in password):
            return {"message": "password must have at least one number"}
        if not any(char.isupper() for char in password):
            return {"message": "password must have at least one uppercase letter"}
        if not any(char.islower() for char in password):
            return {"message": "password must have at least one lowercase letter"}
        if not any(char in special_sym for char in password):
            return {"message": "the password must have at least one of the following symbols $@#"}

        confirm_password = data['confirm_password']
        if not confirm_password or confirm_password != password:
            return {"message": "Please confirm the password"}

        pwd_hashed = UserModel.make_password_hash(password)
        confirm_password_hased = UserModel.make_password_hash(confirm_password)

        user = UserModel(email=email, password=pwd_hashed, confirm_password=confirm_password_hased)

        user.save_to_db()

        token = generate_confirmation_token(user.email)
        print(token)
        subject = "Please confirm your email to be able to use our app."
        link = url_for("useractivateresource", token=token, _external=True)
        body = f"Hi, Thanks for using our app! Please confirm your registration by clicking on the link: {link} . Welcome to our family"
        send_email(user.email, subject, body)
        return {"message": "Thanks for registering!  Please check your email to confirm your email address, success."}, 201

        # try:
        #     user = UserModel(email=email, password=pwd_hashed, confirm_password=confirm_password_hased)

        #     user.save_to_db()

        #     token = generate_confirmation_token(user.email)
        #     print(token)
        #     subject = "Please confirm your email to be able to use our app."
        #     link = url_for("useractivateresource", token=token, _external=True)
        #     body = f"Hi, Thanks for using our app! Please confirm your registration by clicking on the link: {link} . Welcome to our family"
        #     send_email(user.email, subject, body)
        #     return {"message": "Thanks for registering!  Please check your email to confirm your email address, success."}, 201
        # except:
        #     return {'message': 'An error occured while creating the user.'}, 500


class User(Resource):
    
    @jwt_required
    def get(self, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User Not Found'}, 404
        return user.json(), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User Not Found'}, 404
        user.delete_from_db()
        return {'message': 'User deleted.'}, 200


class UserActivateResource(Resource):
    def get(self, token):
        email = confirm_token(token)
        if email is False:
            return {"message": "Invalid token or token expired"}, 400

        user = UserModel.find_by_email(email)

        if not user:
            return {"message": "User not found"}, 404  

        if user.email_confirmed is True:
            return {"message": "The user account is already activated"}, 400

        user.email_confirmed = True
        user.email_confirmed_on = datetime.datetime.now()
        user.save_to_db()
        access_token = create_access_token(identity=user.id, fresh=True)
        
        return {'access_token': access_token}, 200

class UserLogin(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('email',
                type=str,
                required=True,
                nullable=False,
                help="This field cannot be blank."
                )

    parser.add_argument('password',
                type=str,
                required=True,
                nullable=False,
                help="This field cannot be blank."
                )

    def post(self):
        data = UserLogin.parser.parse_args()
        email = data['email']
        if not email:
            return {"message": "The email field is empty"}

        user = UserModel.find_by_email(data['email'])

        password = data['password']
        if user.email_confirmed is False:
            return {'message': 'The user account is not activated yet'}, 403

        if bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):

            access_token = create_access_token(identity=user.id, fresh=True)
            return {
                'access_token': access_token
            }, 200

        return {"message": "Invalid Credentials!"}, 401