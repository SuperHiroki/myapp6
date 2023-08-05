from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(240), unique=True, nullable=False)
    password = db.Column(db.String(360), nullable=False)
    userLevel = db.Column(db.Integer, nullable=False)
    characters = db.relationship('Character', backref='owner_rel', lazy=True)
    rooms = db.relationship('Room', backref='host_rel', lazy=True)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    characterId = db.Column(db.Integer, nullable=False)
    characterLevel = db.Column(db.Integer, nullable=False)
    owner = db.Column(db.String(240), db.ForeignKey('user.username'), nullable=False)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roomID = db.Column(db.String(360), nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    host = db.Column(db.String(240), db.ForeignKey('user.username'), nullable=False)
    last_heartbeat = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=False)