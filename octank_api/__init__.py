import json
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, instance_relative_config=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/pg_octank_api'

db = SQLAlchemy(app)

# define ORM structures
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

# get all shows to watch
@app.route('/api/shows', methods=['GET'])
def read_shows():
    return jsonify({
        'shows': []
    }), 200

@app.route('/api/watching', methods=['POST'])
def watching_heartbeat():
    user = request.args.get('user', type = str)
    show = request.args.get('show', type = str)
    return jsonify({
    }), 201
  
if __name__ == '__main__':
    app.run(debug = True)