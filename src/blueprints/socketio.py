
from flask import Blueprint, send_from_directory, current_app
from flask_sock import Sock
import threading
import time

websocket_bp = Blueprint('socketio', __name__)
sock = Sock()



# Serve any file from the static folder using the root endpoint
@websocket_bp.route('/', defaults={'filename': None})
@websocket_bp.route('/<path:filename>')
def static_files(filename):
	static_dir = websocket_bp.root_path + '/../static'
	if filename:
		return send_from_directory(static_dir, filename)
	else:
		# Optionally serve an index.html or a simple message
		try:
			return send_from_directory(static_dir, 'index.html')
		except Exception:
			return 'Static file server: specify a filename in the URL.', 404


# Standard WebSocket endpoint using Flask-Sock
@sock.route('/ws')
def websocket(ws):
	while True:
		ws.send('{"message": "ping"}')
		current_app.logger.info('Ping event sent to WebSocket client')
		time.sleep(5)

# To use: call sock.init_app(app) in your app factory after registering blueprints
