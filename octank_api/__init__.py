import json
from flask import Flask, request, jsonify

def create_app(test_confiig=None):
    app = Flask(__name__, instance_relative_config=True)

    # read all users to impersonate
    @app.route('/api/users', methods=['GET'])
    def read_users():
        return jsonify({
            'users': []
        }), 209

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
  
    return app
