document.addEventListener('DOMContentLoaded', () => {
    console.log("lola")
    document.querySelector("#continue").onclick = () => {
        console.log("Hola");
        localStorage.setItem('name', document.querySelector('#displayName').value);
        console.log(document.querySelector('#displayName').value);
    }

    displayName()
});

function displayName () {
    document.querySelector('#continue').disabled = true;
    document.querySelector('#displayName').onkeyup = () => {
        if (document.querySelector('#displayName').value.length > 0)
            document.querySelector('#continue').disabled = false;
        else
            document.querySelector('#continue').disabled = true;
    };
}