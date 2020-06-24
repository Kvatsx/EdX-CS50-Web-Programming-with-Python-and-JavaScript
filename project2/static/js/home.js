document.addEventListener('DOMContentLoaded', () => {
    const name = localStorage.getItem('name')
    console.log(localStorage.getItem('name'))

    emptyMessageHandler()

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    socket.on('connect', () => {
        console.log("socket on")
        document.querySelector('#createBtn').onclick = () => {
            const channelName = document.querySelector("#channelName").value;
            console.log(channelName)
            socket.emit('addChannel', {'channelName': channelName});
            $('#newChannel').modal("hide")
        }
    });
    socket.on('createChannel', channelName => {
        console.log(channelName)
        // const template = Handlebars.compile(document.querySelector('#channelBtn').innerHTML);
        var btn = '<button type="button" class="btn btn-primary">'+ channelName['channelName'] +'</button>';
        // const content = template({'channelName': channelName['channelName']});
        console.log(btn)
        document.querySelector("#channelsList").innerHTML += btn;
        console.log("done");
    });
    socket.on('createAlert', message => {
        alert(message)
    })
});

function emptyMessageHandler () {
    document.querySelector('#send').disabled = true;
    document.querySelector('#message').onkeyup = () => {
        if (document.querySelector('#message').value.length > 0)
            document.querySelector('#send').disabled = false;
        else
            document.querySelector('#send').disabled = true;
    };
}
