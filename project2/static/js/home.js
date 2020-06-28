document.addEventListener('DOMContentLoaded', () => {
    var name = localStorage.getItem('name')
    console.log(localStorage.getItem('name'))

    emptyMessageHandler()

    if (localStorage.getItem('current_channel')) {
        showChats(localStorage.getItem('current_channel'));
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

        var btns = document.querySelectorAll('button.close.delM');
        console.log(btns);
        btns.forEach(function(btn) {
            btn.addEventListener('click', function() {
                var parent = this.parentElement;
                var temp = this.parentElement.childNodes;
                // temp.forEach((el, index) => {
                //     console.log(el.innerHTML + " " + index);
                // })
                var mssg = {};
                mssg['name'] = temp[5].innerHTML;
                mssg['message'] = temp[7].innerHTML;
                var str = temp[9].innerHTML;
                str = str.split(" | "); 
                mssg['time'] = str[0];
                mssg['date'] = str[1];
                mssg['channelName'] = localStorage.getItem('current_channel');
        
                // temp[7].innerHTML = "Message deleted!";
                // parent.removeChild(temp[5]);
                // parent.removeChild(temp[8]);
                // parent.removeChild(temp[3]);
                console.log("COOL");
                socket.emit('delete message', mssg);
            })
        })

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
        var btns = document.querySelectorAll('button.close.delM');
        console.log(btns);
        btns.forEach(function(btn) {
            btn.addEventListener('click', function() {
                var parent = this.parentElement;
                var temp = this.parentElement.childNodes;
                // temp.forEach((el, index) => {
                //     console.log(el.innerHTML + " " + index);
                // })
                var mssg = {};
                mssg['name'] = temp[5].innerHTML;
                mssg['message'] = temp[7].innerHTML;
                var str = temp[9].innerHTML;
                str = str.split(" | "); 
                mssg['time'] = str[0];
                mssg['date'] = str[1];
                mssg['channelName'] = localStorage.getItem('current_channel');
        
                // temp[7].innerHTML = "Message deleted!";
                // parent.removeChild(temp[5]);
                // parent.removeChild(temp[8]);
                // parent.removeChild(temp[3]);
                console.log("COOL");
                socket.emit('delete message', mssg);
            })
        })
    });

    socket.on('createAlert', message => {
        alert(message)
    });

    socket.on('updateChats', channel_name => {
        if (localStorage.getItem('current_channel').localeCompare(channel_name) == 0) {
            showChats(channel_name);
        }
    })

    // $('button.delM').onclick(function(event) {
    //     var parent = this.parentElement;
    //     var temp = this.parentElement.childNodes;
    //     var mssg = {};
    //     mssg['name'] = temp[3].innerHTML;
    //     mssg['message'] = temp[5].innerHTML;
    //     var str = temp[7].innerHTML;
    //     str = str.split(" | "); 
    //     mssg['time'] = str[0];
    //     mssg['date'] = str[1];

    //     temp[5].innerHTML = "Message deleted!";
    //     parent.removeChild(temp[3]);
    //     parent.removeChild(temp[6]);
    //     parent.removeChild(temp[1]);
    //     console.log(mssg);
    //     console.log("ok");
    //     socket.emit('delete message', mssg);
    //     return false;
    // })
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
    Handlebars.registerHelper('ifCond', function(v1, operator, v2, options) {
        switch (operator) {
            case '==':
                console.log(v1 + " " + v2);
                return (v1 == v2) ? options.fn(this) : options.inverse(this);
            case '===':
                return (v1 === v2) ? options.fn(this) : options.inverse(this);
            case '!=':
                return (v1 != v2) ? options.fn(this) : options.inverse(this);
            case '!==':
                return (v1 !== v2) ? options.fn(this) : options.inverse(this);
            case '<':
                return (v1 < v2) ? options.fn(this) : options.inverse(this);
            case '<=':
                return (v1 <= v2) ? options.fn(this) : options.inverse(this);
            case '>':
                return (v1 > v2) ? options.fn(this) : options.inverse(this);
            case '>=':
                return (v1 >= v2) ? options.fn(this) : options.inverse(this);
            case '&&':
                return (v1 && v2) ? options.fn(this) : options.inverse(this);
            case '||':
                return (v1 || v2) ? options.fn(this) : options.inverse(this);
            default:
                return options.inverse(this);
        }
    });
    if (localStorage.getItem('current_channel').localeCompare(item.channel_name) == 0) {
        if (item.name.localeCompare(localStorage.getItem('name')) == 0) {
            if (!item.notDeleted) {
                const template = Handlebars.compile(document.querySelector('#sentMessage').innerHTML);
                const content = template({'name': null, 'mssg':item.message, 'time':item.time, 'date':item.date, 'notDeleted': item.notDeleted});
                document.querySelector('#chatList').innerHTML += content;
            }
            else {
                const template = Handlebars.compile(document.querySelector('#sentMessage').innerHTML);
                const content = template({'name': item.name, 'mssg':item.message, 'time':item.time, 'date':item.date, 'notDeleted': item.notDeleted});
                document.querySelector('#chatList').innerHTML += content;
            }
        }
        else {
            if (!item.notDeleted) {
                const template = Handlebars.compile(document.querySelector('#receivedMessage').innerHTML);
                const content = template({'name': null, 'mssg':item.message, 'time':item.time, 'date':item.date, 'notDeleted': item.notDeleted});
                document.querySelector('#chatList').innerHTML += content;
            }
            else {
                const template = Handlebars.compile(document.querySelector('#receivedMessage').innerHTML);
                const content = template({'name': item.name, 'mssg':item.message, 'time':item.time, 'date':item.date, 'notDeleted': item.notDeleted});
                document.querySelector('#chatList').innerHTML += content;
            }
        }
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

function deleteMssg(x) {
    var parent = x.parentElement;
    var temp = x.parentElement.childNodes;
    var mssg = {};
    mssg['name'] = temp[3].innerHTML;
    mssg['message'] = temp[5].innerHTML;
    var str = temp[7].innerHTML;
    str = str.split(" | "); 
    mssg['time'] = str[0];
    mssg['date'] = str[1];

    temp[5].innerHTML = "Message deleted!";
    parent.removeChild(temp[3]);
    parent.removeChild(temp[6]);
    parent.removeChild(temp[1]);
    console.log(mssg);
}
