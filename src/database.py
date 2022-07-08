from datetime import datetime
from email.policy import default
from enum import unique
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
  id=db.Column(db.Integer, primary_key =  True)
  NIK=db.Column(db.String(80), unique=True, nullable=False)
  email=db.Column(db.String(120), unique=True, nullable=False)
  password=db.Column(db.Text(), nullable=False)
  name=db.Column(db.Text(), nullable=False)  
  role=db.Column(db.Text(), nullable=False)
  created_at=db.Column(db.DateTime, default=datetime.now())
  activity=db.relationship('Activity', backref='user')
  checkerIn=db.relationship('CheckerIn', backref='user')

  def __repr__(self) -> str:
    return "User>>> {self.username}"


class Activity(db.Model):
  id=db.Column(db.Integer, primary_key =  True)
  user_id=db.Column(db.Integer, db.ForeignKey("user.id"))
  task=db.Column(db.Text(), nullable=False)
  desc=db.Column(db.Text(), nullable=False)
  work_time_start=db.Column(db.DateTime, nullable=False)
  work_time_end=db.Column(db.DateTime, nullable=False)

  def __repr__(self) -> str:
    return "Activity>>> {self.task}"

class CheckerIn(db.Model):
  id=db.Column(db.Integer, primary_key =  True)
  user_id=db.Column(db.Integer, db.ForeignKey("user.id"))
  is_checkIn = db.Column(db.Boolean, default=False)
  is_checkOut = db.Column(db.Boolean, default=False)
  checkIn_time = db.Column(db.DateTime)
  checkOut_time = db.Column(db.DateTime)

class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)