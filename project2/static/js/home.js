document.addEventListener('DOMContentLoaded', () => {
    var name = localStorage.getItem('name')
    console.log(localStorage.getItem('name'))

    emptyMessageHandler()

    if (localStorage.getItem('current_channel')) {
        showChats(localStorage.getItem('current_channel', name));
    }

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    socket.on('connect', () => {
        console.log("socket on")
        document.querySelector('#createBtn').onclick = () => {
            const channelName = document.querySelector("#channelName").value;
            console.log(channelName)
            socket.emit('addChannel', {'channelName': channelName});
            $('#newChannel').modal("hide")
        }

        document.querySelector("#mssgForm").onsubmit = () => {
            const message = document.querySelector("#message").value;
            console.log(message)
            socket.emit('addMessage', {'name': name, 'message': message, 'channelName': localStorage.getItem('current_channel')})
            document.querySelector("#message").value = "";
            return false
        }
    });
    socket.on('createChannel', channelName => {
        const template = Handlebars.compile(document.querySelector('#channelBtn').innerHTML);
        const content = template({'channelName': channelName['channelName']});
        console.log(content);
        document.querySelector("#channelsList").innerHTML += content;
        // showChats(channelName['channelName']);
    });

    socket.on('createMessage', chat => {
        console.log(chat)
        addChat(chat, 0);
    })

    socket.on('createAlert', message => {
        alert(message)
    })
});

function showChats (name) {
    $("#chatList").empty();
    document.querySelector("#channelname").innerHTML = name;
    localStorage.setItem('current_channel', name);
    console.log("ShowChats called " + name)
    const request = new XMLHttpRequest();
    console.log('/getChats/'+ name);
    request.open('POST', '/getChats');
    request.onload = () => {
        console.log('onload');
        const data = JSON.parse(request.responseText);
        if (data.success) {
            data.chats.forEach(addChat);
            console.log(data)
        }
        else {
            document.querySelector('#chatList').innerHTML = 'There was an error.';
        }
    }
    const data = new FormData();
    data.append('channelName', name);
    request.send(data);
}

function addChat(item, index) {
    if (item.name.localeCompare(localStorage.getItem('name')) == 0) {
        const template = Handlebars.compile(document.querySelector('#sentMessage').innerHTML);
        const content = template({'name': item.name, 'mssg':item.message, 'time':item.time, 'date':item.date});
        document.querySelector('#chatList').innerHTML += content;
    }
    else {
        const template = Handlebars.compile(document.querySelector('#receivedMessage').innerHTML);
        const content = template({'name': item.name, 'mssg':item.message, 'time':item.time, 'date':item.date});
        document.querySelector('#chatList').innerHTML += content;
    }
}

function emptyMessageHandler () {
    document.querySelector('#send').disabled = true;
    document.querySelector('#message').onkeyup = () => {
        if (document.querySelector('#message').value.length > 0)
            document.querySelector('#send').disabled = false;
        else
            document.querySelector('#send').disabled = true;
    };
}
