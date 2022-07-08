from flask import Flask, jsonify
import os
from src.constants.http_status_codes import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from flask_jwt_extended import JWTManager
from src.auth import auth
from src.activity import activity
from src.checkerIn import checkerIn
from src.database import db, Activity, TokenBlocklist
from datetime import timedelta

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
      app.config.from_mapping(
        SECRET_KEY = os.environ.get('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DB_URI"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY"),
        JWT_BLACKLIST_ENABLED = True,
        JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)

      )
    else:
      app.config.from_mapping(test_config)  

    @app.get("/")
    def index():
      return "app run"

    @app.get("/api")
    def say_hello():
      return jsonify({"message":"The API is ready develop"})

    db.app=app
    db.init_app(app)
    jwt = JWTManager(app)
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
      jti = jwt_payload["jti"]
      token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

      return token is not None
    app.register_blueprint(auth)
    app.register_blueprint(activity)
    app.register_blueprint(checkerIn)

    return app