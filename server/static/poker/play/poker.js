this.onmessage = function(event){
    console.log('in worker: ', event.data);

    data = event.data;

    if(data.type == 'start'){

        player_name = data.player_name;
        table_to_spectate = data.table_to_spectate;
        replay_id = data.replay_id;
        back_addr = data.back_addr;
        ip = data.ip;
        port = data.port;
        nick = data.nick;

        start();
    }
    else if(data.type == 'raise minus'){
        raise_minus(data.value, data.max_value, data.min_value);
    }
    else if(data.type == 'raise plus'){
        raise_plus(data.value, data.max_value, data.min_value);
    }
    else if(data.type == 'raise all'){
        raise_all(data.max_value);
    }
    else if(data.type == 'raise pot'){
        raise_pot(data.value, data.max_value);
    }
    else if(data.type == 'textraise'){
        textchange(data.text, data.max_value, data.min_value);
    }
    else if(data.type == 'socket close'){
        socket.close();
    }
    else if(data.type == 'socket stay'){
        socket.stay = true;
        socket.close();
    }
    else if(data.type == 'socket clean'){
        socket.clean = true;
        socket.close();
    }
    else if(data.type == 'set decision'){
        set_decision(data.value);
    }
    else if(data.type == 'pause play'){
        replay_pause_play();
    }
    else if(data.type == 'next step'){
        replay_next_step();
    }
    else if(data.type == 'prev hand'){
        replay_prev_hand();
    }
    else if(data.type == 'next hand'){
        replay_next_hand();
    }
    else if(data.type == 'tournament info'){
        t_info_click();
    }
    else if(data.type == 'last hand info'){
        lh_info_click();
    }
    else if(data.type == 'chat message'){
        chat_message(data.key, data.text);
    }
    else if(data.type == 'premove'){
        premove(data.answer, data.checked);
    }
}

function post_inner_html(obj){
    postMessage({type: 'inner html', obj: obj});
}

function post_change_value(id, value){
    postMessage({type: 'change value', id: id, value: value});
}

function post_remove_style(obj){
    postMessage({type: 'remove style', obj: obj});
}

function post_class_add(id, cls){
    postMessage({type: 'class add', id: id, class: cls});
}

function post_class_rem(obj){
    postMessage({type: 'class rem', obj: obj});
}

function post_src(obj){
    postMessage({type: 'src', obj: obj});
}

function post_src_hide(id1, id2){
    postMessage({type: 'src hide', id1: id1, id2: id2});
}

function post_margin(obj){
    postMessage({type: 'margin', obj: obj});
}

function post_alert(msg){
    postMessage({type: 'alert', msg: msg});
}

function post_location(location){
    postMessage({type: 'location', to: location});
}

function post_play_sound(file){
    if(!replay_in_pause){
        postMessage({type: 'sound', file: get_sound(file)});
    }
}

function post_add_to_chat(text){
    postMessage({type: 'add to chat', text: text});
}

function post_bigger_chat(){
    postMessage({type: 'bigger chat'});
}

function post_set_premove(obj){
    postMessage({type: 'premove', obj: obj});
}

console.log('in worker');

var available_chips = [[1000000000, '16'], 
                       [250000000, '15'], 
                       [100000000, '14'], 
                       [25000000, '13'], 
                       [5000000, '12'], 
                       [1000000, '11'], 
                       [500000, '10'], 
                       [100000, '9'], 
                       [25000, '8'], 
                       [5000, '7'], 
                       [1000, '6'], 
                       [500, '5'], 
                       [100, '4'], 
                       [25, '3'], 
                       [5, '2'], 
                       [1, '1']];
var socket;
var player_name;
var nick;
var table_to_spectate;
var replay_id;
var back_addr;
var ip;
var port;
var queue = [];
var wait_for_initialize = true;
var seats;
var total_seats;
var id_to_seat;
var real_seat_to_local_seat;
var seats_shift;
var button_el;
var main_stack;
var id_in_decision;
var to_call;
var is_t_info_active = false;
var is_lh_info_active = false;
var table_number;
var first_card;
var players_left;
var second_card;
var reconnect_mode = false;
var spectate_mode = false;
var replay_mode = false;
var resit_mode = false;
var premove_first = false;
var premove_second = false;
var premove_third = false;
var replay_in_pause = false;
var curr_id_thinking;
var time_thinking;
var interval_thinking;
var save_positions_chipstacks;
var frames_moving = 50;
var frames_last;
var cannot_move_chips = false;
var chipstack;
var my_id;
var is_in_game = false;

var gauss = [0, 0.001, 0.002, 0.003, 0.004, 0.006, 0.009, 0.013, 0.018, 0.024, 
             0.032, 0.042, 0.054, 0.068, 0.085, 0.105, 0.128, 0.155, 0.185, 0.219, 
             0.256, 0.296, 0.339, 0.384, 0.430, 0.477, 0.524, 0.571, 0.617, 0.662, 
             0.705, 0.745, 0.782, 0.816, 0.846, 0.873, 0.896, 0.916, 0.933, 0.947, 
             0.959, 0.969, 0.977, 0.983, 0.988, 0.992, 0.995, 0.997, 0.999, 1];

Array.prototype.remove = function(from, to) {
  var rest = this.slice((to || from) + 1 || this.length);
  this.length = from < 0 ? this.length + from : from;
  return this.push.apply(this, rest);
};

function get_src(card){
    return "/img/poker/cards/" + card + ".png";
}

function shortcut_number_for_player(num){

    num = num + '';

    if(num.length <= 3){
        return num;
    }
    else if(num.length <= 6){
        return num.substring(0, num.length - 3) + '&thinsp;' + num.substring(num.length - 3, num.length);
    }
    else if(num.length <= 9){
        return num.substring(0, num.length - 6) + '&thinsp;'+ 
            num.substring(num.length - 6, num.length - 3) + '&thinsp;' + 
            num.substring(num.length - 3, num.length);
    }
    else{
        return num.substring(0, num.length - 9) + '&thinsp;'
            num.substring(num.length - 9, num.length - 6) + '&thinsp;' + 
            num.substring(num.length - 6, num.length - 3) + '&thinsp;' + 
            num.substring(num.length - 3, num.length);
    }

}

function shortcut_number_for_decision(num){

    if(num < 1000){
        return num+'';
    }
    else if(num < 10000){
        num = num + '';
        return num.substring(0, num.length - 3) + '&thinsp;' + num.substring(num.length - 3, num.length);
    }
    else if(num < 100000){
        // 46776 -> 46.7k
        return (((num/100)|0)/10) + 'k' ;
    }
    else if(num < 1000000){
        // 123231 -> 123k
        return ((num/1000)|0) + 'k';
    }
    else if(num < 10000000){
        // 3 123 345 -> 3.12m
        return (((num/10000)|0)/100) + 'm';
    }
    else if(num < 100000000){
        // 12 345 678 -> 12.3m
        return (((num/100000)|0)/10) + 'm';
    }
    else if(num < 1000000000){
        // 123 345 678 -> 123m
        return ((num/1000000)|0) + 'm';
    }
    else if(num < 10000000000){
        // 1 123 345 678 -> 1.12b
        return (((num/10000000)|0)/100) + 'b';
    }
    else if(num < 100000000000){
        // 12 123 345 678 -> 12.1b
        return (((num/100000000)|0)/10) + 'b';
    }
    else {
        // 122 223 345 678 -> 123b
        return ((num/1000000000)|0) + 'b';
    }

}

function get_sound(file){

    if(file == 'chips'){
        type_sound = Math.random()*5|0

        return "/music/poker/chips/chip" + (type_sound+1) + ".mp3"
    }
    else if(file == 'fold'){
        return "/music/poker/cards/fold.mp3"
    }
    else if(file == 'check'){
        return "/music/poker/cards/check.mp3"
    }
    else if(file == 'attention'){
        return "/music/poker/attention/alert.mp3"
    }
    else if(file == 'collect'){
        return "/music/poker/chips/collect.mp3"
    }
    else if(file == 'grab'){
        return "/music/poker/chips/grab.mp3"
    }

}

function get_margin_left(i){

    if(i == 0){
        return 310;
    }
    else if(i == 1){
        return 310;
    }
    else if(i == 2){
        return 110;
    }
    else if(i == 3){
        return 70;
    }
    else if(i == 4){
        return 75;
    }
    else if(i == 5){
        return 140;
    }
    else if(i == 6){
        return 480;
    }
    else if(i == 7){
        return 545;
    }
    else if(i == 8){
        return 550;
    }
    else if(i == 9){
        return 510;
    }
    return 0;

}

function get_margin_top(i){

    if(i == 0){
        return -180;
    }
    else if(i == 1){
        return -80;
    }
    else if(i == 2){
        return -110;
    }
    else if(i == 3){
        return -200;
    }
    else if(i == 4){
        return -290;
    }
    else if(i == 5){
        return -380;
    }
    else if(i == 6){
        return -380;
    }
    else if(i == 7){
        return -290;
    }
    else if(i == 8){
        return -200;
    }
    else if(i == 9){
        return -100;
    }
    return 0;

}

function replay_pause_play(){

    clearTimeout(interval_thinking);

    if(replay_in_pause){

        replay_in_pause = false;

        post_class_add('replay_next_step', 'hidden');
        post_inner_html([{id: 'replay_pause_play', str: 'Pause'}]);

        socket.send('play');

    }
    else{

        replay_in_pause = true;

        post_class_rem([{id: 'replay_next_step', class: 'hidden'}]);
        post_inner_html([{id: 'replay_pause_play', str: 'Play'}]);

        socket.send('pause');

    }

}

function replay_next_step(){
    socket.send('next step');
}

function replay_prev_hand(){

    if(cannot_move_chips){
        setTimeout(replay_prev_hand, 10);
        return;
    }

    socket.send('prev hand');
    post_inner_html([{id: 'chat', str: 'Chat:'}]);
    clearTimeout(interval_thinking);
}

function replay_next_hand(){

    if(cannot_move_chips){
        setTimeout(replay_next_hand, 10);
        return;
    }

    socket.send('next hand');
    post_inner_html([{id: 'chat', str: 'Chat:'}]);
    clearTimeout(interval_thinking);
}

function update_info(id, reason, count=0){

    if(reason != '' && count > 0){
        reason = reason + ' ' + shortcut_number_for_decision(count);
    }

    seat = seats[id_to_seat[id]];
    post_inner_html([{id: 'p' + id_to_seat[id], str: seat.name + '<br>' + shortcut_number_for_player(seat.stack) + '<br>' + reason}]);

}

function set_empty_seat_info(seat){

    if(table_number == 0){
        post_class_add('p' + seat, 'hidden');
    }
    else{
        post_inner_html([{id: 'p' + seat, str: '<br>Empty seat'}]);
    }

}

function start_thinking(id){

    if(replay_in_pause == false){

        curr_id_thinking = id;
        time_thinking = 60;
        interval_thinking = setTimeout(loop_thinking, 1000);

    }
    
}

function loop_thinking(){

    time_thinking--;

    if(time_thinking <= 20 && time_thinking >= 0){
        update_info(curr_id_thinking, time_thinking + ' sec');
    }
    else if(time_thinking < 0){
        post_inner_html([{id: 'decisions', str: ''}]);
        return;
    }

    interval_thinking = setTimeout(loop_thinking, 1000);

}

function stop_thinking(){
    clearTimeout(interval_thinking);
}

function clear_table(){

    zz_src = get_src('ZZ');

    all_src = [{id: 'flop1', src: zz_src}, {id: 'flop2', src: zz_src}, {id: 'flop3', src: zz_src}, 
               {id: 'turn', src: zz_src}, {id: 'river', src: zz_src}]

    clear_decision();

    for(seat in seats){

        all_src.push({id: seats[seat].card1, src: zz_src});
        all_src.push({id: seats[seat].card2, src: zz_src});

        if(seats[seat].id != undefined){
            set_bet(seats[seat].id, 0);
        }

    }

    set_bet(-1, 0);

    post_src(all_src);

}

function textchange(text, max_value, min_value){

    if(text.length == 0){
        return;
    }
    else if(text.length == 1 && text == '0'){
        post_change_value('textraise', '');
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

        post_change_value('textraise', new_text);

        if(new_text == ''){
            new_text = min_value;
        }

        new_value = parseInt(new_text);

        if(new_value > max_value){
            new_value = max_value;
        }
        else if (new_value < min_value) {
            new_value = min_value;
        }

        post_change_value('range', new_value);
        post_inner_html([{id: 'raise', str: (new_value==max_value?"All in ":"Raise ") + shortcut_number_for_decision(new_value)}]);
    }

}

function chat_message(key, text){

    if(key == 13 && text.length > 0){ // enter key is 13

        post_change_value('message', '');

        if(!replay_mode){
            socket.send(JSON.stringify({type: 'chat', text: text}));
        }

    }
}


function raise_minus(value, max_value, min_value){

    new_value = (+value) - (+min_value) > min_value? (+value) - (+min_value): min_value;

    post_change_value('range', new_value);
    post_inner_html([{id: 'raise', str: (new_value==max_value?"All in ":"Raise ") + shortcut_number_for_decision(new_value)}]);

}

function raise_plus(value, max_value, min_value){

    new_value = (+value) + (+min_value) < max_value? (+value) + (+min_value) : max_value;

    post_change_value('range', new_value);
    post_inner_html([{id: 'raise', str: (new_value==max_value?"All in ":"Raise ") + shortcut_number_for_decision(new_value)}]);

}

function raise_all(max_value){

    post_change_value('range', max_value);
    post_inner_html([{id: 'raise', str: "All in " + shortcut_number_for_decision(max_value)}]);

}

function raise_pot(value, max_value){

    in_pot = main_stack.money;

    for(i in seats){

        if(seats[i].id != undefined){
            in_pot += seats[i].gived;
        }

    }

    raise_amount = in_pot + 2 * to_call;

    post_change_value('range', raise_amount);
    post_inner_html([{id: 'raise', str: (raise_amount==max_value?"All in ":"Raise ") + shortcut_number_for_decision(raise_amount)}]);

}

function t_info_click(){

    if(is_t_info_active === false){

        if(is_lh_info_active){
            lh_info_click();
        }

        is_t_info_active = true;
        post_class_rem([{id: 'tournament_info', class: 'hidden'}]);
    }
    else{

        is_t_info_active = false;
        post_class_add('tournament_info', 'hidden');

    }

}

function lh_info_click(){

    if(is_lh_info_active == false){

        if(is_t_info_active){
            t_info_click();
        }

        is_lh_info_active = true;
        post_class_rem([{id: 'last_hand_info', class: 'hidden'}]);

    }
    else{

        is_lh_info_active = false;
        post_class_add('last_hand_info', 'hidden');

    }

}

function premove(answer, checked){

    all_premoves = [{id: 'premove1', checked: false}, 
                    {id: 'premove2', checked: false}, 
                    {id: 'premove3', checked: false}];

    premove_first = false;
    premove_second = false;
    premove_third = false;

    if(checked){

        if(answer == '1'){
            all_premoves.push({id: 'premove1', checked: true});
            premove_first = true;
        }
        else if(answer == '2'){
            all_premoves.push({id: 'premove2', checked: true});
            premove_second = true;
        }
        else if(answer == '3'){
            all_premoves.push({id: 'premove3', checked: true});
            premove_third = true;
        }

    }

    post_set_premove(all_premoves);

}

function clear_decision(){

    if(total_seats == 2){
        to_place = [1, 6];
    }
    else if(total_seats == 3){
        to_place = [1, 4, 7];
    }
    else if(total_seats == 4){
        to_place = [1, 3, 6, 8];
    }
    else if(total_seats == 5){
        to_place = [1, 3, 5, 6, 8];
    }
    else if(total_seats == 6){
        to_place = [1, 2, 4, 6, 7, 9];
    }
    else if(total_seats == 7){
        to_place = [1, 2, 4, 5, 6, 7, 9];
    }
    else if(total_seats == 8){
        to_place = [1, 2, 3, 4, 6, 7, 8, 9];
    }
    else if(total_seats == 9){
        to_place = [1, 2, 3, 4, 5, 6, 7, 8, 9];
    }

    all_rem = [];

    for(i = 0; i < to_place.length; i++){

        all_rem.push({id: 'p' + to_place[i], class: 'in_decision'});

    }

    post_class_rem(all_rem);
}

function set_decision(to_send){

    post_inner_html([{id: 'decisions', str: ''}]);
    socket.send(JSON.stringify({type: 'decision', text: to_send}));

}

function made_controlled_player(is_fold){

    if(!spectate_mode && !replay_mode){

        premove('1', false);

        if(is_fold){
            is_in_game = false;
            post_class_add('premoves', 'hidden');
        }
        else{
            post_inner_html([{id: 'textpremove1', str: 'Check/Fold'}, 
                             {id: 'textpremove2', str: 'Check'}, 
                             {id: 'textpremove3', str: 'Call any'}]);
        }

    }

    

}

function set_bet(id, count, reason=''){

    if(id != -1){

        seats[id_to_seat[id]].stack -= count - seats[id_to_seat[id]].gived;
        seats[id_to_seat[id]].gived = count;

        update_info(id, reason, count);

    }

    pot_count = main_stack.money;

    for(var i in seats){

        if(seats[i].id != undefined){
            pot_count += seats[i].gived;
        }

    }

    post_inner_html([{id: 'pot_count', str: pot_count}]);

    amounts = [];

    for(var i = 0; i < available_chips.length; i++){
        if(count >= available_chips[i][0]){
            amounts.push([available_chips[i][1], count / available_chips[i][0] | 0]);
            count -= (count / available_chips[i][0] | 0) * available_chips[i][0];
        }
    }

    while(amounts.length > 8){

        min_betweens = -1;
        index_betweens = -1;

        for(i = 0; i < amounts.length - 1; i++){

            curr_between = 0;

            for(j = 1; j < amounts[i].length; j += 2){
                curr_between += amounts[i][j];
            }

            for(j = 1; j < amounts[i+1].length; j += 2){
                curr_between += amounts[i+1][j];
            }

            if(curr_between <= min_betweens || min_betweens == -1){
                min_betweens = curr_between;
                index_betweens = i;
            }

        }

        for(i = 0; i < amounts[index_betweens + 1].length; i++){
            amounts[index_betweens].push(amounts[index_betweens + 1][i]);
        }

        amounts.remove(index_betweens + 1);

    }

    if(id == -1){
        seat_to_set_bet = main_stack;
    }
    else{
        seat_to_set_bet = seats[id_to_seat[id]];
        player_id = 'p' + id_to_seat[id];
    }

    chip11 = seat_to_set_bet.ch11;
    chip12 = seat_to_set_bet.ch12;
    chip13 = seat_to_set_bet.ch13;
    chip14 = seat_to_set_bet.ch14;
    chip21 = seat_to_set_bet.ch21;
    chip22 = seat_to_set_bet.ch22;
    chip23 = seat_to_set_bet.ch23;
    chip24 = seat_to_set_bet.ch24;

    all_chips = [{id: chip11, str: ''}, {id: chip12, str: ''}, {id: chip13, str: ''}, {id: chip14, str: ''},
                 {id: chip21, str: ''}, {id: chip22, str: ''}, {id: chip23, str: ''}, {id: chip24, str: ''}]

    if(amounts.length == 8){
        chip_order = [chip21, chip22, chip23, chip24, chip11, chip12, chip13, chip14];
    }
    else if(amounts.length == 7){
        chip_order = [chip21, chip22, chip23, chip11, chip12, chip13, chip14];
    }
    else if(amounts.length == 6){
        chip_order = [chip21, chip22, chip11, chip12, chip13, chip14];
    }
    else if(amounts.length == 5){
        chip_order = [chip21, chip11, chip12, chip13, chip14];
    }
    else if(amounts.length == 4){
        chip_order = [chip11, chip12, chip13, chip14];
    }
    else if(amounts.length == 3){
        chip_order = [chip12, chip13, chip14];
    }
    else if(amounts.length == 2){
        chip_order = [chip12, chip13];
    }
    else if(amounts.length == 1){
        chip_order = [chip12];
    }

    for(i = 0; i < amounts.length; i++){
        curr_chips = chip_order[i];
        curr_height = 0;
        total_height_str = '';

        for(j = 1; j < amounts[i].length; j += 2){

            for(k = 0; k < amounts[i][j]; k++){

                total_height_str += '<img class=chip src="/img/poker/chips/' + amounts[i][j-1] + '.png" style="margin-top: -' + curr_height + 'px">';
                curr_height += 5;

            }

        }

        all_chips.push({id: curr_chips, str: total_height_str});

    }

    post_inner_html(all_chips);

}

function move_stacks_to_main(){

    frames_last -= 1;

    all_margin = [];

    if(frames_last != 0){

        percent_done = gauss[frames_moving - frames_last - 1];

        for(i = 0; i < save_positions_chipstacks.length; i++){

            curr_chipstack = save_positions_chipstacks[i];

            all_margin.push({id: curr_chipstack[1], 
                             left: (curr_chipstack[2] + (((curr_chipstack[4] - curr_chipstack[2]) * percent_done) | 0)) + 'px',
                             top: (curr_chipstack[3] + (((curr_chipstack[5] - curr_chipstack[3]) * percent_done) | 0)) + 'px'});

        }

        post_margin(all_margin);

        setTimeout(move_stacks_to_main, 10);
    }
    else{

        cannot_move_chips = false;

        for(i = 0; i < save_positions_chipstacks.length; i++){

            curr_chipstack = save_positions_chipstacks[i];

            all_margin.push({id: curr_chipstack[1], left: curr_chipstack[2] + 'px', top: curr_chipstack[3] + 'px'});

            set_bet(seats[curr_chipstack[0]].id, 0);

        }

        set_bet(-1, main_stack.money);

        post_margin(all_margin);

    }

}

function move_stack_from_main(){

    frames_last -= 1;

    if(frames_last != 0){

        percent_done = gauss[frames_last];

        post_margin([{id: chipstack[1], 
                     left: (chipstack[2] + (((chipstack[4] - chipstack[2]) * percent_done) | 0)) + 'px', 
                     top: (chipstack[3] + (((chipstack[5] - chipstack[3]) * percent_done) | 0)) + 'px'}]);

        setTimeout(move_stack_from_main, 10);
    }
    else{

        cannot_move_chips = false;

        post_margin([{id: chipstack[1], left: chipstack[2] + 'px', top: chipstack[3] + 'px'}]);

    }

}

function collect_money(){

    if(cannot_move_chips){
        return;
    }

    clear_decision();

    save_positions_chipstacks = [];

    main_stack_margin_left = get_margin_left(0);
    main_stack_margin_top = get_margin_top(0);

    all_chips = [];

    for(i in seats){

        if(seats[i].id != undefined && seats[i].gived > 0){

            main_stack.money += seats[i].gived;
            seats[i].stack -= seats[i].gived;

            chipstack = 'ch' + i;

            all_chips.push({id: chipstack});

            chipstack_margin_left = get_margin_left(i);
            chipstack_margin_top = get_margin_top(i);

            save_positions_chipstacks.push([i, chipstack, chipstack_margin_left, chipstack_margin_top,
                                                          main_stack_margin_left, main_stack_margin_top])

            if(replay_in_pause || reconnect_mode){
                set_bet(seats[i].id, 0);
            }

        }

    }

    post_remove_style(all_chips);

    if(save_positions_chipstacks.length > 0){

        if(!replay_in_pause && !reconnect_mode){

            frames_last = frames_moving;
            cannot_move_chips = true;

            setTimeout(move_stacks_to_main, 10);
        }
        else{
            set_bet(-1, main_stack.money);
        }

    }

}

function handle(){

    if(queue.length == 0){
        setTimeout(handle, 10);
        return;
    }

    data = queue.shift();

    if(data.type == 'broken'){
        socket.close();
        return;
    }

    if(data.type == 'finish'){

        socket.clean = true;

        to_general_info = data.msg;
        to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");' +
                           'post_socket_close();\'>Ok</div>';

        post_inner_html([{id: 'general_info', str: to_general_info}]);
        post_class_rem([{id: 'general_info', class: 'hidden'}]);

        return;
    }

    if(data.type == 'info'){

        to_general_info = data.msg;
        to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");\'>Ok</div>';

        post_inner_html([{id: 'general_info', str: to_general_info}]);
        post_class_rem([{id: 'general_info', class: 'hidden'}]);

        setTimeout(handle, 10);
        return;
    }

    if(data.type == 'reconnect start'){
        reconnect_mode = true;
        handle();
        return;
    }

    if(data.type == 'reconnect end'){
        reconnect_mode = false;

        if(!spectate_mode && !resit_mode && !replay_mode){

            to_general_info = 'Reconnection was successful.';
            to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");\'>Ok</div>';

            post_inner_html([{id: 'general_info', str: to_general_info}]);
            post_class_rem([{id: 'general_info', class: 'hidden'}]);

        }

        resit_mode = false;

        handle();
        return;
    }

    if(!reconnect_mode && wait_for_initialize && data.type != 'init hand'){
        setTimeout(handle, 10);
        return;
    }

    console.log(data);


    if(data.type == 'init hand'){

        all_inner_html = []

        if(wait_for_initialize){

            wait_for_initialize = false;

            if(!spectate_mode && !replay_mode){
                to_general_info = 'Game started. Good luck!';
            }
            else{

                if(data.table_number != 0){
                    to_general_info = 'You are watching table #' + data.table_number;
                }
                else{
                    to_general_info = 'You are watching final table';
                }

            }
            
            to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");\'>Ok</div>';

            all_inner_html.push({id: 'general_info', str: to_general_info});

            post_class_rem([{id: 'general_info', class: 'hidden'}, {id: 'tournament_info_button', class: 'hidden'}, 
                {id: 'last_hand_info_button', class: 'hidden'}, {id: 'table_num', class: 'hidden'}, 
                {id: 'hand_num_short_info', class: 'hidden'}, {id: 'place_short_info', class: 'hidden'}, {id: 'chat', class: 'hidden'}, 
                {id: 'big_blind', class: 'hidden'}, {id: 'small_blind', class: 'hidden'}, {id: 'ante', class: 'hidden'}]);

            if(!replay_mode){
                post_class_rem([{id: 'message', class: 'hidden'}]);
            }
            
        }
        

        if(data.table_number == 0){
            all_inner_html.push({id: 'table_num_info', str: 'final table'});
            all_inner_html.push({id: 'table_num', str: 'Final table'});
        }
        else{
            all_inner_html.push({id: 'table_num_info', str: 'table #' + shortcut_number_for_player(data.table_number)});
            all_inner_html.push({id: 'table_num', str: 'Table #' + shortcut_number_for_player(data.table_number)});
        }

        all_inner_html.push({id: 'hand_num_info', str: shortcut_number_for_player(data.hand_number)});
        all_inner_html.push({id: 'hand_num', str: shortcut_number_for_player(data.hand_number)});
        all_inner_html.push({id: 'ante_info', str: shortcut_number_for_decision(data.ante)});
        all_inner_html.push({id: 'ante_shortcut', str: shortcut_number_for_decision(data.ante)});
        all_inner_html.push({id: 'sb_info', str: shortcut_number_for_decision(data.sb)});
        all_inner_html.push({id: 'small_blind_shortcut', str: shortcut_number_for_decision(data.sb)});
        all_inner_html.push({id: 'bb_info', str: shortcut_number_for_decision(data.bb)});
        all_inner_html.push({id: 'big_blind_shortcut', str: shortcut_number_for_decision(data.bb)});
        all_inner_html.push({id: 'average_stack_info', str: shortcut_number_for_player(data.avg_stack)});
        all_inner_html.push({id: 'players_left_info', str: shortcut_number_for_player(data.players_left)});

        post_remove_style([{id: 'ch0'}, {id: 'ch1'}, {id: 'ch2'}, {id: 'ch3'}, {id: 'ch4'}, 
                           {id: 'ch5'}, {id: 'ch6'}, {id: 'ch7'}, {id: 'ch8'}, {id: 'ch9'}]);

        if(replay_mode || spectate_mode){
            all_inner_html.push({id: 'place_short_info', str: shortcut_number_for_player(data.players_left)});
        }

        players_left = data.players_left;

        total_seats = data.seats;

        ante = data.ante;
        sb = data.sb;
        bb = data.bb;

        players = data.players;
        table_number = data.table_number;

        if(seats == undefined || replay_mode == true){

            seats_shift = 0;

            need_to_shift = false;

            if(!spectate_mode && !replay_mode){
                for(var i = 0; i < players.length; i++){
                    if(players[i].controlled){
                        need_to_shift = true;
                        my_id = players[i].id;
                        break;
                    }

                }

                if(need_to_shift){
                    while(players[0].controlled == undefined || players[0].controlled == false){
                        players.push(players.shift());
                        seats_shift++;
                    }
                }
            }

            if(data.seats == 2){
                to_place = [1, 6];
            }
            else if(data.seats == 3){
                to_place = [1, 4, 7];
            }
            else if(data.seats == 4){
                to_place = [1, 3, 6, 8];
            }
            else if(data.seats == 5){
                to_place = [1, 3, 5, 6, 8];
            }
            else if(data.seats == 6){
                to_place = [1, 2, 4, 6, 7, 9];
            }
            else if(data.seats == 7){
                to_place = [1, 2, 4, 5, 6, 7, 9];
            }
            else if(data.seats == 8){
                to_place = [1, 2, 3, 4, 6, 7, 8, 9];
            }
            else if(data.seats == 9){
                to_place = [1, 2, 3, 4, 5, 6, 7, 8, 9];
            }

            if(seats != undefined){
                for(seat in seats){
                    if(seats[seat].id != undefined && seats[seat].disconnected){
                        post_class_rem([{id: 'p' + seat, class: 'is_disconnected'}]);
                    }
                }
            }

            seats = {}
            id_to_seat = {}
            real_seat_to_local_seat = {}

            all_inner_html.push({id: 'players', str: ''});

            doc_players = '';

            for(var i = 0; i < to_place.length; i++){

                if(players[i].id !== null){

                    doc_players += '<div id="p' + to_place[i] + '" class="player' + (players[i].disconnected? ' is_disconnected': '') + 
                                        '">' + players[i].name + '<br>' + shortcut_number_for_player(data.players[i].stack) + '</div>';

                    seats[to_place[i]] = {
                        'id': players[i].id,
                        'name': players[i].name,
                        'real_seat': (seats_shift + i) % data.seats,
                        'stack': players[i].stack,
                        'disconnected': players[i].disconnected,
                        'gived': 0,
                        'card1': 'c' + to_place[i] + '1',
                        'card2': 'c' + to_place[i] + '2',
                        'ch11': 'p' + to_place[i] + 'r1c1',
                        'ch12': 'p' + to_place[i] + 'r1c2',
                        'ch13': 'p' + to_place[i] + 'r1c3',
                        'ch14': 'p' + to_place[i] + 'r1c4',
                        'ch21': 'p' + to_place[i] + 'r2c1',
                        'ch22': 'p' + to_place[i] + 'r2c2',
                        'ch23': 'p' + to_place[i] + 'r2c3',
                        'ch24': 'p' + to_place[i] + 'r2c4',
                    };

                    id_to_seat[players[i].id] = to_place[i];
                    real_seat_to_local_seat[(seats_shift + i) % data.seats] = to_place[i];

                }
                else{

                    if(data.table_number != 0){
                        doc_players += '<div id="p' + to_place[i] + '" class="player"><br>Empty seat</div>';
                    }
                    else{
                        doc_players += '<div id="p' + to_place[i] + '" class="player hidden"><br>Empty seat</div>';
                    }

                    seats[to_place[i]] = {
                        'id': undefined,
                        'real_seat': (seats_shift + i) % data.seats,
                        'card1': 'c' + to_place[i] + '1',
                        'card2': 'c' + to_place[i] + '2',
                        'ch11': 'p' + to_place[i] + 'r1c1',
                        'ch12': 'p' + to_place[i] + 'r1c2',
                        'ch13': 'p' + to_place[i] + 'r1c3',
                        'ch14': 'p' + to_place[i] + 'r1c4',
                        'ch21': 'p' + to_place[i] + 'r2c1',
                        'ch22': 'p' + to_place[i] + 'r2c2',
                        'ch23': 'p' + to_place[i] + 'r2c3',
                        'ch24': 'p' + to_place[i] + 'r2c4',
                    };

                    real_seat_to_local_seat[(seats_shift + i) % data.seats] = to_place[i];

                }
            }

            all_inner_html.push({id: 'players', str: doc_players});

            main_stack = {
                'ch11': 'p0r1c1',
                'ch12': 'p0r1c2',
                'ch13': 'p0r1c3',
                'ch14': 'p0r1c4',
                'ch21': 'p0r2c1',
                'ch22': 'p0r2c2',
                'ch23': 'p0r2c3',
                'ch24': 'p0r2c4',
                'money': 0,
            }

        } else {

            for(i = 0; i < players.length; i++){

                if(players[i].id != undefined){

                    curr_seat = seats[id_to_seat[players[i].id]];

                    curr_seat.stack = players[i].stack;
                    curr_seat.name = players[i].name;

                }

            }

        }

        top9_info = '';

        for(i = 0; i < data.top_9.length; i++){

            top9_info += '<tr><td>' + (i+1) + ')</td><td>' + shortcut_number_for_player(data.top_9[i].stack) + '</td><td>' + data.top_9[i].name + '</td></tr>'

        }

        all_inner_html.push({id: 'top_players_info', str: top9_info});

        post_inner_html(all_inner_html);

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'ante'){

        paid = data.paid;

        for(i = 0; i < paid.length; i++){

            set_bet(paid[i].id, paid[i].paid, 'Ante');

        }

        if(reconnect_mode){
            handle();
        }
        else{
            post_play_sound('chips');
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'collect money'){

        collect_money();

        if(reconnect_mode){
            handle();
        }
        else{
            post_play_sound('collect');
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'blinds'){

        button_id = data.button;

        post_class_rem([{id: 'dealer', class: 'd1'}, {id: 'dealer', class: 'd2'}, {id: 'dealer', class: 'd3'}, 
            {id: 'dealer', class: 'd4'}, {id: 'dealer', class: 'd5'}, {id: 'dealer', class: 'd6'}, 
            {id: 'dealer', class: 'd7'}, {id: 'dealer', class: 'd8'}, {id: 'dealer', class: 'd9'}]);

        post_class_add('dealer', 'd' + id_to_seat[button_id]);

        if(data.info.length == 1){
            set_bet(data.info[0].id, data.info[0].paid, 'BB');
            curr_bb = data.info[0].paid;
            curr_bb_id = data.info[0].id;
        }
        else{
            set_bet(data.info[0].id, data.info[0].paid, 'SB');
            set_bet(data.info[1].id, data.info[1].paid, 'BB');
            curr_bb = data.info[1].paid;
            curr_bb_id = data.info[1].id;
        }

        if(!replay_mode && !spectate_mode){

            post_class_rem([{id: 'premoves', class: 'hidden'}]);
            is_in_game = true;

            if(curr_bb_id == my_id){
                post_inner_html([{id: 'textpremove1', str: 'Check/Fold'}, 
                                 {id: 'textpremove2', str: 'Check'}, 
                                 {id: 'textpremove3', str: 'Call any'}]);
            }
            else{
                post_inner_html([{id: 'textpremove1', str: 'Fold'}, 
                                 {id: 'textpremove2', str: 'Call ' + curr_bb}, 
                                 {id: 'textpremove3', str: 'Call any'}]);
            }

        }

        

        if(reconnect_mode){
            handle();
        }
        else{
            post_play_sound('chips');
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'blinds increased'){

        to_general_info = 'Blinds now ' + data.sb + ' / ' + data.bb;

        if(data.ante != 0){
            to_general_info += ' ante ' + data.ante;
        }

        to_general_info += '.';

        to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");\'>Ok</div>';

        post_inner_html([{id: 'general_info', str: to_general_info}, {id: 'big_blind_shortcut', str: data.bb}, 
                         {id: 'small_blind_shortcut', str: data.sb}, {id: 'ante_shortcut', str: data.ante}]);

        post_class_rem([{id: 'general_info', class: 'hidden'}]);

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'give cards'){

        up_src = get_src('UP');

        all_src = [];

        for(i in seats){

            if(i == 1){

                all_src.push({id: seats[1].card1, src: get_src(data.first)});
                all_src.push({id: seats[1].card2, src: get_src(data.second)});

                first_card = data.first;
                second_card = data.second;
            }
            else if(seats[i].id != undefined){

                all_src.push({id: seats[i].card1, src:  up_src});
                all_src.push({id: seats[i].card2, src:  up_src});

            }
            
        }

        post_src(all_src);

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'deal cards'){

        up_src = get_src('UP');

        all_src = [];

        for(i in seats){

            if(seats[i].id != undefined){

                if(i != 1 || (i == 1 && !resit_mode)){

                    all_src.push({id: seats[i].card1, src: up_src});
                    all_src.push({id: seats[i].card2, src: up_src});

                }
            }
        }

        post_src(all_src);

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'delete player'){

        _seat = id_to_seat[data.id];

        set_bet(data.id, 0);

        seats[_seat].id = undefined;

        if(seats[_seat].disconnected){
            seats[_seat].disconnected = false;
            post_class_rem([{id: 'p' + _seat, class: 'is_disconnected'}]);
        }

        post_src([{id: seats[_seat].card1, src: get_src('ZZ')}, {id: seats[_seat].card2, src: get_src('ZZ')}]);

        set_empty_seat_info(_seat);

        id_to_seat[data.id] = undefined;

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'add player'){

        seat = seats[real_seat_to_local_seat[data.seat]];

        seat.id = data.id;
        seat.gived = 0;
        seat.name = data.name;
        seat.stack = data.stack;
        seat.disconnected = false;

        id_to_seat[seat.id] = real_seat_to_local_seat[data.seat];

        if(table_number == 0){
            post_class_rem([{id: 'p' + real_seat_to_local_seat[data.seat], class: 'hidden'}]);
            update_info(data.id, '');
        }
        else{
            update_info(data.id, 'New player');
        }

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'resit'){

        resit_mode = true;

        all_inner_html = []

        if(data.table_number == 0){
            to_general_info = 'You was resit on final table.';
            to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");\'>Ok</div>';

            post_inner_html([{id: 'general_info', str: to_general_info}]);
            post_class_rem([{id: 'general_info', class: 'hidden'}]);

            post_inner_html([{id: 'table_num_info', str: 'final table'}]);
        }
        else{
            to_general_info = 'You was resit on table #' + data.table_number;
            to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");\'>Ok</div>';

            post_inner_html([{id: 'general_info', str: to_general_info}]);
            post_class_rem([{id: 'general_info', class: 'hidden'}]);

            post_inner_html([{id: 'table_num_info', str: 'table #' + data.table_number}]);
        }

        players = data.players;
        table_number = data.table_number;

        seats_shift = 0;

        while(players[0].id == null || players[0].controlled == false){
            players.push(players.shift());
            seats_shift++;
        }

        data.seats = total_seats;


        if(data.seats == 2){
            to_place = [1, 6];
        }
        else if(data.seats == 3){
            to_place = [1, 4, 7];
        }
        else if(data.seats == 4){
            to_place = [1, 3, 6, 8];
        }
        else if(data.seats == 5){
            to_place = [1, 3, 5, 6, 8];
        }
        else if(data.seats == 6){
            to_place = [1, 2, 4, 6, 7, 9];
        }
        else if(data.seats == 7){
            to_place = [1, 2, 4, 5, 6, 7, 9];
        }
        else if(data.seats == 8){
            to_place = [1, 2, 3, 4, 6, 7, 8, 9];
        }
        else if(data.seats == 9){
            to_place = [1, 2, 3, 4, 5, 6, 7, 8, 9];
        }

        for(seat in seats){
            if(seats[seat].id != undefined && seats[seat].disconnected){
                post_class_rem([{id: 'p' + seat, class: 'is_disconnected'}]);
            }
        }

        seats = {}
        id_to_seat = {}
        real_seat_to_local_seat = {}

        for(var i = 0; i < to_place.length; i++){

            if(players[i].id !== null){

                all_inner_html.push({id: 'p' + to_place[i], str:  players[i].name + '<br>' + shortcut_number_for_player(players[i].stack)});

                if(players[i].disconnected){
                    post_class_add('p' + to_place[i], 'is_disconnected');
                }

                seats[to_place[i]] = {
                    'id': players[i].id,
                    'name': players[i].name,
                    'real_seat': (seats_shift + i) % data.seats,
                    'stack': players[i].stack,
                    'disconnected': players[i].disconnected,
                    'gived': 0,
                    'card1': 'c' + to_place[i] + '1',
                    'card2': 'c' + to_place[i] + '2',
                    'ch11': 'p' + to_place[i] + 'r1c1',
                    'ch12': 'p' + to_place[i] + 'r1c2',
                    'ch13': 'p' + to_place[i] + 'r1c3',
                    'ch14': 'p' + to_place[i] + 'r1c4',
                    'ch21': 'p' + to_place[i] + 'r2c1',
                    'ch22': 'p' + to_place[i] + 'r2c2',
                    'ch23': 'p' + to_place[i] + 'r2c3',
                    'ch24': 'p' + to_place[i] + 'r2c4',
                };

                id_to_seat[players[i].id] = to_place[i];
                real_seat_to_local_seat[(seats_shift + i) % data.seats] = to_place[i];

            }
            else{

                all_inner_html.push({id: 'p' + to_place[i], str:  '<br>Empty seat'});

                if(data.table_number == 0){

                    post_class_add('p' + to_place[i], 'hidden');

                }

                seats[to_place[i]] = {
                    'id': undefined,
                    'real_seat': (seats_shift + i) % data.seats,
                    'card1': 'c' + to_place[i] + '1',
                    'card2': 'c' + to_place[i] + '2',
                    'ch11': 'p' + to_place[i] + 'r1c1',
                    'ch12': 'p' + to_place[i] + 'r1c2',
                    'ch13': 'p' + to_place[i] + 'r1c3',
                    'ch14': 'p' + to_place[i] + 'r1c4',
                    'ch21': 'p' + to_place[i] + 'r2c1',
                    'ch22': 'p' + to_place[i] + 'r2c2',
                    'ch23': 'p' + to_place[i] + 'r2c3',
                    'ch24': 'p' + to_place[i] + 'r2c4',
                };

                real_seat_to_local_seat[(seats_shift + i) % data.seats] = to_place[i];

            }
        }

        post_inner_html(all_inner_html);

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'switch decision'){

        clear_decision();

        post_class_add('p' + id_to_seat[data.id], 'in_decision');

        id_in_decision = data.id;

        start_thinking(data.id);

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'made decision'){

        stop_thinking();

        if(data.result == 'fold'){

            if(id_in_decision == my_id){
                made_controlled_player(true);
            }

            if(id_to_seat[id_in_decision] == 1 && !spectate_mode && !replay_mode){

                post_src_hide(seats[1].card1, seats[1].card2);

            }
            else if(replay_mode){

                post_src_hide(seats[id_to_seat[id_in_decision]].card1, seats[id_to_seat[id_in_decision]].card2);

            }
            else{
                post_src([{id: seats[id_to_seat[id_in_decision]].card1, src: get_src('ZZ')}, 
                    {id: seats[id_to_seat[id_in_decision]].card2, src: get_src('ZZ')}]);

            }

            update_info(id_in_decision, 'Fold');

        }
        else if(data.result == 'check'){

            if(id_in_decision == my_id){
                post_class_rem([{id: 'premoves', class: 'hidden'}]);
                post_inner_html([{id: 'textpremove1', str: 'Check/Fold'}, 
                                 {id: 'textpremove2', str: 'Check'}, 
                                 {id: 'textpremove3', str: 'Call any'}]);
                premove('1', false);
            }

            update_info(id_in_decision, 'Check');

        }
        else if(data.result == 'call'){

            if(id_in_decision == my_id){

                post_class_rem([{id: 'premoves', class: 'hidden'}]);
                post_inner_html([{id: 'textpremove1', str: 'Check/Fold'}, 
                                 {id: 'textpremove2', str: 'Check'}, 
                                 {id: 'textpremove3', str: 'Call any'}]);

                premove('1', false);
            }

            set_bet(id_in_decision, data.money, 'Call');

        }
        else if(data.result == 'raise'){

            if(is_in_game && id_in_decision != my_id && !spectate_mode && !replay_mode){

                myself = seats[id_to_seat[my_id]];

                if(myself.stack + myself.gived > data.money){

                    post_inner_html([{id: 'textpremove1', str: 'Fold'}, 
                                 {id: 'textpremove2', str: 'Call ' + data.money}, 
                                 {id: 'textpremove3', str: 'Call any'}]);

                }
                else{

                    post_class_add('premove3', 'hidden');

                    post_inner_html([{id: 'textpremove1', str: 'Fold'}, 
                                 {id: 'textpremove2', str: 'Call ' + data.money}, 
                                 {id: 'textpremove3', str: ''}]);

                }

                if(premove_second){
                    premove('2', false);
                }
            }
            else if(id_in_decision == my_id){

                post_class_rem([{id: 'premoves', class: 'hidden'}]);
                post_inner_html([{id: 'textpremove1', str: 'Check/Fold'}, 
                                 {id: 'textpremove2', str: 'Check'}, 
                                 {id: 'textpremove3', str: 'Call any'}]);

                premove('1', false);
            }

            set_bet(id_in_decision, data.money, 'Raise');

        }
        else if(data.result == 'all in'){

            if(is_in_game && id_in_decision != my_id && !spectate_mode && !replay_mode){

                myself = seats[id_to_seat[my_id]];

                if(myself.stack + myself.gived > data.money){

                    post_inner_html([{id: 'textpremove1', str: 'Fold'}, 
                                 {id: 'textpremove2', str: 'Call ' + data.money}, 
                                 {id: 'textpremove3', str: 'Call any'}]);

                }
                else{

                    post_class_add('premove3', 'hidden');

                    post_inner_html([{id: 'textpremove1', str: 'Fold'}, 
                                 {id: 'textpremove2', str: 'Call ' + data.money}, 
                                 {id: 'textpremove3', str: ''}]);

                }

                if(premove_second){
                    premove('2', false);
                }
            }
            else if(id_in_decision == my_id){
                premove('1', false);
            }

            set_bet(id_in_decision, data.money, 'All in');

        }

        post_inner_html([{id: 'decisions', str: ''}]);

        if(reconnect_mode){
            handle();
        }
        else{

            if(data.result == 'all in' || data.result == 'raise' || data.result == 'call'){
                post_play_sound('chips');
            }
            else if(data.result == 'fold'){
                post_play_sound('fold');
            }
            else if(data.result == 'check'){
                post_play_sound('check');
            }

            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'excess money'){

        set_bet(data.id, seats[id_to_seat[data.id]].gived - data.money);

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'flop'){

        clear_decision();

        post_src([{id: 'flop1', src: get_src(data.card1)}, 
                  {id: 'flop2', src: get_src(data.card2)}, 
                  {id: 'flop3', src: get_src(data.card3)}]);

        if(reconnect_mode){
            handle();
        }
        else{
            post_play_sound("fold");
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'turn'){

        clear_decision();

        post_src([{id: 'turn', src: get_src(data.card)}]);

        if(reconnect_mode){
            handle();
        }
        else{
            post_play_sound("fold");
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'river'){

        clear_decision();

        post_src([{id: 'river', src: get_src(data.card)}]);

        if(reconnect_mode){
            handle();
        }
        else{
            post_play_sound("fold");
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'open cards'){

        clear_decision();

        if(!spectate_mode && !replay_mode){
            made_controlled_player(true);
            post_class_rem([{id: 'premove3', class: 'hidden'}]);
        }

        all_src = [];

        for(i = 0; i < data.cards.length; i++){

            seat = seats[id_to_seat[data.cards[i].id]];

            all_src.push({id: seat.card1, src: get_src(data.cards[i].card1)});
            all_src.push({id: seat.card2, src: get_src(data.cards[i].card2)});

        }

        post_src(all_src);

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'give money'){

        if(!spectate_mode && !replay_mode){
            made_controlled_player(true);
            post_class_rem([{id: 'premove3', class: 'hidden'}]);
        }

        _chipstack = 'ch' + id_to_seat[data.id];
        main_chipstack = 'ch0';

        main_stack_margin_left = get_margin_left(0);
        main_stack_margin_top = get_margin_top(0);

        chipstack_margin_left = get_margin_left(id_to_seat[data.id]);
        chipstack_margin_top = get_margin_top(id_to_seat[data.id]);

        chipstack = [data.id, _chipstack, chipstack_margin_left, chipstack_margin_top,
                                   main_stack_margin_left, main_stack_margin_top]

        seats[id_to_seat[data.id]].stack += data.money;
        set_bet(data.id, data.money, 'Win');

        main_stack.money -= data.money;
        set_bet(-1, main_stack.money);

        if(!replay_in_pause && !reconnect_mode){

            frames_last = frames_moving;
            cannot_move_chips = true;

            move_stack_from_main();
            post_play_sound('grab');
        }

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'money results'){

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'hand results'){

        if(!spectate_mode && !replay_mode){
            post_src([{id: 'your_first_info', src: get_src(first_card)}, {id: 'your_second_info', src: get_src(second_card)}]);
        }

        post_src([{id: 'flop1_info', src: get_src(data.flop1)}, {id: 'flop2_info', src: get_src(data.flop2)}, 
            {id: 'flop3_info', src: get_src(data.flop3)}, {id: 'turn_info', src: get_src(data.turn)}, 
            {id: 'river_info', src: get_src(data.river)}]);

        table_fill = '';

        for(i = 0; i < data.results.length; i++){

            table_fill += '<tr><td><img class=small_card src="/img/poker/cards/' + data.results[i].first + '.png">';
            table_fill += '<img class=small_card src="/img/poker/cards/' + data.results[i].second + '.png">';
            table_fill += '</td><td>' + data.results[i].name + '</td><td>';
            table_fill += '<img class=small_card src="/img/poker/cards/' + data.results[i].card1 + '.png">';
            table_fill += '<img class=small_card src="/img/poker/cards/' + data.results[i].card2 + '.png">';
            table_fill += '<img class=small_card src="/img/poker/cards/' + data.results[i].card3 + '.png">';
            table_fill += '<img class=small_card src="/img/poker/cards/' + data.results[i].card4 + '.png">';
            table_fill += '<img class=small_card src="/img/poker/cards/' + data.results[i].card5 + '.png">';
            table_fill += '</td></tr>';

        }

        post_inner_html([{id: 'cards_reveal', str: table_fill}]);

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'busted'){

        socket.clean = true;

        to_general_info = 'You are busted! You finished ' + data.place + '.';

        to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");' + 
                           'post_socket_stay();\'>Watch</div>';

        to_general_info += '<div class="button in_general g2" onclick=\'document.getElementById("general_info").classList.add("hidden");' + 
                           'post_socket_close();\'>Quit</div>';

        post_inner_html([{id: 'general_info', str: to_general_info}]);
        post_class_rem([{id: 'general_info', class: 'hidden'}]);

    }
    else if(data.type == 'clear'){

        clear_table();

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'win'){

        socket.clean = true;

        to_general_info = 'Congratulations! You are winner!';
        to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");' + 
                           'post_socket_close();\'>Ok</div>';

        post_inner_html([{id: 'general_info', str: to_general_info}]);
        post_class_rem([{id: 'general_info', class: 'hidden'}]);

    }
    else if(data.type == 'place'){

        post_inner_html([{id: 'place_info', str: data.place}]);

        if(!replay_mode && !spectate_mode){
            post_inner_html([{id: 'place_short_info', str: data.place + ' / ' + players_left}]);
        }

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'chat'){

        post_add_to_chat(data.text);

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'disconnected'){

        post_class_add('p' + id_to_seat[data.id], 'is_disconnected');
        seats[id_to_seat[data.id]].disconnected = true;

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'connected'){

        post_class_rem([{id: 'p' + id_to_seat[data.id], class: 'is_disconnected'}]);
        seats[id_to_seat[data.id]].disconnected = false;

        if(reconnect_mode){
            handle();
        }
        else{
            setTimeout(handle, 10);
        }

    }
    else if(data.type == 'set decision'){

        if(reconnect_mode){
            handle();
            return;
        }

        if(premove_first){

            if(data.decisions[1].type == 'check'){
                set_decision('2');
                made_controlled_player(false);
                setTimeout(handle, 10);
                return;
            }
            else{
                set_decision('1');
                made_controlled_player(true);
                setTimeout(handle, 10);
                return;
            }
            
        }
        else if(premove_second){
            set_decision('2');
            made_controlled_player(false);
            setTimeout(handle, 10);
            return;
        }
        else if(premove_third){
            set_decision('2');
            made_controlled_player(false);
            setTimeout(handle, 10);
            return;
        }

        post_class_rem([{id: 'premoves', class: 'hidden'}]);

        post_play_sound('attention');

        decisions = '';

        for(i = 0; i < data.decisions.length; i++){

            if(data.decisions[i].type == 'fold'){
                decisions += "<div class='button fold_button' onclick='post_set_decision(\"" + (i+1) + "\")'>Fold</div>";
            }
            else if(data.decisions[i].type == 'check'){
                decisions += "<div class='button call_button' onclick='post_set_decision(\"" + (i+1) + "\")'>Check</div>";
            }
            else if(data.decisions[i].type == 'call'){
                decisions += "<div class='button call_button' onclick='post_set_decision(\"" + (i+1) + "\")'>Call " + 
                                                    shortcut_number_for_decision(data.decisions[i].money) + "</div>";
                to_call = data.decisions[i].money;
            }
            else if(data.decisions[i].type == 'raise'){
                decisions += "<div id=raise class='button raise_button' onclick='post_set_decision(\"" + (i+1) + 
                                        " \" + document.getElementById(\"range\").value)'>Raise " + 
                                        shortcut_number_for_decision(data.decisions[i].from) + "</div>";

                decisions += "<input id=range type=range min=" + data.decisions[i].from + " max=" + data.decisions[i].to + 
                                    " step=1 onmousemove='document.getElementById(\"raise\").innerHTML = (this.value==this.max?\"All in \":\"Raise \")" +
                                    "+ shortcut(this.value)' onchange='document.getElementById(\"raise\").innerHTML = " +
                                    "(this.value==this.max?\"All in \":\"Raise \") + shortcut(this.value)' value=" + data.decisions[i].from + ">";

                decisions += "<input id=textraise type=text class=input_button placeholder='input amount' onkeyup='post_textchange(this.value)'>";

                decisions += "<div class='button small_button minus_button' onclick='post_raise_minus()'>-</div>" +
                                       "<div class='button small_button plus_button' onclick='post_raise_plus()'>+</div>" +
                                       "<div class='button small_button pot_button' onclick='post_raise_pot()'>Pot</div>" +
                                       "<div class='button small_button all_in_button' onclick='post_raise_all()'>All</div>";
            }
            else if(data.decisions[i].type == 'all in'){
                decisions += "<div class='button " + (i == 2? "raise_button": "call_button") + "' onclick='post_set_decision(\"" + (i+1) + "\")'>All in " + 
                                                                            shortcut_number_for_decision(data.decisions[i].money) + "</div>";
            }

        }

        post_inner_html([{id: 'decisions', str: decisions}]);

        setTimeout(handle, 10);

    }

}

function socket_open(){


    if((''+player_name) != ''){

        socket.send('js ' + player_name);

    } else if ((''+table_to_spectate) != ''){

        spectate_mode = true;

        post_inner_html([{id: 'sit_on', str: 'watch '}]);
        post_inner_html([{id: 'you_are_on', str: ''}]);
        post_inner_html([{id: 'your_cards', str: ''}]);

        socket.send('sp ' + table_to_spectate);
        socket.send(JSON.stringify({type: 'nick', nick: nick}));

    } else if((''+replay_id) != '') {

        replay_mode = true;

        post_inner_html([{id: 'sit_on', str: 'watch replay of '}]);
        post_inner_html([{id: 'you_are_on', str: ''}]);
        post_inner_html([{id: 'your_cards', str: ''}]);

        post_class_rem([{id: 'replay_control', class: 'hidden'}]);
        post_bigger_chat();

        socket.send('rp ' + replay_id);

    }

}

function socket_close(event){

    if(socket.stay){

        clear_table();

        socket = undefined;
        seats = undefined;
        wait_for_initialize = true;

        post_inner_html([{id: 'players', str: ''}]);

        player_name = '';
        table_to_spectate = table_number;
        
        start();

    } else {

        if (event.wasClean || socket.clean) {
            //alert('Соединение закрыто чисто');
        } else {
            post_alert('Обрыв соединения');
        }
        //alert('Код: ' + event.code + ' причина: ' + event.reason);

        post_location(back_addr);

    }

}

function socket_message(event) {

    console.log(event.data);
    queue.push(JSON.parse(event.data));

}

function start(){

    if(socket === undefined){
        socket = new WebSocket('ws://' + ip + ':' + port);

        socket.clean = false;
        socket.stay = false;

        socket.onopen = socket_open;
        socket.onclose = socket_close;
        socket.onmessage = socket_message;

        setTimeout(handle, 10);
    }
}
