var max_people = 100;

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

function text_change(input){

    text = input.value;

    if(text.length == 0 || text.length == 1 && text == '0' && input.id == 'unreal_count'){
        return;
    }
    else{

        new_text = '';
        at_least_one_num = false;

        for(i = 0; i < text.length; i++){
            curr = text.charCodeAt(i);

            if(curr > 47 && curr < 58){

                if(at_least_one_num == false && curr == 48){
                    continue;
                }

                new_text += text.charAt(i);

                at_least_one_num = true;
            }

        }

        if(new_text == ''){
            new_text = '0';
        }

        if(input.id == 'table_count'){

            num = new Number(new_text);

            if(num < 2){
                num = 2;
            }
            else if(num > 9){
                num = 9;
            }

            input.value = num;

        }
        else if(input.id == 'unreal_count'){

            total_people = new Number(document.getElementById('total_count').value);
            unreal_count = new Number(new_text);

            if(unreal_count > total_people){
                unreal_count = total_people;
            }

            input.value = unreal_count;

        }
        else if(input.id == 'total_count'){

            total_people = new Number(new_text);

            if(total_people > max_people){
                total_people = max_people;
            }
            else if(total_people < 2){
                total_people = 2;
            }

            input.value = total_people;

            unreal_count = new Number(document.getElementById('unreal_count').value);

            if(unreal_count > total_people){
                document.getElementById('unreal_count').value = total_people;
            }

        }
        else if(input.id == 'chip_count'){

            num = new Number(new_text);

            if(num < 1){
                num = 1;
            }

            input.value = num;

        }

    }

}

function start(){

    document.getElementById('menu').style.display = 'block';

}



function create_game(){

    text_change(document.getElementById('total_count'));
    text_change(document.getElementById('unreal_count'));
    text_change(document.getElementById('table_count'));
    text_change(document.getElementById('chip_count'));

    window.location='/poker/create/c?key=' + admin + 
                                    '&total_count=' + document.getElementById('total_count').value +
                                    '&unreal_count=' + document.getElementById('unreal_count').value +
                                    '&table_count=' + document.getElementById('table_count').value +
                                    '&chip_count=' + document.getElementById('chip_count').value;

}

function test_admin(){

    if(last_msg == 'yes'){

        admin = readCookie('admin');
        createCookie('admin', admin, 365);
        start();

    }
    else{

        eraseCookie('admin');
        admin = null;
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