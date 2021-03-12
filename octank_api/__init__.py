import json
import boto3
import logging

from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ

app = Flask(__name__, instance_relative_config=True)

endpoint = environ.get('OCTANK_AURORA_ENDPOINT')
dbname = environ.get('OCTANK_AURORA_DBNAME')
username = 'postgres'
password = environ.get('OCTANK_AURORA_PASSWORD')
connection = f'postgresql://{username}:{password}@{endpoint}/{dbname}'
app.config['SQLALCHEMY_DATABASE_URI'] = connection # 'postgresql://postgres:postgres@localhost/octank_aurora_db'

CORS(app, resources={r"/api/*": {"origins": "*"}})
db = SQLAlchemy(app)

kinesis = boto3.client("kinesis")

# health check
@app.route('/', methods=['GET'])
def health_check():
    return jsonify({}), 200


class user(db.Model):
    user = db.Column(db.String(64), primary_key=True)
    gender = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    state = db.Column(db.String(16), nullable=False)

    def __init__(self, user, gender, age, state):
        self.user = user
        self.gender = gender
        self.age = age
        self.state = state

    def serialize(self):
        return {
            'user': self.user,
            'gender': self.gender,
            'age': self.age,
            'state': self.state
        }


# read all users to impersonate
@app.route('/api/users', methods=['GET'])
def read_users():
    return jsonify({
        'users': [user.serialize() for user in user.query.all()]
    }), 200


class show(db.Model):
    show = db.Column(db.String(64), primary_key=True)
    origin = db.Column(db.String(32), nullable=False)
    genre = db.Column(db.Integer, nullable=False)
    pgrating = db.Column(db.Integer, nullable=False)

    def __init__(self, show, origin, genre, pgrating):
        self.show = show
        self.origin = origin
        self.genre = genre
        self.pgrating = pgrating

    def serialize(self):
        return {
            'show': self.show,
            'origin': self.origin,
            'genre': self.genre,
            'pgrating': self.pgrating
        }


# get all shows to watch
@app.route('/api/shows', methods=['GET'])
def read_shows():
    return jsonify({
        'shows': [show.serialize() for show in show.query.all()]
    }), 200


@app.route('/api/watching', methods=['POST'])
def watching_heartbeat():
    user_param = request.args.get('user', type = str)
    show_param = request.args.get('show', type = str)
    session_param = request.args.get('session', default = "session1", type = str)

    app.logger.warning("User: {}".format(user_param))
    app.logger.warning("Show: {}".format(show_param))
    app.logger.warning("Session: {}".format(session_param))

    # build event
    stream_event = {
        'user': user_param,
        'show': show_param,
        'session': session_param,
        'timestamp': datetime.now().isoformat()
    }

    # send event
    response = kinesis.put_record(
        StreamName = "OctankKinesisDataStream",
        Data = json.dumps(stream_event),
        PartitionKey = session_param
    )

    # analyze response
    ordinal = response["SequenceNumber"]

    return jsonify({
        'seq': ordinal
    }), 201

  
if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port = 80)