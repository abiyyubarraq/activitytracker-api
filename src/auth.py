from os import access
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_409_CONFLICT
from flask import Blueprint, app, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity, get_jwt
from flasgger import swag_from
from src.database import User, db, TokenBlocklist
from datetime import datetime
from datetime import timedelta
from datetime import timezone


auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")
blacklist = set()


@auth.post('/register')
@swag_from('./docs/auth/register.yaml')
def register():
    NIK = request.json['NIK']
    email = request.json['email']
    password = request.json['password']
    name= request.json['name']
    role = request.json['role']
    created_at = datetime.now(timezone.utc)

    if len(password) < 6:
        return jsonify({'error': "Password is too short"}), HTTP_400_BAD_REQUEST

    if len(NIK) < 3:
        return jsonify({'error': "User NIK is too short"}), HTTP_400_BAD_REQUEST

    if not NIK.isalnum() or " " in NIK:
        return jsonify({'error': "NIK should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

    if User.query.filter_by(NIK=NIK).first() is not None:
        return jsonify({'error': "NIK is taken"}), HTTP_409_CONFLICT

    pwd_hash = generate_password_hash(password)

    user = User(NIK=NIK, password=pwd_hash, email=email, name=name, role=role, created_at=created_at)
    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': "User created success",
        'user': {
            'NIK': NIK, "email": email
        }

    }), HTTP_201_CREATED


@auth.post('/login')
@swag_from('./docs/auth/login.yaml')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    user = User.query.filter_by(email=email).first()

    if user:
        is_pass_correct = check_password_hash(user.password, password)

        if is_pass_correct:
            refresh = create_refresh_token(identity=user.id)
            access = create_access_token(identity=user.id)

            return jsonify({
                'user': {
                    'refresh': refresh,
                    'access': access,
                    'NIK': user.NIK,
                    'email': user.email
                }

            }), HTTP_200_OK

    return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED


@auth.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        'NIK': user.NIK,
        'email': user.email
    }), HTTP_200_OK



@auth.route('/logout', methods=['DELETE'])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    now = datetime.now(timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    return jsonify(msg="JWT revoked")



@auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        'access': access
    }), HTTP_200_OK
