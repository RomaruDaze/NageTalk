# app.py
from flask import Flask, send_from_directory, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import threading
import time

app = Flask(__name__, static_folder='./dist/assets', template_folder='./dist')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return send_from_directory(app.template_folder, 'index.html')

@app.route('/<path:path>')
def send_static(path):
    return send_from_directory(app.static_folder, path)

players = {}
countdown = 10  # Initialize countdown

def emit_player_list():
    while True:
        time.sleep(10)  # Wait for 10 seconds
        socketio.emit('update_players', list(players.keys()))  # Emit current players

def countdown_timer():
    global countdown
    while True:
        if countdown > 0:
            time.sleep(1)
            countdown -= 1
            socketio.emit('countdown', countdown)  # Broadcast countdown to all clients
        else:
            countdown = 10  # Reset countdown after reaching 0

@socketio.on('player_ready')
def handle_player_ready(player_name):
    global countdown
    players[player_name] = True  
    print(f"{player_name} is ready")
    socketio.emit('update_players', list(players.keys()))  
    print(f"Current players: {list(players.keys())}")

    # Reset countdown when a player is ready
    countdown = 10

@socketio.on('connect')
def handle_connect():
    print("A client connected.")
    socketio.emit('update_players', list(players.keys()))  # Emit current players on connect

@socketio.on('disconnect')
def handle_disconnect():
    print("A client disconnected.")
    # Optionally, remove the player from the players dictionary

@socketio.on('request_player_list')
def handle_request_player_list():
    socketio.emit('update_players', list(players.keys()))  # Emit current players

@socketio.on('button_click')
def handle_button_click(data):
    player_name = data['name']
    print(f"{player_name} was selected.")
    socketio.emit('button_click', {'name': player_name})  # Broadcast selected player to all clients

# Start the background thread to emit player list every 10 seconds
threading.Thread(target=emit_player_list, daemon=True).start()
# Start the countdown timer thread
threading.Thread(target=countdown_timer, daemon=True).start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, allow_unsafe_werkzeug=True)
