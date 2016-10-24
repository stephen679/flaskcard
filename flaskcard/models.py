from sqlalchemy import Column, Integer, String, Table, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

from flask_sqlalchemy import SQLAlchemy
from flaskcard import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    semesters = db.relationship('Semester', backref='person',lazy='dynamic')

    def __init__(self, username, password, first_name,last_name):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return '<User: %r (%r %r)>' % (self.username,self.first_name, self.last_name)

class Semester(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(String(10))
    year = db.Column(Integer)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id')) # attached to a user model
    courses = db.relationship('Course', backref='semester',lazy='dynamic') # one-to-many, Semester* to courses

    def __init__(self,season,year,user_id):
        self.season = season
        self.year = year
        self.user_id = user_id

    def __repr__(self):
        return '<Semester: %r %r>' % (self.season,self.year)

class Assignment(db.Model):
    pass

class Course(db.Model):
    pass
"""

class Semester(Base):
    __tablename__ = 'semesters'
    season = Column(String(10))
    year = Column(Integer)
    courses = relationship('Course')
    username = Column(String(80),ForeignKey('User.username'))

    def __init__(self, season, year, username):
        self.season = season
        self.year = year
        self.user = username

class Assignment(Base):
    __tablename__ = 'assignments'
    name = Column(String(128),primary_key=True)
    grade = Column(Float)
    category = Column(String(80))
    course = Column(String(80),ForeignKey('Course.coursename'))


class Course(Base):
    __tablename__ = 'courses'
    name = Column(String(80),primary_key=True)
    assignments = relationship('Assignment')"""
