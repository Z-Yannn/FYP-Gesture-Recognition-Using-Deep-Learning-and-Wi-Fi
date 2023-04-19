import time
import queue
import socket
import spotipy
from spotipy.oauth2 import SpotifyOAuth

client_id = "31f4b13536d74296bb868695b105ee1d"
client_secret = "d8c0be39ba5c45d8ae8488c94f32b4ab"
redirect_uri = "http://localhost:8888/callback"

# Authenticate and get the access token
# sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri))
scope = "user-modify-playback-state,user-read-playback-state"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

# Get a list of available devices
devices = sp.devices()
device_id = devices['devices'][0]['id']

# define the action to be executed when a message is received
def execute(message):
    if message == "down":
        sp.pause_playback()
    if message == "start":
        sp.start_playback()
    if message == "right":
        sp.next_track()
    if message == "left":
        sp.previous_track()

# Set up socket connection
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', 2000))
sock.listen()

while True:
    # Wait for a message to be sent from the other program
    conn, addr = sock.accept()
    message = conn.recv(1024).decode()

    # Check the message and execute the corresponding action
    execute(message)

    # Close the connection
    conn.close()
