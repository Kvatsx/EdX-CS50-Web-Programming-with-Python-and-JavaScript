import os

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_socketio import SocketIO, emit

from datetime import datetime


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
    # print("Channels:", Channels)
    return render_template('home.html', channels=Channels)


@socketio.on("addChannel")
def addChannel(channelName):
    name = channelName['channelName']
    if (name not in Channels):
        Channels.append(name)
        Chats[name] = []
        print("Channel Created", Channels)
        emit("createChannel", channelName, broadcast=True)
    else:
        emit("createAlert", "Channel with this name already exist.")


@socketio.on("addMessage")
def addMessage(data):
    chat = {}
    chat['name'] = data['name']
    chat['message'] = data['message']
    now = datetime.now()
    date = now.strftime("%d/%m/%Y")
    time = now.strftime('%H:%M')
    chat['date'] = date
    chat['time'] = time
    chat['notDeleted'] = True
    chat['channel_name'] = data['channelName']

    if (len(Chats[data['channelName']]) == 100):
        Chats[data['channelName']].pop(0)
    Chats[data['channelName']].append(chat)
    emit('createMessage', (chat, data['channelName']), broadcast=True)


@app.route('/getChats', methods=["POST"])
def getChats():
    print("Channels:", Channels)
    print("Chat:", Chats.keys())
    channelName = request.form.get("channelName")
    if channelName not in Chats:
        return jsonify({'success': False})
    return jsonify({'success': True, 'chats': Chats[channelName]})

@socketio.on("delete message")
def deleteM(data):
    temp = Chats[data['channelName']]
    for e in temp:
        if (e['name'] == data['name'] and e['message'] == data['message'] and e['date'] == data['date'] and e['time'] == data['time']):
            e['message'] = "Message deleted!"
            e['date'] = None
            e['time'] = None
            e['notDeleted'] = False
            break
    print(data)
    emit("updateChats", data['channelName'],  broadcast=True)



# https://bootsnipp.com/snippets/1ea0N