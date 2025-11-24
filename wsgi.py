
from src import create_app
from src.blueprints.socketio import sock

app = create_app()
sock.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)