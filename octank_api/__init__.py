import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/pg_octank_api'

db = SQLAlchemy(app)

# read all users to impersonate
@app.route('/api/users', methods=['GET'])
def read_users():

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

    return jsonify({
        'users': [user.serialize() for user in user.query.all()]
    }), 200

# get all shows to watch
@app.route('/api/shows', methods=['GET'])
def read_shows():
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

    return jsonify({
        'shows': [show.serialize() for show in show.query.all()]
    }), 200

@app.route('/api/watching', methods=['POST'])
def watching_heartbeat():
    user = request.args.get('user', type = str)
    show = request.args.get('show', type = str)
    return jsonify({
    }), 201
  
if __name__ == '__main__':
    app.run(debug = True)