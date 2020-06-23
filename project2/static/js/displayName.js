document.addEventListener('DOMContentLoaded', () => {
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