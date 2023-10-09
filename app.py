from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta
from sqlalchemy import text
from pytz import timezone
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://myapp6user:140286TakaHiro@localhost/myapp6db_1'
db = SQLAlchemy(app)

app.logger.setLevel(logging.DEBUG)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(240), unique=True, nullable=False)
    password = db.Column(db.String(360), nullable=False)
    userLevel = db.Column(db.Integer, nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    magicStone = db.Column(db.Integer, nullable=False)
    characters = db.relationship('Character', backref='owner_rel', lazy=True)
    rooms = db.relationship('Room', backref='host_rel', lazy=True)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    characterId = db.Column(db.Integer, nullable=False)
    characterLevel = db.Column(db.Integer, nullable=False)
    awakening = db.Column(db.Integer, nullable=False)
    reliability = db.Column(db.Integer, nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    owner = db.Column(db.String(240), db.ForeignKey('user.username'), nullable=False)

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roomID = db.Column(db.String(360), nullable=False)
    active = db.Column(db.Boolean, nullable=False)
    host = db.Column(db.String(240), db.ForeignKey('user.username'), nullable=False)
    last_heartbeat = db.Column(db.DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=False)

@app.route('/', methods=['GET'])
def home():
    return "Hello Hiroki Hiroki Super"

@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    user = User.query.options(joinedload(User.characters)).filter_by(username=username).first()
    if user:
        user_data = {
            'Username': user.username,
            'Password': user.password,
            'UserLevel': user.userLevel,
            'Experience': user.experience,
            'MagicStone': user.magicStone,
            'Characters': [{'CharacterId': c.characterId, 'CharacterLevel': c.characterLevel, 'Awakening': c.awakening, 'Reliability': c.reliability, 'Experience': c.experience} for c in user.characters]
        }
        return jsonify(user_data)
    else:
        return jsonify({'Content': 'User not found!'}), 404

@app.route('/user', methods=['POST'])
def add_user():
    data = request.get_json()
    if User.query.filter_by(username=data['Username']).first():
        return jsonify({'Content': 'Username already exists.'}), 400
    new_user = User(username=data['Username'], password=data['Password'], userLevel=1, experience=0, magicStone=0)
    new_character = Character(characterId=0, characterLevel=3, awakening=0, reliability=0, experience=0, owner=data['Username'])
    new_character_2 = Character(characterId=1, characterLevel=5, awakening=0, reliability=0, experience=0, owner=data['Username'])
    new_character_3 = Character(characterId=2, characterLevel=4, awakening=0, reliability=0, experience=0, owner=data['Username'])
    db.session.add(new_user)
    db.session.add(new_character)
    db.session.add(new_character_2)
    db.session.add(new_character_3)
    db.session.commit()
    return jsonify({'Content': 'User added!'}), 201

@app.route('/room', methods=['GET'])
def get_rooms():
    active_rooms = Room.query.filter_by(active=True).all()
    if active_rooms:
        rooms = [{'RoomId': r.roomID, 'Host': r.host} for r in active_rooms]
        return jsonify(rooms)#リスト型で送信しちゃった
    else:
        return jsonify({'Content': 'No active rooms.'}), 404
    
@app.route('/room', methods=['POST'])
def add_room():
    app.logger.debug(f"AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA  add_room.")
    data = request.get_json()
    room = Room.query.filter_by(roomID=data['RoomId']).first()
    if room:
        room.active = True
        db.session.commit()
        return jsonify({'Content': 'Room activity updated!'}), 200
    else:
        new_room = Room(roomID=data['RoomId'], active=True, host=data['Host'])
        db.session.add(new_room)
        db.session.commit()
        return jsonify({'Content': 'Room added!'}), 201
    
@app.route('/room/<roomId>/heartbeat', methods=['POST'])
def room_heartbeat(roomId):
    room = Room.query.filter_by(roomID=roomId).first()
    if room:
        jst = timezone('Asia/Tokyo')
        current_jst_time = datetime.now(jst).replace(microsecond=0)
        room.last_heartbeat = current_jst_time
        db.session.commit()
        return jsonify({'Content': 'Heartbeat received.'}), 200
    else:
        return jsonify({'Content': 'Room not found.'}), 404

@app.route('/user/save', methods=['POST'])
def save_user_data():
    data = request.get_json()
    if not data:
        return jsonify({'Content': 'Bad Request'}), 400
    username = data.get('Username')
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'Content': 'User not found!'}), 404
    # ユーザの基本情報をアップデート
    user.userLevel = data.get('UserLevel')
    user.experience = data.get('Experience')
    user.magicStone = data.get('MagicStone')
    # キャラクター情報のアップデート
    for char_data in data.get('Characters'):
        character = Character.query.filter_by(owner=username, characterId=char_data.get('CharacterId')).first()
        if character:
            character.characterLevel = char_data.get('CharacterLevel')
            character.awakening = char_data.get('Awakening')
            character.reliability = char_data.get('Reliability')
            character.experience = char_data.get('Experience')
        else:
            new_character = Character(characterId=char_data.get('CharacterId'), characterLevel=char_data.get('CharacterLevel'), awakening=char_data.get('Awakening'), reliability=char_data.get('Reliability'), experience=char_data.get('Experience'), owner=username )
            db.session.add(new_character)
    try:
        db.session.commit()
    except Exception as e:
        app.logger.error(f"Failed to save user data: {str(e)}")
        db.session.rollback()
        return jsonify({'Content': 'Internal Server Error'}), 500
    return jsonify({'Content': 'User data updated successfully'}), 201


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)


