import os

from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

Channels = []
Chats = {}

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('displayName')
        print(name)
        return redirect(url_for('home'))
    return render_template('index.html')

@app.route('/home')
def home():
    print("Channels:", Channels)
    return render_template('home.html', channels=Channels)

@socketio.on("addChannel")
def addChannel(channelName):
    name = channelName['channelName']
    if (name not in Channels):
        Channels.append(name)
        Chats[name] = []
        print(1)
        emit("createChannel", channelName, broadcast=True)
    else:
        print(2)
        emit("createAlert", "Channel with this name already exist.")

# https://bootsnipp.com/snippets/1ea0N