import json
import boto3
import logging
import random

from datetime import datetime
from enum import Enum, unique
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from os import environ

from opentelemetry import propagate, trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter
)

from opentelemetry.instrumentation.botocore import BotocoreInstrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from opentelemetry.propagators.aws import AwsXRayPropagator
from opentelemetry.sdk.extension.aws.trace import AwsXRayIdGenerator

propagate.set_global_textmap(AwsXRayPropagator())

otlp_exporter = OTLPSpanExporter(endpoint="http://localhost:4317")
span_processor = BatchSpanProcessor(otlp_exporter)
trace.set_tracer_provider(
    TracerProvider(
        active_span_processor=span_processor,
        id_generator=AwsXRayIdGenerator(),
        # resource=get_aggregated_resources(
        #     [
        #         AwsEc2ResourceDetector(),
        #     ]
        # ),
    )
)

app = Flask(__name__, instance_relative_config=True)

BotocoreInstrumentor().instrument()
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
tracer = trace.get_tracer(__name__)

endpoint = environ.get('OCTANK_AURORA_ENDPOINT')
dbname = environ.get('OCTANK_AURORA_DBNAME')
username = 'postgres'
password = environ.get('OCTANK_AURORA_PASSWORD')
connection = f'postgresql://{username}:{password}@{endpoint}/{dbname}'
app.config['SQLALCHEMY_DATABASE_URI'] = connection
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/octank_aurora_db'

function_name = environ.get('OCTANK_FUNCTION_NAME')

CORS(app, resources={r"/api/*": {"origins": "*"}})
db = SQLAlchemy(app)

kinesis = boto3.client("kinesis")
lambda_ = boto3.client("lambda")

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
    # with tracer.start_as_current_span("health-check"):
    return jsonify({}), 200


class user(db.Model):
    user = db.Column(db.String(64), primary_key=True)
    gender = db.Column(db.Integer, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    state = db.Column(db.String(16), nullable=False)

    def __init__(self, user, gender, age, state):
        with tracer.start_as_current_span("user-init"):
            self.user = user
            self.gender = gender
            self.age = age
            self.state = state

    def serialize(self):
        with tracer.start_as_current_span("user-serialize"):
            return {
                'user': self.user,
                'gender': self.gender,
                'age': self.age,
                'state': self.state
            }


# fake the users table query (for local development w/o Postgres)
def query_users():
    with tracer.start_as_current_span("query-hardcoded-users"):
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
    with tracer.start_as_current_span("read-users"):
        span = trace.get_current_span()
        span.add_event("All the users!")
        return jsonify({
            'users': [user.serialize() for user in user.query.all()]
            # 'users': [user.serialize() for user in query_users()]
        }), 200


class show(db.Model):
    show = db.Column(db.String(64), primary_key=True)
    origin = db.Column(db.String(32), nullable=False)
    genre = db.Column(db.Integer, nullable=False)
    pgrating = db.Column(db.Integer, nullable=False)

    def __init__(self, show, origin, genre, pgrating):
        with tracer.start_as_current_span("show-init"):
            self.show = show
            self.origin = origin
            self.genre = genre
            self.pgrating = pgrating

    def serialize(self):
        with tracer.start_as_current_span("show-serialize"):
            return {
                'show': self.show,
                'origin': self.origin,
                'genre': self.genre,
                'pgrating': self.pgrating,
                'recommended': random.choice([True, False])
            }


# fake the shows table query (for local development w/o Postgres)
def query_shows():
    with tracer.start_as_current_span("query-hardcoded-shows"):
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
    with tracer.start_as_current_span("read-shows"):
        span = trace.get_current_span()
        span.add_event("All the shows!")
        return jsonify({
            'shows': [show.serialize() for show in show.query.all()]
            # 'shows': [show.serialize() for show in query_shows()]
        }), 200


@app.route('/api/events', methods=['POST'])
def event_sink():
    with tracer.start_as_current_span("event-sink") as span:
        # obligatory
        device_param = request.form.get('device', type=str)
        user_param = request.form.get('user', type=str)
        event_param = request.form.get('event', type=str)
        span.set_attribute("device", device_param)

        # optional
        show_param = request.form.get('show', default='', type=str)
        recommended_param = request.form.get('recommended', default=0, type=int)
        tstamp = datetime.now().isoformat()

        # event builder
        builder = {
            EventType.LOGIN.value: lambda: {
                'eventType': EventType.LOGIN.value,
                'deviceId': device_param,
                'userId': user_param,
                'tstamp': tstamp
            },
            EventType.LOGIN_FAILED.value: lambda: {
                'eventType': EventType.LOGIN_FAILED.value,
                'deviceId': device_param,
                'userId': user_param,
                'tstamp': tstamp
            },
            EventType.LOGOUT.value: lambda: {
                'eventType': EventType.LOGOUT.value,
                'deviceId': device_param,
                'userId': user_param,
                'tstamp': tstamp
            },
            EventType.DETAILS.value: lambda: {
                'eventType': EventType.DETAILS.value,
                'deviceId': device_param,
                'userId': user_param,
                'showId': show_param,
                'recommended': recommended_param,
                'tstamp': tstamp
            },
            EventType.TRAILER.value: lambda: {
                'eventType': EventType.TRAILER.value,
                'deviceId': device_param,
                'userId': user_param,
                'showId': show_param,
                'recommended': recommended_param,
                'tstamp': tstamp
            },
            EventType.WATCHING.value: lambda: {
                'eventType': EventType.WATCHING.value,
                'deviceId': device_param,
                'userId': user_param,
                'showId': show_param,
                'recommended': recommended_param,
                'tstamp': tstamp
            },
            EventType.FINISHED.value: lambda: {
                'eventType': EventType.FINISHED.value,
                'deviceId': device_param,
                'userId': user_param,
                'showId': show_param,
                'recommended': recommended_param,
                'tstamp': tstamp
            }
        }

        # build event
        stream_event_builder = builder.get(int(event_param), lambda: {})
        event = stream_event_builder()

        if event['eventType'] == EventType.LOGIN_FAILED.value:
            current_span = trace.get_current_span()
            current_span.set_status(StatusCode.ERROR)

        json_load = json.dumps(event)
        print(json_load)

        # send event
        # response = kinesis.put_record(
        #     StreamName="octank-kinesis-data-stream",
        #     Data=json_load,
        #     PartitionKey=user_param
        # )

        # call lambda
        response = lambda_.invoke(
            FunctionName=function_name,
            InvocationType='RequestResponse',
            LogType='Tail',
            Payload=json_load
        )

        # analyze response
        code = response["StatusCode"]

        return jsonify({
            'code': code
        }), 201


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
