import json
import boto3
import logging
import random

from enum import Enum, unique
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
# app.config['SQLALCHEMY_DATABASE_URI'] = connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/octank_aurora_db'

CORS(app, resources={r"/api/*": {"origins": "*"}})
db = SQLAlchemy(app)

kinesis = boto3.client("kinesis")


# event types
@unique
class EventType(Enum):
    LOGIN = 1
    LOGIN_FAILED = 2
    LOGOUT = 3
    DETAILS = 4
    TRAILER = 5
    WATCHING = 6
    FINISHED = 7


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


# fake the users table query (for local development w/o Postgres)
def query_users():
    return [
        user('Ana-0-20-MZ', 0, 20, 'MZ'),
        user('Bob-1-30-SW', 1, 30, 'SW'),
        user('Chloe-0-40-MP', 0, 40, 'MP'),
        user('Don-1-50-WP', 1, 50, 'WP'),
        user('Eve-0-25-SW', 0, 25, 'SW'),
        user('Flynn-1-35-MP', 1, 35, 'MP'),
        user('Gina-0-45-MZ', 0, 45, 'MZ'),
        user('Hugo-1-15-MZ', 1, 15, 'MZ')
    ]


# read all users to impersonate
@app.route('/api/users', methods=['GET'])
def read_users():
    return jsonify({
        # 'users': [user.serialize() for user in user.query.all()]
        'users': [user.serialize() for user in query_users()]
    }), 200


class show(db.Model):
    show = db.Column(db.String(64), primary_key=True)
    origin = db.Column(db.String(32), nullable=False)
    genre = db.Column(db.Integer, nullable=False)
    pgrating = db.Column(db.Integer, nullable=False)
    recommended = random.choice([True, False])

    def __init__(self, show, origin, genre, pgrating, recommended):
        self.show = show
        self.origin = origin
        self.genre = genre
        self.pgrating = pgrating
        self.recommended = recommended

    def serialize(self):
        return {
            'show': self.show,
            'origin': self.origin,
            'genre': self.genre,
            'pgrating': self.pgrating,
            'recommended': self.recommended
        }


# fake the shows table query (for local development w/o Postgres)
def query_shows():
    return [
        show('Avatar-AU-1-1', 'Austria', 1, '1', False),
        show('Breaking Bad-BR-2-2', 'Brasil', 2, '2', True),
        show('Chernobyl-CH-3-3', 'Chile', 3, '3', True),
        show('Dracula-DE-1-4', 'Denmark', 1, '4', False),
        show('Exorcist-AU-1-5', 'Austria', 1, '5', False),
        show('Family Guy-BR-2-1', 'Brasil', 2, '1', True),
        show('Goonies-CH-2-1', 'Chile', 2, '1', False),
        show('Home Alone-DE-1-2', 'Denmark', 1, '2', False)
    ]


# get all shows to watch
@app.route('/api/shows', methods=['GET'])
def read_shows():
    return jsonify({
        # 'shows': [show.serialize() for show in show.query.all()]
        'shows': [show.serialize() for show in query_shows()]
    }), 200


@app.route('/api/events', methods=['POST'])
def event_sink():
    # obligatory
    device_param = request.form.get('device', type=str)
    user_param = request.form.get('user', type=str)
    event_param = request.form.get('event', type=str)

    # optional
    show_param = request.form.get('show', default='', type=str)
    recommended_param = request.form.get('recommended', default=0, type=int)

    # event builder
    builder = {
        EventType.LOGIN.value: lambda: {
            'eventType': EventType.LOGIN.value,
            'deviceId': device_param,
            'userId': user_param
        },
        EventType.LOGIN_FAILED.value: lambda: {
            'eventType': EventType.LOGIN_FAILED.value,
            'deviceId': device_param,
            'userId': user_param
        },
        EventType.LOGOUT.value: lambda: {
            'eventType': EventType.LOGOUT.value,
            'deviceId': device_param,
            'userId': user_param
        },
        EventType.DETAILS.value: lambda: {
            'eventType': EventType.DETAILS.value,
            'deviceId': device_param,
            'userId': user_param,
            'showId': show_param,
            'recommended': recommended_param
        },
        EventType.TRAILER.value: lambda: {
            'eventType': EventType.TRAILER.value,
            'deviceId': device_param,
            'userId': user_param,
            'showId': show_param,
            'recommended': recommended_param
        },
        EventType.WATCHING.value: lambda: {
            'eventType': EventType.WATCHING.value,
            'deviceId': device_param,
            'userId': user_param,
            'showId': show_param,
            'recommended': recommended_param
        },
        EventType.FINISHED.value: lambda: {
            'eventType': EventType.FINISHED.value,
            'deviceId': device_param,
            'userId': user_param,
            'showId': show_param,
            'recommended': recommended_param
        }
    }

    # build event
    stream_event_builder = builder.get(int(event_param), lambda: {})
    json_load = json.dumps(stream_event_builder())
    print(json_load)

    # send event
    response = kinesis.put_record(
        StreamName="octank-kinesis-data-stream",
        Data=json_load,
        PartitionKey=user_param
    )

    # analyze response
    ordinal = response["SequenceNumber"]

    return jsonify({
        'seq': ordinal
    }), 201


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)