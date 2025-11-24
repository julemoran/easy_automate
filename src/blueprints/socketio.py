
from flask import Blueprint, send_from_directory, current_app
from flask_sock import Sock
import threading
import time

websocket_bp = Blueprint('socketio', __name__)
sock = Sock()

@websocket_bp.route('/ws-test')
def ws_test():
    return send_from_directory(websocket_bp.root_path + '/../static', 'ws_test.html')

@websocket_bp.route('/crud')
def crud():
    return send_from_directory(websocket_bp.root_path + '/../static', 'crud.html')


# Standard WebSocket endpoint using Flask-Sock
@sock.route('/ws')
def websocket(ws):
	while True:
		ws.send('{"message": "ping"}')
		current_app.logger.info('Ping event sent to WebSocket client')
		time.sleep(5)

# To use: call sock.init_app(app) in your app factory after registering blueprints
