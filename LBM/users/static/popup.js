let popupWindow;

function openLoginPopup() {
    // popupWindow = window.open('http://127.0.0.1:7000/login/?next=http://127.0.0.1:8000/login_success/', 'Login', 'height=500,width=500')
    popupWindow = window.open('http://127.0.0.1:7000/login/');
    popupWindow.onload = function() {
        popupWindow.opener = window;
    }

    var popupCheck = setInterval(function() {
        if(popupWindow.closed) {
            console.log("popup Closed");
            clearInterval(popupCheck);
            location.reload();
        }
    }, 500);
}


window.addEventListener('message', function(event) {
    if (event.data === 'login_successful') {
        console.log("got message")
        location.reload();
    }
}, false);
