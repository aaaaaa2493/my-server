var socket;
var last_msg = '';
var func;

function createCookie(name,value,days) {
    var expires = "";
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = "; expires=" + date.toUTCString();
    }
    document.cookie = name + "=" + value + expires + "; path=/";
}

function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for(var i=0;i < ca.length;i++) {
        var c = ca[i];
        while (c.charAt(0)==' ') c = c.substring(1,c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
    }
    return null;
}

function eraseCookie(name) {
    createCookie(name,"",-1);
}

function text_change(text){

    if(text.length == 0){
        return;
    }
    else if(text.length == 1 && text == ' '){
        document.getElementById('textraise').value = '';
    }
    else{

        new_text = '';

        for(i = 0; i < text.length; i++){
            curr = text.charCodeAt(i);

            if(curr > 47 && curr < 58 || 
               curr > 96 && curr < 123 || 
               curr > 64 && curr < 91 || 
               curr == 1025 || 
               curr > 1039 && curr < 1104 ||
               curr == 1105){

                new_text += text.charAt(i);
            }

        }

        if(new_text.length > 10 && new_text.length != 64){
            new_text = new_text.substring(0, 10);
        }

        document.getElementById('nick').value = new_text;
    }

}

function register(){

    nick = document.getElementById('nick').value;

    if(nick == ''){
        alert('Введите имя или ник!')
    }
    else{

        if(nick.length != 64){
            createCookie('nick', nick, 365);
            window.location = '/poker/play/' + nick;
        }
        else{

            if(admin != null){
                func = del_admin;
                socket.send('del ' + nick + ' ' + admin);
            }
            else{
                func = get_admin;
                socket.send('get ' + nick);
            }

        }
        
    }

}

function watch(){

    nick = document.getElementById('nick').value;

    if(nick == ''){
        alert('Введите имя или ник!');
    }
    else{
        if(nick.length != 64){
            createCookie('nick', nick, 365);
            window.location='/poker/watch';
        }
    }

}

function start(){

    if(state == 'machine not work'){

        document.getElementById('state').innerHTML = 'Игровой сервер не в сети';

        document.getElementById('nick').classList.add('hidden');
        document.getElementById('register').classList.add('hidden');
        document.getElementById('connect').classList.add('hidden');
        document.getElementById('watch').classList.add('hidden');

        document.getElementById('create').parentNode.removeChild(document.getElementById('create'));
        document.getElementById('delete').parentNode.removeChild(document.getElementById('delete'));

    }
    else if(state == 'game not created'){

        document.getElementById('state').innerHTML = 'Игра ещё не создана';

        document.getElementById('nick').classList.add('hidden');
        document.getElementById('register').classList.add('hidden');
        document.getElementById('connect').classList.add('hidden');
        document.getElementById('watch').classList.add('hidden');

        document.getElementById('delete').parentNode.removeChild(document.getElementById('delete'));

    }
    else if(state == 'registration started'){

        document.getElementById('state').innerHTML = 'Идёт регистрация';

        document.getElementById('connect').classList.add('hidden');
        document.getElementById('watch').classList.add('hidden');

        document.getElementById('create').parentNode.removeChild(document.getElementById('create'));

    }
    else if(state == 'game started'){

        document.getElementById('state').innerHTML = 'Идёт игра';

        document.getElementById('register').classList.add('hidden');

        document.getElementById('create').parentNode.removeChild(document.getElementById('create'));

    }
    else if(state == 'unknown state'){
        document.getElementById('state').innerHTML = 'Ошибка - неизвестное состояние';
        document.getElementById('create').parentNode.removeChild(document.getElementById('create'));
        document.getElementById('delete').parentNode.removeChild(document.getElementById('delete'));
    }
    else{
        document.getElementById('state').innerHTML = 'Критическая ошибка состояния';
        document.getElementById('create').parentNode.removeChild(document.getElementById('create'));
        document.getElementById('delete').parentNode.removeChild(document.getElementById('delete'));
    }

    if(document.getElementById('create') != null && !admin){
        document.getElementById('create').parentNode.removeChild(document.getElementById('create'));
    }

    if(document.getElementById('delete') != null && !admin){
        document.getElementById('delete').parentNode.removeChild(document.getElementById('delete'));
    }

    nick = readCookie('nick');
    if(nick){
        document.getElementById('nick').value = nick;
    }

    document.getElementById('menu').style.display = 'block';

}


function test_admin(){

    if(last_msg == 'yes'){

        admin = readCookie('admin');
        createCookie('admin', admin, 365);

        console.log('admin test success');

        start();

    }
    else{

        eraseCookie('admin');
        admin = null;

        console.log('admin test fail');

        start();

    }

}


function get_admin(){

    if(last_msg.length == 64){
        createCookie('admin', last_msg, 365);
    }
    else{
        eraseCookie('admin');
    }

    window.location = '/poker';

}


function del_admin(){

    if(last_msg == 'ok'){

        eraseCookie('admin');
        admin = null;

    }

    window.location = '/poker';

}


function socket_open(){

    admin = readCookie('admin');
    console.log(admin);

    if(admin != null){

        if(admin.length != 64){
            eraseCookie('admin');
            admin = null;

            console.log('delete bad admin key');

            start();
        }
        else{
            func = test_admin;
            socket.send('test ' + admin);
        }
        
    }
    else{

        start();

    }

}

function socket_message(event) {
    last_msg = event.data;
    func();
}

function setup(){

    if(socket === undefined){
        socket = new WebSocket('ws://' + ip + ':' + port);

        socket.onopen = socket_open;
        socket.onmessage = socket_message;
    }

}

window.onload = setup
