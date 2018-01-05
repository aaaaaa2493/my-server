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

var w;

window.onload = function(){

    if(!WebSocket || !Worker){

        document.getElementById('general_info').innerHTML = 'Your browser is unsupported' +
                '<div class="button in_general g1" onclick=\'socket.clean=true;socket.close();\'>Ok</div>';

        document.getElementById('general_info').classList.remove('hidden');

        return;

    }

    document.getElementById('general_info').innerHTML = 'Wait while all players register' +
                '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");\'>Ok</div>';

    document.getElementById('general_info').classList.remove('hidden');
    
    w = new Worker("/static/poker/play/poker.js");

    w.onmessage = function(event) {
        console.log('from worker: ', event.data);

        data = event.data;

        if(data.type == 'inner html'){

            obj = data.obj;

            for(i = 0; i < obj.length; i++){
                document.getElementById(obj[i].id).innerHTML = obj[i].str;
            }

        }
        else if(data.type == 'change value'){
            document.getElementById(data.id).value = data.value;
        }
        else if(data.type == 'remove attr'){

            obj = data.obj;

            for(i = 0; i < obj.length; i++){
                document.getElementById(obj[i].id).removeAttribute('style');
            }
            
        }
        else if(data.type == 'class add'){
            document.getElementById(data.id).classList.add(data.class);
        }
        else if(data.type == 'class rem'){

            obj = data.obj;

            for(i = 0; i < obj.length; i++){
                document.getElementById(obj[i].id).classList.remove(obj[i].class);
            }
            
        }
        else if(data.type == 'src'){

            obj = data.obj;

            for(i = 0; i < obj.length; i++){
                document.getElementById(obj[i].id).src = obj[i].src;
            }
            
        }
        else if(data.type == 'src hide'){

            card1 = document.getElementById(data.id1);
            card2 = document.getElementById(data.id2);

            if(!card1.src.endsWith('UP.png')){
                card1.src = card1.src.replace('/img/poker/cards/', '/img/poker/cards_hidden/');
            }
            else{
                card1.src = '/img/poker/cards/ZZ.png';
            }

            if(!card2.src.endsWith('UP.png')){
                card2.src = card2.src.replace('/img/poker/cards/', '/img/poker/cards_hidden/');
            }
            else{
                card2.src = '/img/poker/cards/ZZ.png';
            }

        }
        else if(data.type == 'margin'){

            obj = data.obj;

            for(i = 0; i < obj.length; i++){

                chipstack = document.getElementById(obj[i].id);

                chipstack.style.marginLeft = obj[i].left;
                chipstack.style.marginTop = obj[i].top;

            }

            
        }
        else if(data.type == 'alert'){
            alert(data.msg);
        }
        else if(data.type == 'location'){
            window.location = data.to;
        }
        else if(data.type == 'sound'){
            playSound(data.file);
        }
        else if(data.type == 'add to chat'){
            chat = document.getElementById('chat');
            chat.innerHTML += '\n' + data.text;
            document.getElementById('chat').scrollTop = document.getElementById('chat').scrollHeight;
        }
        else if(data.type == 'bigger chat'){
            document.getElementById('chat').classList.add('bigger_chat');
        }
        else if(data.type == 'premove'){

            obj = data.obj;

            for(i = 0; i < obj.length; i++){
                document.getElementById(obj[i].id).checked = obj[i].checked;
            }

        }

    };

    w.postMessage({'type': 'start', 'player_name': player_name, 'table_to_spectate': table_to_spectate, 
                   'replay_id': replay_id, 'back_addr': back_addr, 'ip': ip, 'port': port, 'nick': nick});

}

function post_raise_minus(){
    raise = document.getElementById('range');
    w.postMessage({type: 'raise minus', value: raise.value, min_value: raise.min, max_value: raise.max});
}

function post_raise_plus(){
    raise = document.getElementById('range');
    w.postMessage({type: 'raise plus', value: raise.value, min_value: raise.min, max_value: raise.max});
}

function post_raise_all(){
    raise = document.getElementById('range');
    w.postMessage({type: 'raise all', max_value: raise.max});
}

function post_raise_pot(){
    raise = document.getElementById('range');
    w.postMessage({type: 'raise pot', value: raise.value, max_value: raise.max});
}

function post_textchange(text){
    raise = document.getElementById('range');
    w.postMessage({type: 'textraise', text: text, max_value: raise.max, min_value: raise.min});
}

function post_socket_close(){
    w.postMessage({type: 'socket close'});
}

function post_socket_stay(){
    w.postMessage({type: 'socket stay'});
}

function post_socket_clean(){
    w.postMessage({type: 'socket clean'});
}

function post_set_decision(decision){
    w.postMessage({type: 'set decision', value: decision});
}

function post_replay_pause_play(){
    w.postMessage({type: 'pause play'});
}

function post_replay_next_step(){
    w.postMessage({type: 'next step'});
}

function post_replay_prev_hand(){
    w.postMessage({type: 'prev hand'});
}

function post_replay_next_hand(){
    w.postMessage({type: 'next hand'});
}

function post_tournament_info(){
    w.postMessage({type: 'tournament info'});
}

function post_last_hand_info(){
    w.postMessage({type: 'last hand info'});
}

function post_input_chat(event, text){
    w.postMessage({type: 'chat message', key: event.keyCode, text: text});
}

function post_premove(obj, answer){
    w.postMessage({type: 'premove', answer: answer, checked: obj.checked});
}