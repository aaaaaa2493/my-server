class Handler{
    constructor(socket){
        this.in_loop = false;
        this.reconnect_mode = false;
        this.wait_for_init = true;
        this.game_mode = false;
        this.queue = [];
        this.socket = socket;
        this.seats = undefined;
        this.info = new InfoCreator();
        this.tabs = new TabController();

        this.system_handle = {
            'broken': d => this.broken(d),
            'finish': d => this.finish(d),
            'info': d => this.info_message(d),
            'reconnect start': d => this.reconnect_start(d),
            'reconnect end': d => this.reconnect_end(d),
        };

        this.game_handle = {
            'init hand': d => this.init_hand(d),
            'ante': d => this.ante(d),
            'collect money': d => this.collect_money(d),
            'blinds': d => this.blinds(d),
            'blinds increased': d => this.blinds_increased(d),
            'give cards': d => this.give_cards(d),
            'deal cards': d => this.deal_cards(d),
            'delete player': d => this.delete_player(d),
            'add player': d => this.add_player(d),
            'resit': d => this.resit(d),
            'switch decision': d => this.switch_decision(d),
            'made decision': d => this.made_decision(d),
            'excess money': d => this.excess_money(d),
            'flop': d => this.flop(d),
            'turn': d => this.turn(d),
            'river': d => this.river(d),
            'open cards': d => this.open_cards(d),
            'give money': d => this.give_money(d),
            'money results': d => this.money_results(d),
            'hand results': d => this.hand_results(d),
            'busted': d => this.busted(d),
            'clear': d => this.clear(d),
            'win': d => this.win(d),
            'place': d => this.place(d),
            'chat': d => this.chat(d),
            'disconnected': d => this.disconnected(d),
            'connected': d => this.connected(d),
            'kick': d => this.kick(d),
            'back counting': d => this.back_counting(d),
            'set decision': d => this.set_decision(d),
        };
    }

    async handle(){
        this.in_loop = true;

        while(this.in_loop) {

            if(!this.reconnect_mode){
                await this.sleep(10);
            }

            if(this.queue.length === 0){
                continue;
            }

            let data = this.queue.shift();

            if(data.type in this.system_handle){
                this.system_handle[data.type](data);
            }

            if(!this.reconnect_mode && this.wait_for_init && data.type !== 'init hand'){
                continue;
            }

            console.log(data);

            if(data.type in this.game_handle){
                this.game_handle[data.type](data);
            }
        }
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    can_move_chips(){
        return !this.reconnect_mode;
    }

    chat_message(key, text){
        if(key === 13 && text.length > 0){ // enter key is 13
            worker.change_value('message', '');
            worker.socket.send(JSON.stringify({type: 'chat', text: text}));
        }
    }

    broken(){
        this.socket.close();
        this.in_loop = false;
    }

    finish(data){
        this.socket.clean = true;
        this.info.finish(data.msg);
        this.in_loop = false;
    }

    info_message(data){
        this.info.basic(data.msg);
    }

    reconnect_start(){
        this.reconnect_mode = true;
    }

    reconnect_end(){
        this.reconnect_mode = false;
    }

    init_hand(data){
        let all_inner_html = [];

        if(this.wait_for_init){

            this.wait_for_init = false;

            worker.class_rem([
                {id: 'general_info', class: 'hidden'},
                {id: 'tournament_info_button', class: 'hidden'},
                {id: 'last_hand_info_button', class: 'hidden'},
                {id: 'table_num', class: 'hidden'},
                {id: 'hand_num_short_info', class: 'hidden'},
                {id: 'place_short_info', class: 'hidden'},
                {id: 'chat', class: 'hidden'},
                {id: 'big_blind', class: 'hidden'},
                {id: 'small_blind', class: 'hidden'},
                {id: 'ante', class: 'hidden'}
            ]);

        }

        let table_number = shortcut_number_for_player(data.table_number);

        if(data.is_final){
            all_inner_html.push({id: 'table_num_info', str: 'final table'});
            all_inner_html.push({id: 'table_num', str: 'Final table'});
        }
        else{
            all_inner_html.push({id: 'table_num_info', str: 'table #' + table_number});
            all_inner_html.push({id: 'table_num', str: 'Table #' + table_number});
        }

        let hand_number = shortcut_number_for_player(data.hand_number);
        let ante = shortcut_number_for_decision(data.ante);
        let sb = shortcut_number_for_decision(data.sb);
        let bb = shortcut_number_for_decision(data.bb);
        let avg_stack = shortcut_number_for_player(data.avg_stack);
        let players_left = shortcut_number_for_player(data.players_left);

        all_inner_html.push({id: 'hand_num_info', str: hand_number});
        all_inner_html.push({id: 'hand_num', str: hand_number});
        all_inner_html.push({id: 'ante_info', str: ante});
        all_inner_html.push({id: 'ante_shortcut', str: ante});
        all_inner_html.push({id: 'sb_info', str: sb});
        all_inner_html.push({id: 'small_blind_shortcut', str: sb});
        all_inner_html.push({id: 'bb_info', str: bb});
        all_inner_html.push({id: 'big_blind_shortcut', str: bb});
        all_inner_html.push({id: 'average_stack_info', str: avg_stack});
        all_inner_html.push({id: 'players_left_info', str: players_left});



        this.seats = new Seats(data, this.game_mode);

        let top9_info = '';

        for(let i = 0; i < data.top_9.length; i++){

            top9_info += `<tr>
                            <td>${i+1}</td>
                            <td>${shortcut_number_for_player(data.top_9[i].stack)}</td>
                            <td>${data.top_9[i].name}</td>
                          </tr>`;

        }

        all_inner_html.push({id: 'top_players_info', str: top9_info});

        worker.inner_html(all_inner_html);
    }

    ante(data){
        let paid = data.paid;

        for(let i = 0; i < paid.length; i++){

            this.seats.set_bet(paid[i].id, paid[i].paid, 'Ante');

        }

        worker.play_sound('chips');
    }

    collect_money(){

        let move_ids = [];

        for(let seat of this.seats.all()){

            if(seat.chipstack.money > 0){

                this.seats.main_stack.money += seat.chipstack.money;
                seat.stack -= seat.chipstack.money;

                move_ids.push(seat.chipstack.id);

                if(!this.can_move_chips()){
                    worker.socket.handler.seats.set_bet(seat.id, 0);
                }

            }

        }


        if(move_ids.length > 0){

            if(!this.can_move_chips()){
                this.seats.set_bet(-1, this.seats.main_stack.money);
            }
            else{
                this.seats.chipstack_timeout = setTimeout(() => this.seats.clear_bets(), 500);
                worker.chips_to_main(move_ids);
            }

        }

        this.seats.clear_decision_states();

        worker.play_sound('collect');
    }

    blinds(data){
        let button_id = data.button;

        worker.dealer_pos(this.seats.id_to_local_seat[button_id]);

        if(data.info.length === 1){
            this.seats.set_bet(data.info[0].id, data.info[0].paid, 'BB');
        }
        else{
            this.seats.set_bet(data.info[0].id, data.info[0].paid, 'SB');
            this.seats.set_bet(data.info[1].id, data.info[1].paid, 'BB');
        }

        worker.play_sound('chips');
    }

    blinds_increased(data){

        let text_bb = shortcut_number_for_decision(data.bb);
        let text_sb = shortcut_number_for_decision(data.sb);
        let text_ante = shortcut_number_for_decision(data.ante);

        this.info.blinds_increasing(text_bb, text_sb, text_ante);

        worker.inner_html([
            {id: 'big_blind_shortcut', str: text_bb},
            {id: 'small_blind_shortcut', str: text_sb},
            {id: 'ante_shortcut', str: text_ante}
        ]);
    }

    give_cards(){
        console.log('Handler.give_cards()');
    }

    deal_cards(){
        let up_src = get_src('UP');

        let all_src = [];

        for(let seat of this.seats.all()){
            all_src.push({id: seat.card1, src: up_src});
            all_src.push({id: seat.card2, src: up_src});
        }

        worker.src(all_src);
    }

    delete_player(data){
        this.seats.delete_player(data.id);
    }

    add_player(data){
        this.seats.add_player(data);
    }

    resit(){
        console.log('Handler.resit()');
    }

    switch_decision(data){
        worker.thinking_pos(this.seats.id_to_local_seat[data.id]);
        this.seats.id_in_decision = data.id;
    }

    made_decision(data){

        let seat = this.seats.get_by_id(this.seats.id_in_decision);

        switch (data.result){
        case 'fold':
            worker.src_hide(seat.card1, seat.card2);
            this.seats.update_info(this.seats.id_in_decision, 'Fold');
            worker.play_sound('fold');
            break;

        case 'check':
            this.seats.update_info(this.seats.id_in_decision, 'Check');
            worker.play_sound('check');
            break;

        case 'call':
            this.seats.set_bet(this.seats.id_in_decision, data.money, 'Call');
            worker.play_sound('chips');
            break;

        case 'raise':
            this.seats.set_bet(this.seats.id_in_decision, data.money, 'Raise');
            worker.play_sound('chips');
            break;

        case 'all in':
            this.seats.set_bet(this.seats.id_in_decision, data.money, 'All in');
            worker.play_sound('chips');
            break;

        default:
            break;
        }
    }

    excess_money(data){
        this.seats.set_bet(data.id, this.seats.get_by_id(data.id).chipstack.money - data.money);
    }

    flop(data){
        this.seats.clear_decision_states();
        this.seats.clear_decisions();

        worker.src([
            {id: 'flop1', src: get_src(data.card1)},
            {id: 'flop2', src: get_src(data.card2)},
            {id: 'flop3', src: get_src(data.card3)}
        ]);

        worker.play_sound('fold');
    }

    turn(data){
        this.seats.clear_decision_states();
        this.seats.clear_decisions();

        worker.src([{id: 'turn', src: get_src(data.card)}]);

        worker.play_sound('fold');
    }

    river(data){
        this.seats.clear_decision_states();
        this.seats.clear_decisions();

        worker.src([{id: 'river', src: get_src(data.card)}]);

        worker.play_sound('fold');
    }

    open_cards(data){
        this.seats.clear_decision_states();
        this.seats.clear_decisions();

        let all_src = [];

        for(let i = 0; i < data.cards.length; i++){

            let seat = this.seats.get_by_id(data.cards[i].id);

            all_src.push({id: seat.card1, src: get_src(data.cards[i].card1)});
            all_src.push({id: seat.card2, src: get_src(data.cards[i].card2)});

        }

        worker.src(all_src);
    }

    give_money(data){

        this.seats.clear_decision_states();

        let seat = this.seats.get_by_id(data.id);

        if(this.can_move_chips()){
            // Firstly change position of chipstack to main and only then set bet
            worker.class_add(seat.chipstack.id, 'main_chips');
        }

        seat.chipstack.money += data.money;
        this.seats.set_bet(data.id, data.money, 'Win');

        this.seats.main_stack.money -= data.money;
        this.seats.set_bet(-1, this.seats.main_stack.money, 'Win');

        if(this.can_move_chips()){
            worker.chips_from_main(seat.chipstack.id);
            worker.play_sound('grab');
        }

    }

    money_results(){
        console.log('Handler.money_results()');
    }

    hand_results(data){

        worker.src([
            {id: 'flop1_info', src: get_src(data.flop1)},
            {id: 'flop2_info', src: get_src(data.flop2)},
            {id: 'flop3_info', src: get_src(data.flop3)},
            {id: 'turn_info', src: get_src(data.turn)},
            {id: 'river_info', src: get_src(data.river)}
        ]);

        let table_fill = '';

        for(let i = 0; i < data.results.length; i++){

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

        worker.inner_html([{id: 'cards_reveal', str: table_fill}]);
    }

    busted(){
        console.log('Handler.busted()');
    }

    clear(){
        this.seats.clear();
    }

    win(){
        console.log('Handler.win()');
    }

    place(data){
        worker.inner_html([{
            id: 'place_info',
            str: data.place
        }]);
    }

    chat(data){
        worker.add_to_chat(data.text);
    }

    disconnected(data){
        let seat = this.seats.get_by_id(data.id);
        worker.set_disconnected(seat.html_id, 1);
        seat.disconnected = true;
    }

    connected(data){
        let seat = this.seats.get_by_id(data.id);
        worker.set_disconnected(seat.html_id, 0);
        seat.disconnected = false;
    }

    kick(){
        console.log('Handler.kick()');
    }

    back_counting(data){
        this.seats.update_info(data.id, data.time + ' sec');
    }

    set_decision(){
        console.log('Handler.set_decision()');
    }

}

class GameHandler extends Handler{
    constructor(name, socket){
        super(socket);
        this.name = name;
        this.game_mode = true;
        this.resit_mode = false;
        this.in_game = false;
        this.premoves = new Premoves();
        this.raises = new Raises(this);
    }

    open(){
        this.socket.send('js ' + this.name);
        this.info.wait_while_all_players_register();
    }

    set_premove(num_answer, is_checked){
        this.premoves.set(num_answer, is_checked);
    }

    send_decision(to_send){
        worker.inner_html([{id: 'decisions', str: ''}]);
        this.socket.send(JSON.stringify({type: 'decision', text: to_send}));
    }

    reconnect_end(){

        if(!this.resit_mode){
            this.info.success_reconnection();
        }
        this.resit_mode = false;

        super.reconnect_end();
    }

    init_hand(data){

        if(this.wait_for_init){
            this.info.started_game();
            worker.class_rem([{id: 'message', class: 'hidden'}]);
        }

        super.init_hand(data);

    }

    blinds(data){

        if(!this.resit_mode){
            this.in_game = true;

            let curr_bb;
            let curr_bb_id;

            if(data.info.length === 1){
                curr_bb = data.info[0].paid;
                curr_bb_id = data.info[0].id;
            }
            else{
                curr_bb = data.info[1].paid;
                curr_bb_id = data.info[1].id;
            }

            if(curr_bb_id === this.seats.my_id){
                if (curr_bb < this.seats.me.stack){
                    this.premoves.check_fold();
                }
                else{
                    // so I am in all-in and premoves should be hidden
                    this.premoves.hide();
                }

            }
            else{
                if (this.seats.bb < this.seats.me.all_money()){
                    this.premoves.call_fold(this.seats.bb - this.seats.me.chipstack.money);
                }
                else{
                    // big blind amount bigger than my stack so either fold or all-in
                    this.premoves.all_in_fold(this.seats.me.stack);
                }
            }
        }

        super.blinds(data);
    }

    give_cards(data){
        let up_card = get_src('UP');

        let src_list = [];

        for(let seat of this.seats.all()){
            if(seat.id === this.seats.my_id){
                src_list.push({id: seat.card1, src: get_src(data.first)});
                src_list.push({id: seat.card2, src: get_src(data.second)});
                seat.first_card = data.first;
                seat.second_card = data.second;
            }
            else{
                src_list.push({id: seat.card1, src: up_card});
                src_list.push({id: seat.card2, src: up_card});
            }
        }

        worker.src(src_list);
    }

    resit(data){
        this.resit_mode = true;

        this.info.resit(data.table_number, data.is_final);

        if(data.is_final){
            worker.inner_html([{id: 'table_num_info', str: 'final table'}]);
        }
        else{
            worker.inner_html([{id: 'table_num_info', str: 'table #' + data.table_number}]);
        }

        this.seats = new Seats(data, this.game_mode);
    }

    made_decision(data){

        if(this.seats.id_in_decision === this.seats.my_id){

            switch (data.result){
            case 'fold':
                this.in_game = false;
                this.premoves.hide();
                break;

            case 'check':
            case 'raise':
                this.premoves.reset();
                this.premoves.check_fold();
                break;

            case 'call':
                if(this.seats.me.all_money() === data.money){
                    this.premoves.hide();
                }
                else{
                    this.premoves.reset();
                    this.premoves.check_fold();
                }
                break;

            case 'all in':
                this.premoves.hide();
                break;

            default:
                break;
            }

            worker.inner_html([{id: 'decisions', str: ''}]);

        }
        else if(this.in_game){
            switch (data.result){
            case 'raise':
            case 'all in':

                if(this.premoves.second){
                    // fold stays at fold, 'call any' stays at 'call any' or moved to 'all in'
                    // only 'call' resets
                    this.premoves.reset();
                }

                if(this.seats.me.all_money() <= data.money){
                    this.premoves.all_in_fold(this.seats.me.stack);
                }
                else{
                    this.premoves.call_fold(data.money - this.seats.me.chipstack.money);
                }
                break;

            default:
                break;
            }
        }

        super.made_decision(data);
    }

    flop(data){
        this.premoves.reset();
        super.flop(data);
    }

    turn(data){
        this.premoves.reset();
        super.turn(data);
    }

    river(data){
        this.premoves.reset();
        super.river(data);
    }

    open_cards(data){
        this.premoves.hide();
        this.in_game = false;
        super.open_cards(data);
    }

    give_money(data){
        this.premoves.hide();
        super.give_money(data);
    }

    hand_results(data){
        worker.src([
            {id: 'your_first_info', src: get_src(this.seats.me.first_card)},
            {id: 'your_second_info', src: get_src(this.seats.me.second_card)}
        ]);

        super.hand_results(data);
    }

    busted(data){
        this.socket.clean = true;
        this.info.busted(data.place);
        this.in_loop = false;
    }

    win(){
        this.socket.clean = true;
        this.info.win();
        this.in_loop = false;
    }

    place(data){
        if(!this.reconnect_mode) {
            worker.inner_html([{
                id: 'place_short_info',
                str: data.place + ' / ' + this.seats.players_left
            }]);
        }
    }

    kick(){
        this.socket.clean = true;
        this.info.kick();
        worker.inner_html([{id: 'decisions', str: ''}]);
        this.in_loop = false;
    }

    set_decision(data){
        // if it in reconnect mode then player was autofolded
        if(this.reconnect_mode){
            return;
        }

        // all premoves checking flags stays in 'this.made_decision' method
        if(this.premoves.first){
            if(data.decisions[1].type === 'check'){
                this.send_decision('2'); // if 'check/fold' then autoclick 'check'
                // but 'check/fold' flag stays so if someone raises then autoclick 'fold'
                return;
            }
            else{
                // autoclick 'fold'
                this.send_decision('1');
                return;
            }
        }
        else if(this.premoves.second){
            // autoclick 'call'
            this.send_decision('2');
            return;
        }
        else if(this.premoves.third){
            // because third is 'call any' so autoclick 'call'
            this.send_decision('2');
            return;
        }

        this.premoves.hide();

        worker.play_sound('attention');

        let decisions = '';

        for(let i = 0; i < data.decisions.length; i++){

            if(data.decisions[i].type === 'fold'){
                decisions += `<div class='button fold_button' onclick='post_set_decision("${i+1}")'>Fold</div>`;
            }
            else if(data.decisions[i].type === 'check'){
                decisions += `<div class='button call_button' onclick='post_set_decision("${i+1}")'>Check</div>`;
            }
            else if(data.decisions[i].type === 'call'){
                let text_call = data.decisions[i].money - this.seats.me.chipstack.money;
                decisions += `<div class='button call_button' onclick='post_set_decision("${i+1}")'>
                    Call ${shortcut_number_for_decision(text_call)}</div>`;
                this.seats.to_call = data.decisions[i].money;
            }
            else if(data.decisions[i].type === 'raise'){
                decisions += `<div id=raise class='button raise_button' onclick=
                                'post_set_decision("${i+1} " + document.getElementById("range").value)'>
                                Raise ${shortcut_number_for_decision(data.decisions[i].from)}</div>`;

                decisions += `<input id=range type=range min=${data.decisions[i].from} max=${data.decisions[i].to} 
                                step=1 onmousemove='document.getElementById("raise").innerHTML = 
                                (this.value === this.max? "All in ": "Raise ") + shortcut(this.value)' 
                                onchange='document.getElementById("raise").innerHTML =
                                (this.value === this.max? "All in ": "Raise ") + shortcut(this.value)' 
                                value=${data.decisions[i].from}>`;

                decisions += `<input id=textraise type=text class=input_button placeholder='input amount' 
                                onkeyup='text_change(this.value)'>`;

                decisions += `<div class='button small_button minus_button' onclick='post_raise_minus()'>-</div>
                              <div class='button small_button plus_button' onclick='post_raise_plus()'>+</div>
                              <div class='button small_button pot_button' onclick='post_raise_pot()'>Pot</div>
                              <div class='button small_button all_in_button' onclick='post_raise_all()'>All</div>`;
            }
            else if(data.decisions[i].type === 'all in'){
                let text_all_in = data.decisions[i].money - this.seats.me.chipstack.money;
                decisions += `<div class='button ${i === 2? 'raise_button': 'call_button'}' 
                                onclick='post_set_decision("${i+1}")'>
                                All in ${shortcut_number_for_decision(text_all_in)}</div>`;
            }

        }
        worker.inner_html([{id: 'decisions', str: decisions}]);
    }

}

class SpectatorHandler extends Handler{
    constructor(table_and_nick, socket){
        super(socket);
        this.table_to_spectate = table_and_nick[0];
        this.nick = table_and_nick[1];
    }

    open(){
        worker.inner_html([{id: 'sit_on', str: 'watch '}]);
        worker.inner_html([{id: 'you_are_on', str: ''}]);
        worker.inner_html([{id: 'your_cards', str: ''}]);

        this.socket.send('sp ' + this.table_to_spectate);
        this.socket.send(JSON.stringify({type: 'nick', nick: this.nick}));
    }

    init_hand(data){

        if(this.wait_for_init){
            this.info.watching_table(data.table_number, data.is_final);
            worker.class_rem([{id: 'message', class: 'hidden'}]);
        }

        worker.inner_html([
            {id: 'place_short_info', str: shortcut_number_for_player(data.players_left)}
        ]);
        
        super.init_hand(data);

    }
}

class ReplayHandler extends Handler{
    constructor(id, socket){
        super(socket);
        this.replay_id = id;
        this.in_pause = false;
    }

    open(){
        worker.inner_html([{id: 'sit_on', str: 'watch replay of '}]);
        worker.inner_html([{id: 'you_are_on', str: ''}]);
        worker.inner_html([{id: 'your_cards', str: ''}]);

        worker.class_rem([{id: 'replay_control', class: 'hidden'}]);
        worker.bigger_chat();

        let js = {type: 'rp', name: this.replay_id};

        this.socket.send(JSON.stringify(js));
    }

    chat_message(){
        // Need to rewrite chat_message method for replay to do nothing
        console.log('Replay.chat_message()');
    }

    can_move_chips(){
        return !this.in_pause;
    }

    pause_play(){
        if(this.in_pause){

            this.in_pause = false;

            worker.class_add('replay_next_step', 'hidden');
            worker.inner_html([{id: 'replay_pause_play', str: 'Pause'}]);

            this.socket.send('play');

        }
        else{

            this.in_pause = true;

            worker.class_rem([{id: 'replay_next_step', class: 'hidden'}]);
            worker.inner_html([{id: 'replay_pause_play', str: 'Play'}]);

            this.socket.send('pause');

        }
    }

    next_step(){
        this.socket.send('next step');
    }

    prev_hand(){
        clearTimeout(this.seats.chipstack_timeout);
        this.seats.clear_bets();

        worker.inner_html([{id: 'chat', str: 'Chat:'}]);
        this.socket.send('prev hand');
    }

    next_hand(){
        clearTimeout(this.seats.chipstack_timeout);
        this.seats.clear_bets();

        worker.inner_html([{id: 'chat', str: 'Chat:'}]);
        this.socket.send('next hand');
    }

    init_hand(data){

        if(this.wait_for_init){
            this.info.watching_table(data.table_number, data.is_final);
        }

        worker.inner_html([
            {id: 'place_short_info', str: shortcut_number_for_player(data.players_left)}
        ]);

        super.init_hand(data);

    }
}

class Chipstack{
    constructor(local_seat, money){
        this.money = money;
        this.local_seat = local_seat;
        this.id = 'ch' + local_seat;
        this.ch11 = 'p' + local_seat + 'r1c1';
        this.ch12 = 'p' + local_seat + 'r1c2';
        this.ch13 = 'p' + local_seat + 'r1c3';
        this.ch14 = 'p' + local_seat + 'r1c4';
        this.ch21 = 'p' + local_seat + 'r2c1';
        this.ch22 = 'p' + local_seat + 'r2c2';
        this.ch23 = 'p' + local_seat + 'r2c3';
        this.ch24 = 'p' + local_seat + 'r2c4';

        let int_seat = parseInt(local_seat);

        this.order8 = this.get_order_8(int_seat);
        this.order7 = this.get_order_7(int_seat);
        this.order6 = this.get_order_6(int_seat);
        this.order5 = this.get_order_5(int_seat);
        this.order4 = this.get_order_4(int_seat);
        this.order3 = this.get_order_3(int_seat);
        this.order2 = this.get_order_2(int_seat);
        this.order1 = this.get_order_1(int_seat);
    }

    convert_order(order){
        let new_order = [];
        for(let one of order){
            new_order.push(one[0] + this.local_seat + one.substring(2));
        }
        return new_order;
    }

    get_empty(order){
        let empty_order = [];
        for(let curr of this.order8){
            if(!order.includes(curr)){
                empty_order.push(curr);
            }
        }
        return empty_order;
    }

    get_order(count){
        switch(count){
        case 1:
            return this.order1;
        case 2:
            return this.order2;
        case 3:
            return this.order3;
        case 4:
            return this.order4;
        case 5:
            return this.order5;
        case 6:
            return this.order6;
        case 7:
            return this.order7;
        case 8:
            return this.order8;
        default:
            return [];
        }
    }

    get_order_8(seat){
        switch(seat){
        case 0: case 1: case 6: case 7: case 8: case 9:
            return [this.ch21, this.ch22, this.ch23, this.ch24, this.ch11, this.ch12, this.ch13, this.ch14];
        case 2: case 3: case 4: case 5:
            return [this.ch24, this.ch23, this.ch22, this.ch21, this.ch14, this.ch13, this.ch12, this.ch11];
        default:
            return [];
        }
    }

    get_order_7(seat){
        switch(seat){
        case 0: case 1: case 6: case 7: case 8: case 9:
            return [this.ch22, this.ch23, this.ch24, this.ch11, this.ch12, this.ch13, this.ch14];
        case 2: case 3: case 4: case 5:
            return [this.ch23, this.ch22, this.ch21, this.ch14, this.ch13, this.ch12, this.ch11];
        default:
            return [];
        }
    }

    get_order_6(seat){
        switch(seat){
        case 0: case 1: case 6: case 7: case 8: case 9:
            return [this.ch23, this.ch24, this.ch11, this.ch12, this.ch13, this.ch14];
        case 2: case 3: case 4: case 5:
            return [this.ch22, this.ch21, this.ch14, this.ch13, this.ch12, this.ch11];
        default:
            return [];
        }
    }

    get_order_5(seat){
        switch(seat){
        case 0: case 1: case 6: case 7: case 8: case 9:
            return [this.ch24, this.ch11, this.ch12, this.ch13, this.ch14];
        case 2: case 3: case 4: case 5:
            return [this.ch21, this.ch14, this.ch13, this.ch12, this.ch11];
        default:
            return [];
        }
    }

    get_order_4(seat){
        switch(seat){
        case 0: case 1: case 6: case 7: case 8: case 9:
            return [this.ch11, this.ch12, this.ch13, this.ch14];
        case 2: case 3: case 4: case 5:
            return [this.ch14, this.ch13, this.ch12, this.ch11];
        default:
            return [];
        }
    }

    get_order_3(seat){
        switch(seat){
        case 0: case 1: case 6: case 7: case 8: case 9:
            return [this.ch12, this.ch13, this.ch14];
        case 2: case 3: case 4: case 5:
            return [this.ch13, this.ch12, this.ch11];
        default:
            return [];
        }
    }

    get_order_2(seat){
        switch(seat){
        case 0: case 1: case 6: case 7: case 8: case 9:
            return [this.ch13, this.ch14];
        case 2: case 3: case 4: case 5:
            return [this.ch12, this.ch11];
        default:
            return [];
        }
    }

    get_order_1(seat){
        switch(seat){
        case 0: case 1: case 6: case 7: case 8: case 9:
            return [this.ch14];
        case 2: case 3: case 4: case 5:
            return [this.ch11];
        default:
            return [];
        }
    }
}

class Player{
    constructor(data, local_seat){
        this.id = data.id;
        this.name = data.name;
        this.disconnected = data.disconnected;
        this.stack = data.stack;
        this.local_seat = local_seat;
        this.html_id = 'p' + local_seat;
        this.chipstack = new Chipstack(local_seat, 0);
        this.card1 = 'c' + local_seat + '1';
        this.card2 = 'c' + local_seat + '2';
    }

    all_money(){
        return this.stack + this.chipstack.money;
    }

    delete_cards(){
        worker.src([{id: this.card1, src: get_src('ZZ')}, {id: this.card2, src: get_src('ZZ')}]);
    }
}

class Seats{
    constructor(data, game_mode) {

        let inner_html = [];

        let seats_shift = 0;

        this.players_left = data.players_left;

        this.bb = data.bb;
        this.sb = data.sb;
        this.ante = data.ante;

        this.to_call = 0;

        let players = data.players;
        this.table_number = data.table_number;

        this.is_final = data.is_final;

        if (game_mode) {

            while (players[0].controlled === undefined || players[0].controlled === false) {
                players.push(players.shift());
                seats_shift++;
            }

            this.my_id = players[0].id;
        }

        this.places = this.get_places(data.seats);

        this.seats = new Map();
        this.id_to_local_seat = {};
        this.real_seat_to_local_seat = {};

        inner_html.push({id: 'players', str: ''});

        let doc_players = '';

        for (let i = 0; i < this.places.length; i++) {

            this.real_seat_to_local_seat[(seats_shift + i) % data.seats] = this.places[i];

            if (players[i].id !== null) {

                doc_players += `<div id=p${this.places[i]} 
                    data-empty=0 data-disconnected=${players[i].disconnected ? 1 : 0}>
                    ${players[i].name}<br>${shortcut_number_for_player(players[i].stack)}</div>`;

                let player = new Player(players[i], this.places[i]);

                this.seats.set(this.places[i], player);

                if (game_mode && player.id === this.my_id){
                    this.me = player;
                }

                this.id_to_local_seat[players[i].id] = this.places[i];

            }
            else {
                doc_players += `<div id=p${this.places[i]} data-empty=1><br>Empty seat</div>`;
            }
        }

        inner_html.push({id: 'players', str: doc_players});

        this.main_stack = new Chipstack('0', 0);

        worker.final_table(data.is_final? 1: 0);
        worker.inner_html(inner_html);

        this.chipstack_timeout = null;
    }

    get_places(seats){
        switch(seats){
        case 2:
            return [1, 6];
        case 3:
            return [1, 4, 7];
        case 4:
            return [1, 3, 6, 8];
        case 5:
            return [1, 3, 5, 6, 8];
        case 6:
            return [1, 2, 4, 6, 7, 9];
        case 7:
            return [1, 2, 4, 5, 6, 7, 9];
        case 8:
            return [1, 2, 3, 4, 6, 7, 8, 9];
        case 9:
            return [1, 2, 3, 4, 5, 6, 7, 8, 9];
        default:
            return [];
        }
    }

    add_player(data){
        let local_seat = this.real_seat_to_local_seat[data.seat];

        let player = new Player(data, local_seat);

        this.seats.set(local_seat, player);

        this.id_to_local_seat[data.id] = local_seat;
        worker.set_empty(player.html_id, 0);
        worker.set_disconnected(player.html_id, player.disconnected? 1: 0);

        if(this.is_final){
            this.update_info(data.id, '');
        }
        else{
            this.update_info(data.id, 'New player');
        }
    }

    delete_player(id){
        let seat = this.get_by_id(id);

        seat.delete_cards();

        this.set_empty_seat(seat.local_seat);
        
        this.seats.delete(seat.local_seat);
        this.id_to_local_seat[id] = undefined;
    }

    * all(){
        for(let [,seat] of this.seats){
            yield seat;
        }
    }

    get_by_id(id){
        return this.seats.get(this.id_to_local_seat[id]);
    }

    clear_decisions(){
        for(let seat of worker.socket.handler.seats.all()){
            this.update_info(seat.id, '');
        }
    }

    clear_decision_states(){
        worker.thinking_pos(0);
    }

    get available_chips(){
        return [
            [1000000000, '16'],
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
            [1, '1']
        ];
    }

    set_bet(id, count, reason=''){

        if(id !== -1){

            let seat = this.get_by_id(id);
            let money_spent;

            if(reason === 'Win'){
                money_spent = count;
                seat.stack += money_spent;
            }
            else if(reason !== 'Clear'){
                money_spent = count - seat.chipstack.money;
                seat.stack -= money_spent;
            }

            seat.chipstack.money = count;

            if(reason !== 'Clear'){
                this.update_info(id, reason, money_spent);
            }

        }

        let pot_count = this.main_stack.money;

        if(reason !== 'Win'){
            for(let seat of this.all()){
                pot_count += seat.chipstack.money;
            }
        }
        else if(id !== -1){
            pot_count -= count;
        }

        if(reason !== 'Clear'){
            worker.inner_html([
                {id: 'pot_count', str: shortcut_number_for_player(pot_count)}
            ]);
        }

        let amounts = [];

        for(let chip of this.available_chips){
            if(count >= chip[0]){
                let int_amount = Math.floor(count / chip[0]);
                amounts.push([chip[1], int_amount]);
                count -= int_amount * chip[0];
            }
        }

        while(amounts.length > 8){

            let min_betweens = -1;
            let index_betweens = -1;

            for(let i = 0; i < amounts.length - 1; i++){

                let curr_between = 0;

                for(let j = 1; j < amounts[i].length; j += 2){
                    curr_between += amounts[i][j];
                }

                for(let j = 1; j < amounts[i+1].length; j += 2){
                    curr_between += amounts[i+1][j];
                }

                if(curr_between <= min_betweens || min_betweens === -1){
                    min_betweens = curr_between;
                    index_betweens = i;
                }

            }

            for(let i = 0; i < amounts[index_betweens + 1].length; i++){
                amounts[index_betweens].push(amounts[index_betweens + 1][i]);
            }

            amounts.splice(index_betweens + 1, 1);
        }

        let chipstack_to_set_bet;

        if(id === -1){
            chipstack_to_set_bet = this.main_stack;
        }
        else{
            chipstack_to_set_bet = this.get_by_id(id).chipstack;
        }

        let chip_order;

        if(reason === 'Win'){
            let main_order = this.main_stack.get_order(amounts.length);
            chip_order = chipstack_to_set_bet.convert_order(main_order);
        }
        else{
            chip_order = chipstack_to_set_bet.get_order(amounts.length);
        }

        let all_chips = [];

        for(let empty of chipstack_to_set_bet.get_empty(chip_order)){
            all_chips.push({id: empty, str: ''});
        }

        for(let i = 0; i < amounts.length; i++){
            let curr_chips = chip_order[i];
            let curr_height = 0;
            let total_height_str = '';

            for(let j = 1; j < amounts[i].length; j += 2){

                for(let k = 0; k < amounts[i][j]; k++){

                    total_height_str += '<img class=chip src="/img/poker/chips/' + amounts[i][j-1] + '.png" style="margin-top: -' + curr_height + 'px">';
                    curr_height += 5;

                }

            }

            all_chips.push({id: curr_chips, str: total_height_str});

        }

        worker.inner_html(all_chips);

    }

    clear_bets(){
        this.chipstack_timeout = null;
        let chipstack_ids = [];
        for(let seat of this.all()){
            if(seat.chipstack.money > 0){
                chipstack_ids.push(seat.chipstack.id);
                this.set_bet(seat.id, 0);
            }
        }
        this.set_bet(-1, this.main_stack.money);
        worker.clear_chips(chipstack_ids);
    }

    clear(){
        let zz_src = get_src('ZZ');

        let all_src = [
            {id: 'flop1', src: zz_src},
            {id: 'flop2', src: zz_src},
            {id: 'flop3', src: zz_src},
            {id: 'turn', src: zz_src},
            {id: 'river', src: zz_src}
        ];

        this.clear_decision_states();

        for(let seat of this.all()){

            all_src.push({id: seat.card1, src: zz_src});
            all_src.push({id: seat.card2, src: zz_src});

            this.set_bet(seat.id, 0, 'Clear');

        }

        this.set_bet(-1, 0);

        worker.src(all_src);
    }

    set_empty_seat(local_seat){
        let player = this.seats.get(local_seat);

        worker.set_empty(player.html_id, 1);
        if(player.disconnected){
            worker.set_disconnected(player.html_id, 0);
        }

        worker.inner_html([{id: player.html_id, str: '<br>Empty seat'}]);
    }

    update_info(id, reason, count=0){
        if(reason !== '' && count > 0){
            reason = reason + ' ' + shortcut_number_for_decision(count);
        }

        let seat = worker.socket.handler.seats.get_by_id(id);
        worker.inner_html([
            {
                id: seat.html_id,
                str: seat.name + '<br>' + shortcut_number_for_player(seat.stack) + '<br>' + reason
            }
        ]);
    }
}

class Raises{
    constructor(handler){
        this.handler = handler;
    }

    raise(value, is_max){
        worker.change_value('range', value);
        let text_value = shortcut_number_for_decision(value);
        let action = is_max ? 'All in' : 'Raise';
        worker.inner_html([
            {id: 'raise', str: `${action} ${text_value}`}
        ]);
    }

    minus(value, max_value, min_value){
        let new_value = (+value) - (+min_value) > min_value ? (+value) - (+min_value) : min_value;
        this.raise(new_value, new_value === max_value);
    }

    plus(value, max_value, min_value){
        let new_value = (+value) + (+min_value) < max_value? (+value) + (+min_value) : max_value;
        this.raise(new_value, new_value === max_value);
    }

    all(max_value){
        this.raise(max_value, true);
    }

    pot(max_value){
        let in_pot = this.handler.seats.main_stack.money;

        for(let seat of this.handler.seats.all()){
            in_pot += seat.chipstack.money;
        }

        let raise_amount = in_pot + 2 * this.handler.seats.to_call;

        if(raise_amount > max_value){
            raise_amount = max_value;
        }

        this.raise(raise_amount, raise_amount === max_value);
    }
}

class Premoves{
    constructor(){
        this.first = false;
        this.second = false;
        this.third = false;
        this.is_visible = false;
        this.in_two_choices = false;
    }

    hide(){
        if(this.is_visible){
            this.is_visible = false;
            this.reset();
            worker.class_add('premoves', 'hidden');
        }
    }

    show(){
        if(!this.is_visible){
            this.is_visible = true;
            this.reset();
            worker.class_rem([{id: 'premoves', class: 'hidden'}]);
        }
    }

    check_fold(){
        this.show();
        worker.inner_html([
            {id: 'textpremove1', str: 'Check/Fold'},
            {id: 'textpremove2', str: 'Check'},
            {id: 'textpremove3', str: 'Call any'}
        ]);
    }

    call_fold(money){
        this.show();
        worker.inner_html([
            {id: 'textpremove1', str: 'Fold'},
            {id: 'textpremove2', str: 'Call ' + shortcut_number_for_decision(money)},
            {id: 'textpremove3', str: 'Call any'}
        ]);
    }

    all_in_fold(money){
        this.show();
        this.two_choices_mode();
        worker.inner_html([
            {id: 'textpremove1', str: 'Fold'},
            {id: 'textpremove2', str: 'Call ' + shortcut_number_for_decision(money)},
            {id: 'textpremove3', str: ''}
        ]);
    }

    two_choices_mode(){
        if(!this.in_two_choices){
            this.in_two_choices = true;
            if(this.third){
                // so 'call any' stays at 'all in'
                this.set('2', true);
            }
            else if(this.second){
                // so 'call' deletes
                this.set('2', false);
            }
            worker.class_add('premove3', 'hidden');
        }
    }

    three_choices_mode(){
        if(this.in_two_choices){
            this.in_two_choices = false;
            worker.class_rem([{id: 'premove3', class: 'hidden'}]);
        }
    }

    reset(){
        this.three_choices_mode();
        this.set(undefined, false);
    }

    set(answer, checked){

        let all_premoves = [
            {id: 'premove1', checked: false},
            {id: 'premove2', checked: false},
            {id: 'premove3', checked: false}
        ];

        this.first = false;
        this.second = false;
        this.third = false;

        if(checked){

            if(answer === '1'){
                all_premoves.push({id: 'premove1', checked: true});
                this.first = true;
            }
            else if(answer === '2'){
                all_premoves.push({id: 'premove2', checked: true});
                this.second = true;
            }
            else if(answer === '3'){
                all_premoves.push({id: 'premove3', checked: true});
                this.third = true;
            }

        }
        worker.set_premove(all_premoves);
    }

}

class InfoCreator{

    basic(info, append=[['Ok', '']]){

        for(let i = 0; i < append.length; i++){
            info += `<div class='button in_general g${i}' 
                onclick='document.getElementById("general_info").classList.add("hidden");
                ${append[i][1]}'>${append[i][0]}</div>`;
        }

        worker.inner_html([{id: 'general_info', str: info}]);
        worker.class_rem([{id: 'general_info', class: 'hidden'}]);
    }

    started_game(){
        this.basic('Game started. Good luck!');
    }

    watching_table(table_number, is_final){
        if(is_final){
            this.basic('You are watching final table');
        }
        else{
            this.basic('You are watching table #' + table_number);
        }
    }

    blinds_increasing(text_bb, text_sb, text_ante){

        let info = `Blinds now ${text_sb} / ${text_bb}`;

        if(text_ante !== '0'){
            info += ` ante ${text_ante}`;
        }

        this.basic(info);
    }

    resit(table_num, is_final){
        if (is_final){
            this.basic('You was resit on final table.');
        }
        else{
            this.basic('You was resit on table # ' + table_num);
        }
    }

    busted(place){
        let info = `You are busted! You finished ${place}.`;
        this.basic(info, [
            ['Watch', 'post_socket_stay()'],
            ['Quit', 'post_socket_close()']
        ]);
    }

    win(){
        let info = 'Congratulations! You are winner!';
        this.basic(info, [
            ['Ok', 'post_socket_close()']
        ]);
    }

    kick(){
        let info = 'You was kicked. You have 20 seconds to think now.';
        this.basic(info, [
            ['Refresh', 'window.location=window.location']
        ]);
    }

    finish(msg){
        this.basic(msg, [
            ['Ok', 'post_socket_close()']
        ]);
    }

    success_reconnection(){
        this.basic('Reconnection was successful.');
    }

    wait_while_all_players_register(){
        this.basic('Wait while all players register.');
    }

}

class TabController{
    constructor(){
        this.empty = new EmptyTab(this, 'tabs');
        this.info = new InfoTab(this, 'tournament_info');
        this.last_hand = new LastHandTab(this, 'last_hand_info');

        this.current = this.empty;
        this.is_visible = false;

        this.find_tab = {
            'empty': this.empty,
            'info': this.info,
            'last hand': this.last_hand
        };
    }

    hide(){
        if(this.is_visible){
            this.is_visible = false;
            worker.class_add('tabs', 'hidden');
        }
    }

    show(){
        if(!this.is_visible){
            this.is_visible = true;
            worker.class_rem([{id: 'tabs', class: 'hidden'}]);
        }
    }

    open(tab){
        let new_tab = this.find_tab[tab];

        if(new_tab === this.current){
            this.hide();
            this.current.deactivate();
            this.current = this.empty;
        }
        else if(new_tab){
            this.current.deactivate();
            this.current = new_tab;
            this.current.activate();
        }
    }

    message(message){
        this.current.message(JSON.parse(message));
    }
}

class BaseTab{
    constructor(controller, id_tab_element){
        this.tabs = controller;
        this.id = id_tab_element;
    }

    activate(){
        worker.class_rem([{id: this.id, class: 'hidden'}]);
    }

    deactivate(){
        worker.class_add(this.id, 'hidden');
    }

    message(){
        console.log('BaseTab.message()');
    }
}

class EmptyTab extends BaseTab{

    activate(){
        this.tabs.hide();
    }

    deactivate(){
        this.tabs.show();
    }

    message(){
        super.message();
    }
}

class InfoTab extends BaseTab{
    message(){
        console.log('InfoTab.message()');
    }
}

class LastHandTab extends BaseTab{
    message(){
        console.log('LastHandTab.message()');
    }
}

class Socket{
    constructor(ip, port, back_addr){
        this.ip = ip;
        this.port = port;
        this.back_addr = back_addr;
    }

    create_connection(name_entity, class_entity){

        this.clean = false;
        this.stay = false;

        this.handler = new class_entity(name_entity, this);

        this.socket = new WebSocket(`ws://${this.ip}:${this.port}`);

        this.socket.onopen = () => this.handler.open();
        this.socket.onclose = e => this.close(e);
        this.socket.onmessage = e => this.message(e);

        this.handler.handle();
    }

    close(event){
        if(this.stay){
            this.handler.seats.clear();

            this.socket = undefined;
            this.handler.loop = false;

            this.create_connection([this.handler.seats.table_number, this.handler.name], SpectatorHandler);

        } else {

            if (event.wasClean || this.clean) {
                console.log('Соединение закрыто чисто');
            } else {
                worker.alert('Обрыв соединения');
            }
            //alert('Код: ' + event.code + ' причина: ' + event.reason);

            worker.location(this.back_addr);

        }
    }

    message(event){
        console.log(event.data);
        this.handler.queue.push(JSON.parse(event.data));
    }

    send(message){
        console.log('WebSocket send ' + message);
        this.socket.send(message);
    }
}

class WorkerConnection{
    constructor(){
        console.log('Worker initialized');
    }

    message(event){
        console.log('in worker: ', event.data);

        let data = event.data;

        switch(data.type){
        case 'start':
            this.socket = new Socket(data.ip, data.port, data.back_addr);
            if(data.player_name !== ''){
                this.socket.create_connection(data.player_name, GameHandler);
            }
            else if(data.table_to_spectate !== ''){
                this.socket.create_connection([data.table_to_spectate, data.nick], SpectatorHandler);
            }
            else if(data.replay_id !== ''){
                this.socket.create_connection(data.replay_id, ReplayHandler);
            }
            break;

        case 'raise minus':
            this.socket.handler.raises.minus(data.value, data.max_value, data.min_value);
            break;

        case 'raise plus':
            this.socket.handler.raises.plus(data.value, data.max_value, data.min_value);
            break;

        case 'raise all':
            this.socket.handler.raises.all(data.max_value);
            break;

        case 'raise pot':
            this.socket.handler.raises.pot(data.max_value);
            break;

        case 'socket close':
            this.socket.socket.close();
            break;

        case 'socket stay':
            this.socket.stay = true;
            this.socket.socket.close();
            break;

        case 'socket clean':
            this.socket.clean = true;
            this.socket.socket.close();
            break;

        case 'set decision':
            this.socket.handler.send_decision(data.value);
            break;

        case 'pause play':
            this.socket.handler.pause_play();
            break;

        case 'next step':
            this.socket.handler.next_step();
            break;

        case 'prev hand':
            this.socket.handler.prev_hand();
            break;

        case 'next hand':
            this.socket.handler.next_hand();
            break;

        case 'chat message':
            this.socket.handler.chat_message(data.key, data.text);
            break;

        case 'premove':
            this.socket.handler.set_premove(data.answer, data.checked);
            break;

        case 'open tab':
            this.socket.handler.tabs.open(data.name);
            break;

        default:
            console.log(`Worker: bad type ${data.type}`);
            break;
        }
    }

    send(obj){
        postMessage(obj);
    }

    inner_html(obj){
        this.send({type: 'inner html', obj: obj});
    }

    change_value(id, value){
        this.send({type: 'change value', id: id, value: value});
    }

    class_add(id, cls){
        this.send({type: 'class add', id: id, class: cls});
    }

    class_rem(obj){
        this.send({type: 'class rem', obj: obj});
    }

    src(obj){
        this.send({type: 'src', obj: obj});
    }

    src_hide(id1, id2){
        this.send({type: 'src hide', id1: id1, id2: id2});
    }

    alert(msg){
        this.send({type: 'alert', msg: msg});
    }

    location(location){
        this.send({type: 'location', to: location});
    }

    play_sound(file){
        if(this.socket.handler.can_move_chips()){
            this.send({type: 'sound', file: get_sound(file)});
        }
    }

    add_to_chat(text){
        this.send({type: 'add to chat', text: text});
    }

    bigger_chat(){
        this.send({type: 'bigger chat'});
    }

    set_premove(obj){
        this.send({type: 'premove', obj: obj});
    }

    dealer_pos(pos){
        this.send({type: 'dealer pos', pos: pos});
    }

    chips_to_main(ids){
        this.send({type: 'chips to main', ids: ids});
    }

    chips_from_main(id){
        this.send({type: 'chips from main', id: id});
    }

    clear_chips(ids){
        this.send({type: 'clear chips', ids: ids});
    }

    thinking_pos(pos){
        this.send({type: 'thinking pos', pos: pos});
    }

    final_table(is_final){
        this.send({type: 'final table', is_final: is_final});
    }

    set_empty(id, is_empty){
        this.send({type: 'set empty', id: id, is_empty: is_empty});
    }

    set_disconnected(id, is_disconnected){
        this.send({type: 'set disconnected', id: id, is_disconnected: is_disconnected});
    }

}

function get_src(card){
    return '/img/poker/cards/' + card + '.png';
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
        return num.substring(0, num.length - 9) + '&thinsp;' +
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

function get_sound(file){

    if(file === 'chips'){
        let type_sound = Math.floor(Math.random()*5);

        return '/music/poker/chips/chip' + (type_sound+1) + '.mp3';
    }
    else if(file === 'fold'){
        return '/music/poker/cards/fold.mp3';
    }
    else if(file === 'check'){
        return '/music/poker/cards/check.mp3';
    }
    else if(file === 'attention'){
        return '/music/poker/attention/alert.mp3';
    }
    else if(file === 'collect'){
        return '/music/poker/chips/collect.mp3';
    }
    else if(file === 'grab'){
        return '/music/poker/chips/grab.mp3';
    }
    return 'sound file not found';
}

let worker = new WorkerConnection();

onmessage = e => worker.message(e);
