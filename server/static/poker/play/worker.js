function createCookie(name,value,days) {
    let expires = '';
    if (days) {
        let date = new Date();
        date.setTime(date.getTime() + (days*24*60*60*1000));
        expires = '; expires='+ date.toUTCString();
    }
    document.cookie = name + '=' + value + expires + '; path=/';
}

function readCookie(name) {
    let nameEQ = name + '=';
    let ca = document.cookie.split(';');
    for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0)=== ' '){
            c = c.substring(1, c.length);
        }
        if (c.indexOf(nameEQ) === 0) {
            return c.substring(nameEQ.length, c.length);
        }
    }
    return null;
}

function eraseCookie(name) {
    createCookie(name, '', -1);
}

class Receive{
    constructor(){
        this.handle = {
            'inner html': d => this.inner_html(d),
            'change value': d => this.change_value(d),
            'class add': d => this.class_add(d),
            'class rem': d => this.class_rem(d),
            'src': d => this.src(d),
            'src hide': d => this.src_hide(d),
            'alert': d => this.alert(d),
            'location': d => this.location(d),
            'sound': d => this.sound(d),
            'add to chat': d => this.add_to_chat(d),
            'bigger chat': d => this.bigger_chat(d),
            'premove': d => this.premove(d),
            'dealer pos': d => this.dealer_pos(d),
            'chips to main': d => this.chips_to_main(d),
            'chips from main': d => this.chips_from_main(d),
            'clear chips': d => this.clear_chips(d),
            'thinking pos': d => this.thinking_pos(d),
            'final table': d => this.final_table(d),
            'set empty': d => this.set_empty(d),
            'set disconnected': d => this.set_disconnected(d),
        };
    }

    event(data){
        console.log('from worker: ', data);
        this.handle[data.type](data);
    }

    inner_html(data){
        let obj = data.obj;
        for(let i = 0; i < obj.length; i++){
            document.getElementById(obj[i].id).innerHTML = obj[i].str;
        }
    }

    change_value(data){
        document.getElementById(data.id).value = data.value;
    }

    class_add(data){
        document.getElementById(data.id).classList.add(data.class);
    }

    class_rem(data){
        let obj = data.obj;
        for(let i = 0; i < obj.length; i++){
            document.getElementById(obj[i].id).classList.remove(obj[i].class);
        }
    }

    src(data){
        let obj = data.obj;
        for(let i = 0; i < obj.length; i++){
            document.getElementById(obj[i].id).src = obj[i].src;
        }
    }

    src_hide(data){
        let card1 = document.getElementById(data.id1);
        let card2 = document.getElementById(data.id2);

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

    alert(data){
        alert(data.msg);
    }

    location(data){
        window.location = data.to;
    }

    sound(data){
        playSound(data.file);
    }

    add_to_chat(data){
        let chat = document.getElementById('chat');
        chat.innerHTML += '\n' + data.text;
        document.getElementById('chat').scrollTop = document.getElementById('chat').scrollHeight;
    }

    bigger_chat(){
        document.getElementById('chat').classList.add('bigger_chat');
    }

    premove(data){
        let obj = data.obj;
        for(let i = 0; i < obj.length; i++){
            document.getElementById(obj[i].id).checked = obj[i].checked;
        }
    }

    dealer_pos(data){
        document.getElementById('dealer').setAttribute('data-pos', data.pos);
    }

    chips_to_main(data){
        for(let curr_id of data.ids){
            document.getElementById(curr_id).classList.add('move_to_main');
        }
    }

    chips_from_main(data){
        let obj = document.getElementById(data.id);
        setTimeout(() => obj.classList.add('move_from_main'), 100);
        setTimeout(() => obj.classList.remove('main_chips'), 200);
    }

    clear_chips(data){
        for(let curr_id of data.ids){
            let obj = document.getElementById(curr_id);
            obj.classList.remove('move_to_main');
            obj.classList.remove('move_from_main');
        }
    }

    thinking_pos(data){
        document.getElementById('players').setAttribute('data-think', data.pos);
    }

    final_table(data){
        document.getElementById('players').setAttribute('data-final', data.is_final);
    }

    set_empty(data){
        document.getElementById(data.id).setAttribute('data-empty', data.is_empty);
    }

    set_disconnected(data){
        document.getElementById(data.id).setAttribute('data-disconnected', data.is_disconnected);
    }
}

let w;
let r;

window.onload = function(){

    if(!WebSocket || !Worker){
        document.getElementById('general_info').innerHTML = 'Your browser is unsupported' +
                '<div class="button in_general g1" onclick=\'location=back_addr\'>Ok</div>';
        document.getElementById('general_info').classList.remove('hidden');
        return;
    }
    
    w = new Worker('/static/poker/play/poker.js');
    r = new Receive();

    w.onmessage = e => r.event(e.data);

    w.postMessage({
        'type': 'start',
        'player_name': player_name,
        'table_to_spectate': table_to_spectate,
        'replay_id': replay_id,
        'back_addr': back_addr,
        'ip': ip,
        'port': port,
        'nick': nick
    });
};

function shortcut(num){

    if(num < 1000){
        return num+'';
    }
    else if(num < 10000){
        num = num + '';
        return num.substring(0, num.length - 3) + '&thinsp;' + num.substring(num.length - 3, num.length);
    }
    else if(num < 100000){
        // 46776 -> 46.7k
        return (Math.floor(num/100)/10) + 'k';
    }
    else if(num < 1000000){
        // 123231 -> 123k
        return Math.floor(num/1000) + 'k';
    }
    else if(num < 10000000){
        // 3 123 345 -> 3.12m
        return (Math.floor(num/10000)/100) + 'm';
    }
    else if(num < 100000000){
        // 12 345 678 -> 12.3m
        return ((Math.floor(num/100000))/10) + 'm';
    }
    else if(num < 1000000000){
        // 123 345 678 -> 123m
        return Math.floor(num/1000000) + 'm';
    }
    else if(num < 10000000000){
        // 1 123 345 678 -> 1.12b
        return (Math.floor(num/10000000)/100) + 'b';
    }
    else if(num < 100000000000){
        // 12 123 345 678 -> 12.1b
        return (Math.floor(num/100000000)/10) + 'b';
    }
    else {
        // 122 223 345 678 -> 123b
        return Math.floor(num/1000000000) + 'b';
    }

}

function post_raise_minus(){
    let raise = document.getElementById('range');
    w.postMessage({type: 'raise minus', value: raise.value, min_value: raise.min, max_value: raise.max});
}

function post_raise_plus(){
    let raise = document.getElementById('range');
    w.postMessage({type: 'raise plus', value: raise.value, min_value: raise.min, max_value: raise.max});
}

function post_raise_all(){
    let raise = document.getElementById('range');
    w.postMessage({type: 'raise all', max_value: raise.max});
}

function post_raise_pot(){
    let raise = document.getElementById('range');
    w.postMessage({type: 'raise pot', value: raise.value, max_value: raise.max});
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

function open_tab(name) {
    w.postMessage({type: 'open tab', name: name});
}

function post_input_chat(event, text){
    w.postMessage({type: 'chat message', key: event.keyCode, text: text});
}

function post_premove(obj, answer){
    w.postMessage({type: 'premove', answer: answer, checked: obj.checked});
}

function text_change(text){

    let raise = document.getElementById('range');
    let max_value = raise.max;
    let min_value = raise.min;

    if(text.length > 0) {
        if (text.length === 1 && text === '0') {
            document.getElementById('textraise').value = '';
        }
        else {

            let new_text = '';
            let at_least_one_num = false;

            for (let i = 0; i < text.length; i++) {
                let curr = text.charCodeAt(i);

                if (curr > 47 && curr < 58) {

                    if (at_least_one_num === false && curr === 48) {
                        continue;
                    }

                    new_text += text.charAt(i);

                    at_least_one_num = true;
                }

            }

            document.getElementById('textraise').value = new_text;

            if (new_text === '') {
                new_text = min_value;
            }

            let new_value = parseInt(new_text);

            if (new_value > max_value) {
                new_value = max_value;
            }
            else if (new_value < min_value) {
                new_value = min_value;
            }

            document.getElementById('range').value = new_value;

            let action = new_value === max_value ? 'All in' : 'Raise';
            document.getElementById('raise').innerHTML = `${action} ${shortcut(new_value)}`;
        }
    }
}

let cached_sounds = {};

function playSound(file) {
    if(file in cached_sounds){
        cached_sounds[file].play();
    }
    else{
        let a = new Audio(file);
        a.play();
        cached_sounds[file] = a;
    }
}