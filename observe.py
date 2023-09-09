from flask import Flask
from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import logging
from sqlalchemy import text
from pytz import timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://myapp6user:140286TakaHiro@localhost/myapp6db_1'
db = SQLAlchemy(app)

app.config['SQLALCHEMY_ECHO'] = True
app.logger.setLevel(logging.INFO)

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

@app.route('/')
def hello_world():
    return 'Hello, World! ggg!'

def check_rooms():
    app.logger.debug(f"SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS  check_rooms.")
    jst = timezone('Asia/Tokyo')
    current_jst_time = datetime.now(jst).replace(microsecond=0)
    app.logger.debug(f"aaaaaaaaaaaaaaaaa Current JST time: {current_jst_time}")
    timeout = current_jst_time - timedelta(minutes=0, seconds=15)
    app.logger.debug(f"aaaaaaaaaaaaaaaaa  Timeout value: {timeout}")
    with app.app_context():
        app.logger.debug(f"CCCCCCCCCCCCCCCCCCCCCCCCCCCCCC  In with context.")
        rooms = Room.query.filter(Room.last_heartbeat <= timeout).all()
        app.logger.debug(f"VVVVVVVVVVVVVVVVVVVVVVVVVVVVVV  Number of rooms fetched: {len(rooms)}")
        for room in rooms:
            app.logger.debug(f"DDDDDDDDDDDDDDDDDDDDDDDDDDDDDD  Deactivating room last_heartbeat: {room.last_heartbeat}")
            app.logger.debug(f"DDDDDDDDDDDDDDDDDDDDDDDDDDDDDD  Deactivating room: {room.roomID}")
            room.active = False
        db.session.commit()

scheduler = APScheduler()
scheduler.add_job(id='Scheduled task', func=check_rooms, trigger='interval', seconds=6)
scheduler.init_app(app)
scheduler.start()

if __name__ == '__main__':
    app.run()
