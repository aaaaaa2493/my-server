class Handler{
    constructor(socket){
        this.in_loop = false;
        this.reconnect_mode = false;
        this.wait_for_init = true;
        this.spectate_mode = false;
        this.replay_mode = false;
        this.game_mode = false;
        this.in_game = false;
        this.resit_mode = false;
        this.queue = [];
        this.socket = socket;
        this.seats = undefined;
    }

    async handle(){
        this.in_loop = true;

        while(this.in_loop) {

            if(!this.reconnect_mode){
                await sleep(100);
            }

            if(this.queue.length === 0){
                continue;
            }

            let data = this.queue.shift();

            if(data.type === 'broken'){
                this.socket.close();
                return;
            }

            if(data.type === 'finish'){

                this.socket.clean = true;

                let to_general_info = data.msg;
                to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");' +
                                   'post_socket_close();\'>Ok</div>';

                worker.inner_html([{id: 'general_info', str: to_general_info}]);
                worker.class_rem([{id: 'general_info', class: 'hidden'}]);

                return;
            }

            if(data.type === 'info'){

                let to_general_info = data.msg;
                to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");\'>Ok</div>';

                worker.inner_html([{id: 'general_info', str: to_general_info}]);
                worker.class_rem([{id: 'general_info', class: 'hidden'}]);

                continue;
            }

            if(data.type === 'reconnect start'){
                this.reconnect_mode = true;
                continue;
            }

            if(data.type === 'reconnect end'){
                this.reconnect_mode = false;

                if(!this.spectate_mode && !this.resit_mode && !this.replay_mode){

                    let to_general_info = 'Reconnection was successful.';
                    to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");\'>Ok</div>';

                    worker.inner_html([{id: 'general_info', str: to_general_info}]);
                    worker.class_rem([{id: 'general_info', class: 'hidden'}]);

                }

                this.resit_mode = false;

                continue;
            }

            if(!this.reconnect_mode && this.wait_for_init && data.type !== 'init hand'){
                continue;
            }

            console.log(data);

            switch(data.type){
            case 'init hand':
                this.init_hand(data);
                break;

            case 'ante':
                this.ante(data);
                break;

            case 'collect money':
                this.collect_money();
                break;

            case 'blinds':
                this.blinds(data);
                break;

            case 'blinds increased':
                this.blinds_increased(data);
                break;

            case 'give cards':
                this.give_cards(data);
                break;

            case 'deal cards':
                this.deal_cards(data);
                break;

            case 'delete player':
                this.delete_player(data);
                break;

            case 'add player':
                this.add_player(data);
                break;

            case 'resit':
                this.resit(data);
                break;

            case 'switch decision':
                this.switch_decision(data);
                break;

            case 'made decision':
                this.made_decision(data);
                break;

            case 'excess money':
                this.excess_money(data);
                break;

            case 'flop':
                this.flop(data);
                break;

            case 'turn':
                this.turn(data);
                break;

            case 'river':
                this.river(data);
                break;

            case 'open cards':
                this.open_cards(data);
                break;

            case 'give money':
                this.give_money(data);
                break;

            case 'money results':
                this.money_results(data);
                break;

            case 'hand results':
                this.hand_results(data);
                break;

            case 'busted':
                this.busted(data);
                break;

            case 'clear':
                this.clear();
                break;

            case 'win':
                this.win();
                break;

            case 'place':
                this.place(data);
                break;

            case 'chat':
                this.chat(data);
                break;

            case 'disconnected':
                this.disconnected(data);
                break;

            case 'connected':
                this.connected(data);
                break;

            case 'kick':
                this.kick();
                break;

            case 'back counting':
                this.back_counting(data);
                break;

            case 'set decision':
                this.set_decision(data);
                break;

            default:
                break;
            }

        }
    }

    init_hand(data){
        let all_inner_html = [];

        if(this.wait_for_init){

            this.wait_for_init = false;

            let to_general_info;

            if(this.game_mode){
                to_general_info = 'Game started. Good luck!';
            }
            else{

                if(data.is_final){
                    to_general_info = 'You are watching table #' + data.table_number;
                }
                else{
                    to_general_info = 'You are watching final table';
                }

            }

            to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");\'>Ok</div>';

            all_inner_html.push({id: 'general_info', str: to_general_info});

            worker.class_rem([{id: 'general_info', class: 'hidden'}, {id: 'tournament_info_button', class: 'hidden'},
                {id: 'last_hand_info_button', class: 'hidden'}, {id: 'table_num', class: 'hidden'},
                {id: 'hand_num_short_info', class: 'hidden'}, {id: 'place_short_info', class: 'hidden'}, {id: 'chat', class: 'hidden'},
                {id: 'big_blind', class: 'hidden'}, {id: 'small_blind', class: 'hidden'}, {id: 'ante', class: 'hidden'}]);

            if(!this.replay_mode){
                worker.class_rem([{id: 'message', class: 'hidden'}]);
            }

        }


        if(data.is_final){
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

        worker.remove_style([
            {id: 'ch0'}, {id: 'ch1'},
            {id: 'ch2'}, {id: 'ch3'},
            {id: 'ch4'}, {id: 'ch5'},
            {id: 'ch6'}, {id: 'ch7'},
            {id: 'ch8'}, {id: 'ch9'}
        ]);

        if(this.replay_mode || this.spectate_mode){
            all_inner_html.push({id: 'place_short_info', str: shortcut_number_for_player(data.players_left)});
        }

        this.seats = new Seats(data, this.game_mode);

        let top9_info = '';

        for(let i = 0; i < data.top_9.length; i++){

            top9_info += '<tr><td>' + (i+1) + ')</td><td>' + shortcut_number_for_player(data.top_9[i].stack) + '</td><td>' + data.top_9[i].name + '</td></tr>';

        }

        all_inner_html.push({id: 'top_players_info', str: top9_info});

        worker.inner_html(all_inner_html);
    }

    ante(data){
        let paid = data.paid;

        for(let i = 0; i < paid.length; i++){

            set_bet(paid[i].id, paid[i].paid, 'Ante');

        }

        if(!this.reconnect_mode){
            worker.play_sound('chips');
        }
    }

    collect_money(){
        collect_money();

        if(!this.reconnect_mode){
            worker.play_sound('collect');
        }
    }

    blinds(data){
        let button_id = data.button;

        worker.class_rem([
            {id: 'dealer', class: 'd1'}, {id: 'dealer', class: 'd2'}, {id: 'dealer', class: 'd3'},
            {id: 'dealer', class: 'd4'}, {id: 'dealer', class: 'd5'}, {id: 'dealer', class: 'd6'},
            {id: 'dealer', class: 'd7'}, {id: 'dealer', class: 'd8'}, {id: 'dealer', class: 'd9'}
        ]);

        worker.class_add('dealer', 'd' + this.seats.id_to_local_seat[button_id]);

        let curr_bb;
        let curr_bb_id;

        if(data.info.length === 1){
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

        if(this.game_mode){

            worker.class_rem([{id: 'premoves', class: 'hidden'}]);
            this.in_game = true;

            if(curr_bb_id === this.seats.my_id){
                worker.inner_html([
                    {id: 'textpremove1', str: 'Check/Fold'},
                    {id: 'textpremove2', str: 'Check'},
                    {id: 'textpremove3', str: 'Call any'}
                ]);
            }
            else{
                worker.inner_html([
                    {id: 'textpremove1', str: 'Fold'},
                    {id: 'textpremove2', str: 'Call ' + shortcut_number_for_decision(curr_bb)},
                    {id: 'textpremove3', str: 'Call any'}
                ]);
            }

        }

        if(!this.reconnect_mode){
            worker.play_sound('chips');
        }
    }

    blinds_increased(data){
        let to_general_info = 'Blinds now ' + shortcut_number_for_decision(data.sb) + ' / ' + shortcut_number_for_decision(data.bb);

        if(data.ante !== 0){
            to_general_info += ' ante ' + shortcut_number_for_decision(data.ante);
        }

        to_general_info += '.';

        to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");\'>Ok</div>';

        worker.inner_html([
            {id: 'general_info', str: to_general_info},
            {id: 'big_blind_shortcut', str: shortcut_number_for_decision(data.bb)},
            {id: 'small_blind_shortcut', str: shortcut_number_for_decision(data.sb)},
            {id: 'ante_shortcut', str: shortcut_number_for_decision(data.ante)}
        ]);

        worker.class_rem([{id: 'general_info', class: 'hidden'}]);
    }

    give_cards(data){
        let up_src = get_src('UP');

        let all_src = [];

        for(let seat of this.seats.all()){

            if(seat.id === this.seats.my_id){

                all_src.push({id: seat.card1, src: get_src(data.first)});
                all_src.push({id: seat.card2, src: get_src(data.second)});

                seat.first_card = data.first;
                seat.second_card = data.second;
            }
            else{
                all_src.push({id: seat.card1, src:  up_src});
                all_src.push({id: seat.card2, src:  up_src});
            }

        }

        worker.src(all_src);
    }

    deal_cards(){
        let up_src = get_src('UP');

        let all_src = [];

        for(let seat of this.seats.all()){
            if(seat.local_seat !== 1 || (seat.local_seat === 1 && !this.resit_mode)){
                all_src.push({id: seat.card1, src: up_src});
                all_src.push({id: seat.card2, src: up_src});
            }
        }

        worker.src(all_src);
    }

    delete_player(data){
        this.seats.delete_player(data.id);
    }

    add_player(data){
        this.seats.add_player(data);
    }

    resit(data){
        this.resit_mode = true;

        if(data.is_final){
            let to_general_info = 'You was resit on final table.';
            to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");\'>Ok</div>';

            worker.inner_html([{id: 'general_info', str: to_general_info}]);
            worker.class_rem([{id: 'general_info', class: 'hidden'}]);

            worker.inner_html([{id: 'table_num_info', str: 'final table'}]);
        }
        else{
            let to_general_info = 'You was resit on table #' + data.table_number;
            to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");\'>Ok</div>';

            worker.inner_html([{id: 'general_info', str: to_general_info}]);
            worker.class_rem([{id: 'general_info', class: 'hidden'}]);

            worker.inner_html([{id: 'table_num_info', str: 'table #' + data.table_number}]);
        }

        this.seats = new Seats(data, this.game_mode);
    }

    switch_decision(data){
        clear_decision();

        worker.class_add('p' + this.seats.id_to_local_seat[data.id], 'in_decision');

        this.seats.id_in_decision = data.id;
    }

    made_decision(data){

        let seat = this.seats.get_by_id(this.seats.id_in_decision);

        if(data.result === 'fold'){

            if(this.seats.id_in_decision === this.seats.my_id){
                made_controlled_player(true);
            }

            if(this.seats.id_to_local_seat[this.seats.id_in_decision] === 1 && this.game_mode){

                worker.src_hide(seat.card1, seat.card2);

            }
            else if(this.replay_mode){

                worker.src_hide(seat.card1, seat.card2);

            }
            else{
                worker.src([
                    {id: seat.card1, src: get_src('ZZ')},
                    {id: seat.card2, src: get_src('ZZ')}
                ]);

            }

            update_info(this.seats.id_in_decision, 'Fold');

        }
        else if(data.result === 'check'){

            if(this.seats.id_in_decision === this.seats.my_id){
                worker.class_rem([{id: 'premoves', class: 'hidden'}]);
                worker.inner_html([
                    {id: 'textpremove1', str: 'Check/Fold'},
                    {id: 'textpremove2', str: 'Check'},
                    {id: 'textpremove3', str: 'Call any'}
                ]);
                premove('1', false);
            }

            update_info(this.seats.id_in_decision, 'Check');

        }
        else if(data.result === 'call'){

            if(this.seats.id_in_decision === this.seats.my_id){

                worker.class_rem([{id: 'premoves', class: 'hidden'}]);
                worker.inner_html([
                    {id: 'textpremove1', str: 'Check/Fold'},
                    {id: 'textpremove2', str: 'Check'},
                    {id: 'textpremove3', str: 'Call any'}
                ]);

                premove('1', false);
            }

            set_bet(this.seats.id_in_decision, data.money, 'Call');

        }
        else if(data.result === 'raise'){

            if(this.in_game && this.seats.id_in_decision !== this.seats.my_id && this.game_mode){

                let myself = this.seats.get_by_id(this.seats.my_id);

                if(myself.stack + myself.chipstack.money > data.money){

                    worker.inner_html([
                        {id: 'textpremove1', str: 'Fold'},
                        {id: 'textpremove2', str: 'Call ' + shortcut_number_for_decision(data.money)},
                        {id: 'textpremove3', str: 'Call any'}
                    ]);

                }
                else{

                    worker.class_add('premove3', 'hidden');

                    worker.inner_html([
                        {id: 'textpremove1', str: 'Fold'},
                        {id: 'textpremove2', str: 'Call ' + shortcut_number_for_decision(data.money)},
                        {id: 'textpremove3', str: ''}
                    ]);

                }

                if(premove_second){
                    premove('2', false);
                }
            }
            else if(this.seats.id_in_decision === this.seats.my_id){

                worker.class_rem([{id: 'premoves', class: 'hidden'}]);
                worker.inner_html([
                    {id: 'textpremove1', str: 'Check/Fold'},
                    {id: 'textpremove2', str: 'Check'},
                    {id: 'textpremove3', str: 'Call any'}
                ]);

                premove('1', false);
            }

            set_bet(this.seats.id_in_decision, data.money, 'Raise');

        }
        else if(data.result === 'all in'){

            if(this.in_game && this.seats.id_in_decision === this.seats.my_id && this.game_mode){

                let myself = this.seats.get_by_id(this.seats.my_id);

                if(myself.stack + myself.chipstack.money > data.money){

                    worker.inner_html([
                        {id: 'textpremove1', str: 'Fold'},
                        {id: 'textpremove2', str: 'Call ' + shortcut_number_for_decision(data.money)},
                        {id: 'textpremove3', str: 'Call any'}
                    ]);

                }
                else{

                    worker.class_add('premove3', 'hidden');

                    worker.inner_html([
                        {id: 'textpremove1', str: 'Fold'},
                        {id: 'textpremove2', str: 'Call ' + shortcut_number_for_decision(data.money)},
                        {id: 'textpremove3', str: ''}
                    ]);

                }

                if(premove_second){
                    premove('2', false);
                }
            }
            else if(this.seats.id_in_decision === this.seats.my_id){
                premove('1', false);
            }

            set_bet(this.seats.id_in_decision, data.money, 'All in');

        }

        worker.inner_html([{id: 'decisions', str: ''}]);

        if(!this.reconnect_mode){
            if(data.result === 'all in' || data.result === 'raise' || data.result === 'call'){
                worker.play_sound('chips');
            }
            else if(data.result === 'fold'){
                worker.play_sound('fold');
            }
            else if(data.result === 'check'){
                worker.play_sound('check');
            }
        }
    }

    excess_money(data){
        set_bet(data.id, this.seats.get_by_id(data.id).chipstack.money - data.money);
    }

    flop(data){
        clear_decision();

        worker.src([
            {id: 'flop1', src: get_src(data.card1)},
            {id: 'flop2', src: get_src(data.card2)},
            {id: 'flop3', src: get_src(data.card3)}
        ]);

        if(!this.reconnect_mode){
            worker.play_sound('fold');
        }
    }

    turn(data){
        clear_decision();

        worker.src([{id: 'turn', src: get_src(data.card)}]);

        if(!this.reconnect_mode){
            worker.play_sound('fold');
        }
    }

    river(data){
        clear_decision();

        worker.src([{id: 'river', src: get_src(data.card)}]);

        if(!this.reconnect_mode){
            worker.play_sound('fold');
        }
    }

    open_cards(data){
        clear_decision();

        if(this.game_mode){
            made_controlled_player(true);
            worker.class_rem([{id: 'premove3', class: 'hidden'}]);
        }

        let all_src = [];

        for(let i = 0; i < data.cards.length; i++){

            let seat = this.seats.get_by_id(data.cards[i].id);

            all_src.push({id: seat.card1, src: get_src(data.cards[i].card1)});
            all_src.push({id: seat.card2, src: get_src(data.cards[i].card2)});

        }

        worker.src(all_src);
    }

    give_money(data){
        if(this.game_mode){
            made_controlled_player(true);
            worker.class_rem([{id: 'premove3', class: 'hidden'}]);
        }

        let seat = this.seats.get_by_id(data.id);

        let _chipstack = 'ch' + seat.local_seat;

        let main_stack_margin_left = get_margin_left(0);
        let main_stack_margin_top = get_margin_top(0);

        let chipstack_margin_left = get_margin_left(seat.local_seat);
        let chipstack_margin_top = get_margin_top(seat.local_seat);

        chipstack = [
            data.id,
            _chipstack,
            chipstack_margin_left,
            chipstack_margin_top,
            main_stack_margin_left,
            main_stack_margin_top
        ];

        seat.chipstack.money += data.money;
        set_bet(data.id, data.money, 'Win');

        this.seats.main_stack.money -= data.money;
        set_bet(-1, this.seats.main_stack.money);

        if(!replay_in_pause && !this.reconnect_mode){

            frames_last = frames_moving;
            cannot_move_chips = true;

            move_stack_from_main();
            worker.play_sound('grab');
        }
    }

    money_results(){
        print('money results');
    }

    hand_results(data){
        if(this.game_mode){
            worker.src([{id: 'your_first_info', src: get_src(first_card)}, {id: 'your_second_info', src: get_src(second_card)}]);
        }

        worker.src([{id: 'flop1_info', src: get_src(data.flop1)}, {id: 'flop2_info', src: get_src(data.flop2)},
            {id: 'flop3_info', src: get_src(data.flop3)}, {id: 'turn_info', src: get_src(data.turn)},
            {id: 'river_info', src: get_src(data.river)}]);

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

    busted(data){
        this.socket.clean = true;

        let to_general_info = 'You are busted! You finished ' + data.place + '.';

        to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");' +
                           'post_socket_stay();\'>Watch</div>';

        to_general_info += '<div class="button in_general g2" onclick=\'document.getElementById("general_info").classList.add("hidden");' +
                           'post_socket_close();\'>Quit</div>';

        worker.inner_html([{id: 'general_info', str: to_general_info}]);
        worker.class_rem([{id: 'general_info', class: 'hidden'}]);

        this.in_loop = false;
    }

    clear(){
        clear_table();
    }

    win(){
        this.socket.clean = true;

        let to_general_info = 'Congratulations! You are winner!';
        to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");' +
                           'post_socket_close();\'>Ok</div>';

        worker.inner_html([{id: 'general_info', str: to_general_info}]);
        worker.class_rem([{id: 'general_info', class: 'hidden'}]);

        this.in_loop = false;
    }

    place(data){
        worker.inner_html([{id: 'place_info', str: data.place}]);

        if(!this.replay_mode && !this.spectate_mode){
            worker.inner_html([{id: 'place_short_info', str: data.place + ' / ' + players_left}]);
        }
    }

    chat(data){
        worker.add_to_chat(data.text);
    }

    disconnected(data){
        if(this.seats.id_to_local_seat[data.id] !== undefined){
            let seat = this.seats.get_by_id(data.id);
            worker.class_add('p' + seat.local_seat, 'is_disconnected');
            seat.disconnected = true;
        }
    }

    connected(data){
        let seat = this.seats.get_by_id(data.id);
        worker.class_rem([{id: 'p' + seat.local_seat, class: 'is_disconnected'}]);
        seat.disconnected = false;
    }

    kick(){
        this.socket.clean = true;

        let to_general_info = 'You was kicked. You have 20 seconds to think now.';
        to_general_info += '<div class="button in_general g1" onclick=\'document.getElementById("general_info").classList.add("hidden");' +
                           'window.location=window.location;\'>Refresh</div>';

        worker.inner_html([{id: 'general_info', str: to_general_info}]);
        worker.class_rem([{id: 'general_info', class: 'hidden'}]);

        worker.inner_html([{id: 'decisions', str: ''}]);

        this.in_loop = false;
    }

    back_counting(data){
        update_info(data.id, data.time + ' sec');
    }

    set_decision(data){
        if(this.reconnect_mode){
            return;
        }

        if(premove_first){

            if(data.decisions[1].type === 'check'){
                set_decision('2');
                made_controlled_player(false);
                return;
            }
            else{
                set_decision('1');
                made_controlled_player(true);
                return;
            }

        }
        else if(premove_second){
            set_decision('2');
            made_controlled_player(false);
            return;
        }
        else if(premove_third){
            set_decision('2'); // because third is call any
            made_controlled_player(false);
            return;
        }

        worker.class_rem([{id: 'premoves', class: 'hidden'}]);

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
                decisions += `<div class='button call_button' onclick='post_set_decision("${i+1}")'>
                    Call ${shortcut_number_for_decision(data.decisions[i].money)}</div>`;
                to_call = data.decisions[i].money;
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
                                onkeyup='post_textchange(this.value)'>`;

                decisions += `<div class='button small_button minus_button' onclick='post_raise_minus()'>-</div>
                              <div class='button small_button plus_button' onclick='post_raise_plus()'>+</div>
                              <div class='button small_button pot_button' onclick='post_raise_pot()'>Pot</div>
                              <div class='button small_button all_in_button' onclick='post_raise_all()'>All</div>`;
            }
            else if(data.decisions[i].type === 'all in'){
                decisions += `<div class='button ${i === 2? 'raise_button': 'call_button'}' 
                                onclick='post_set_decision("${i+1}")'>
                                All in ${shortcut_number_for_decision(data.decisions[i].money)}</div>`;
            }

        }

        worker.inner_html([{id: 'decisions', str: decisions}]);
    }

}

class GameHandler extends Handler{
    constructor(name, socket){
        super(socket);
        this.name = name;
        this.game_mode = true;
    }

    open(){
        this.socket.send('js ' + this.name);
    }
}

class SpectatorHandler extends Handler{
    constructor(table_and_nick, socket){
        super(socket);
        this.table_to_spectate = table_and_nick[0];
        this.nick = table_and_nick[1];
        this.spectate_mode = true;
    }

    open(){
        worker.inner_html([{id: 'sit_on', str: 'watch '}]);
        worker.inner_html([{id: 'you_are_on', str: ''}]);
        worker.inner_html([{id: 'your_cards', str: ''}]);

        this.socket.send('sp ' + this.table_to_spectate);
        this.socket.send(JSON.stringify({type: 'nick', nick: this.nick}));
    }
}

class ReplayHandler extends Handler{
    constructor(id, socket){
        super(socket);
        this.replay_id = id;
        this.replay_mode = true;
    }

    open(){
        worker.inner_html([{id: 'sit_on', str: 'watch replay of '}]);
        worker.inner_html([{id: 'you_are_on', str: ''}]);
        worker.inner_html([{id: 'your_cards', str: ''}]);

        worker.class_rem([{id: 'replay_control', class: 'hidden'}]);
        worker.bigger_chat();

        this.socket.send('rp ' + this.replay_id);
    }
}

class Chipstack{
    constructor(local_seat, money){
        this.money = money;
        this.ch11 = 'p' + local_seat + 'r1c1';
        this.ch12 = 'p' + local_seat + 'r1c2';
        this.ch13 = 'p' + local_seat + 'r1c3';
        this.ch14 = 'p' + local_seat + 'r1c4';
        this.ch21 = 'p' + local_seat + 'r2c1';
        this.ch22 = 'p' + local_seat + 'r2c2';
        this.ch23 = 'p' + local_seat + 'r2c3';
        this.ch24 = 'p' + local_seat + 'r2c4';
    }
}

class Player{
    constructor(data, local_seat){
        this.id = data.id;
        this.name = data.name;
        this.disconnected = data.disconnected;
        this.stack = data.stack;
        this.local_seat = local_seat;
        this.chipstack = new Chipstack(local_seat, 0);
        this.card1 = 'c' + local_seat + '1';
        this.card2 = 'c' + local_seat + '2';
    }

    delete_cards(){
        worker.src([{id: this.card1, src: get_src('ZZ')}, {id: this.card2, src: get_src('ZZ')}]);
    }
}

class Seats{
    constructor(data, need_to_shift) {

        let inner_html = [];

        let seats_shift = 0;

        this.players_left = data.players_left;

        this.total_seats = data.seats;

        let players = data.players;
        this.table_number = data.table_number;

        this.is_final = data.is_final;

        if (need_to_shift) {

            while (players[0].controlled === undefined || players[0].controlled === false) {
                players.push(players.shift());
                seats_shift++;
            }

            this.my_id = players[0].id;
        }

        let to_place;

        if (data.seats === 2) {
            to_place = [1, 6];
        }
        else if (data.seats === 3) {
            to_place = [1, 4, 7];
        }
        else if (data.seats === 4) {
            to_place = [1, 3, 6, 8];
        }
        else if (data.seats === 5) {
            to_place = [1, 3, 5, 6, 8];
        }
        else if (data.seats === 6) {
            to_place = [1, 2, 4, 6, 7, 9];
        }
        else if (data.seats === 7) {
            to_place = [1, 2, 4, 5, 6, 7, 9];
        }
        else if (data.seats === 8) {
            to_place = [1, 2, 3, 4, 6, 7, 8, 9];
        }
        else if (data.seats === 9) {
            to_place = [1, 2, 3, 4, 5, 6, 7, 8, 9];
        }

        this.seats = new Map();
        this.id_to_local_seat = {};
        this.real_seat_to_local_seat = {};

        inner_html.push({id: 'players', str: ''});

        let doc_players = '';

        for (let i = 0; i < to_place.length; i++) {

            this.real_seat_to_local_seat[(seats_shift + i) % data.seats] = to_place[i];

            if (players[i].id !== null) {

                doc_players += `<div id=p${to_place[i]} class='player${players[i].disconnected ? ' is_disconnected' : ''}'>
                    ${players[i].name}<br>${shortcut_number_for_player(players[i].stack)}</div>`;

                this.seats.set(to_place[i], new Player(players[i], to_place[i]));

                this.id_to_local_seat[players[i].id] = to_place[i];

            }
            else {

                if (!data.is_final) {
                    doc_players += '<div id="p' + to_place[i] + '" class="player"><br>Empty seat</div>';
                }
                else {
                    doc_players += '<div id="p' + to_place[i] + '" class="player hidden"><br>Empty seat</div>';
                }

            }
        }

        inner_html.push({id: 'players', str: doc_players});

        this.main_stack = new Chipstack('0', 0);

        worker.inner_html(inner_html);
    }

    add_player(data){
        let local_seat = this.real_seat_to_local_seat[data.seat];

        this.seats.set(local_seat, new Player(data, local_seat));

        this.id_to_local_seat[data.id] = local_seat;

        if(this.is_final){
            worker.class_rem([{id: 'p' + local_seat, class: 'hidden'}]);
            update_info(data.id, '');
        }
        else{
            update_info(data.id, 'New player');
        }
    }

    delete_player(id){
        let seat = this.get_by_id(id);

        seat.delete_cards();

        set_empty_seat_info(seat.local_seat);
        
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
            clear_table();

            this.socket = undefined;
            this.handler.loop = false;

            this.create_connection([table_number, this.handler.name], SpectatorHandler);

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
            raise_minus(data.value, data.max_value, data.min_value);
            break;

        case 'raise plus':
            raise_plus(data.value, data.max_value, data.min_value);
            break;

        case 'raise all':
            raise_all(data.max_value);
            break;

        case 'raise pot':
            raise_pot(data.max_value);
            break;

        case 'textraise':
            text_change(data.text, data.max_value, data.min_value);
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
            set_decision(data.value);
            break;

        case 'pause play':
            replay_pause_play();
            break;

        case 'next step':
            replay_next_step();
            break;

        case 'prev hand':
            replay_prev_hand();
            break;

        case 'next hand':
            replay_next_hand();
            break;

        case 'tournament info':
            t_info_click();
            break;

        case 'last hand info':
            lh_info_click();
            break;

        case 'chat message':
            chat_message(data.key, data.text);
            break;

        case 'premove':
            premove(data.answer, data.checked);
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

    remove_style(obj){
        this.send({type: 'remove style', obj: obj});
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

    margin(obj){
        this.send({type: 'margin', obj: obj});
    }

    alert(msg){
        this.send({type: 'alert', msg: msg});
    }

    location(location){
        this.send({type: 'location', to: location});
    }

    play_sound(file){
        if(!replay_in_pause){
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

}

let worker = new WorkerConnection();

onmessage = e => worker.message(e);

const available_chips = [
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

let to_call;
let is_t_info_active = false;
let is_lh_info_active = false;
let table_number;
let first_card;
let players_left;
let second_card;
let premove_first = false;
let premove_second = false;
let premove_third = false;
let replay_in_pause = false;
let save_positions_chipstacks;
let frames_moving = 50;
let frames_last;
let cannot_move_chips = false;
let chipstack;

const gauss = [
    0, 0.001, 0.002, 0.003, 0.004, 0.006, 0.009, 0.013, 0.018, 0.024,
    0.032, 0.042, 0.054, 0.068, 0.085, 0.105, 0.128, 0.155, 0.185, 0.219,
    0.256, 0.296, 0.339, 0.384, 0.430, 0.477, 0.524, 0.571, 0.617, 0.662,
    0.705, 0.745, 0.782, 0.816, 0.846, 0.873, 0.896, 0.916, 0.933, 0.947,
    0.959, 0.969, 0.977, 0.983, 0.988, 0.992, 0.995, 0.997, 0.999, 1
];

Array.prototype.remove = function(from, to) {
    let rest = this.slice((to || from) + 1 || this.length);
    this.length = from < 0 ? this.length + from : from;
    return this.push.apply(this, rest);
};

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function print(str){
    console.log(str);
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
        return (parseInt(num/100)/10) + 'k';
    }
    else if(num < 1000000){
        // 123231 -> 123k
        return parseInt(num/1000) + 'k';
    }
    else if(num < 10000000){
        // 3 123 345 -> 3.12m
        return (parseInt(num/10000)/100) + 'm';
    }
    else if(num < 100000000){
        // 12 345 678 -> 12.3m
        return ((parseInt(num/100000))/10) + 'm';
    }
    else if(num < 1000000000){
        // 123 345 678 -> 123m
        return parseInt(num/1000000) + 'm';
    }
    else if(num < 10000000000){
        // 1 123 345 678 -> 1.12b
        return (parseInt(num/10000000)/100) + 'b';
    }
    else if(num < 100000000000){
        // 12 123 345 678 -> 12.1b
        return (parseInt(num/100000000)/10) + 'b';
    }
    else {
        // 122 223 345 678 -> 123b
        return parseInt(num/1000000000) + 'b';
    }

}

function get_sound(file){

    if(file === 'chips'){
        let type_sound = parseInt(Math.random()*5);

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

function get_margin_left(i){

    if(i === 0){
        return 310;
    }
    else if(i === 1){
        return 310;
    }
    else if(i === 2){
        return 110;
    }
    else if(i === 3){
        return 70;
    }
    else if(i === 4){
        return 75;
    }
    else if(i === 5){
        return 140;
    }
    else if(i === 6){
        return 480;
    }
    else if(i === 7){
        return 545;
    }
    else if(i === 8){
        return 550;
    }
    else if(i === 9){
        return 510;
    }
    return 0;

}

function get_margin_top(i){

    if(i === 0){
        return -180;
    }
    else if(i === 1){
        return -80;
    }
    else if(i === 2){
        return -110;
    }
    else if(i === 3){
        return -200;
    }
    else if(i === 4){
        return -290;
    }
    else if(i === 5){
        return -380;
    }
    else if(i === 6){
        return -380;
    }
    else if(i === 7){
        return -290;
    }
    else if(i === 8){
        return -200;
    }
    else if(i === 9){
        return -100;
    }
    return 0;

}

function replay_pause_play(){

    if(replay_in_pause){

        replay_in_pause = false;

        worker.class_add('replay_next_step', 'hidden');
        worker.inner_html([{id: 'replay_pause_play', str: 'Pause'}]);

        worker.socket.send('play');

    }
    else{

        replay_in_pause = true;

        worker.class_rem([{id: 'replay_next_step', class: 'hidden'}]);
        worker.inner_html([{id: 'replay_pause_play', str: 'Play'}]);

        worker.socket.send('pause');

    }

}

function replay_next_step(){
    worker.socket.send('next step');
}

function replay_prev_hand(){

    if(cannot_move_chips){
        setTimeout(replay_prev_hand, 10);
        return;
    }

    worker.socket.send('prev hand');
    worker.inner_html([{id: 'chat', str: 'Chat:'}]);
}

function replay_next_hand(){

    if(cannot_move_chips){
        setTimeout(replay_next_hand, 10);
        return;
    }

    worker.socket.send('next hand');
    worker.inner_html([{id: 'chat', str: 'Chat:'}]);
}

function update_info(id, reason, count=0){

    if(reason !== '' && count > 0){
        reason = reason + ' ' + shortcut_number_for_decision(count);
    }

    let seat = worker.socket.handler.seats.get_by_id(id);
    worker.inner_html([
        {
            id: 'p' + seat.local_seat,
            str: seat.name + '<br>' + shortcut_number_for_player(seat.stack) + '<br>' + reason
        }
    ]);

}

function set_empty_seat_info(seat){
// TODO : handle 'is_disconnected' attribute when setting empty
    if(table_number === 0){
        worker.class_add('p' + seat, 'hidden');
    }
    else{
        worker.inner_html([{id: 'p' + seat, str: '<br>Empty seat'}]);
    }

}

function clear_table(){

    let zz_src = get_src('ZZ');

    let all_src = [
        {id: 'flop1', src: zz_src},
        {id: 'flop2', src: zz_src},
        {id: 'flop3', src: zz_src},
        {id: 'turn', src: zz_src},
        {id: 'river', src: zz_src}
    ];

    clear_decision();

    for(let seat of worker.socket.handler.seats.all()){

        all_src.push({id: seat.card1, src: zz_src});
        all_src.push({id: seat.card2, src: zz_src});

        set_bet(seat.id, 0);

    }

    set_bet(-1, 0);

    worker.src(all_src);

}

function text_change(text, max_value, min_value){

    if(text.length > 0) {
        if (text.length === 1 && text === '0') {
            worker.change_value('textraise', '');
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

            worker.change_value('textraise', new_text);

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

            worker.change_value('range', new_value);
            worker.inner_html([{
                id: 'raise',
                str: (new_value === max_value ? 'All in ' : 'Raise ') + shortcut_number_for_decision(new_value)
            }]);
        }
    }
}

function chat_message(key, text){

    if(key === 13 && text.length > 0){ // enter key is 13

        worker.change_value('message', '');

        if(!worker.socket.handler.replay_mode){
            worker.socket.send(JSON.stringify({type: 'chat', text: text}));
        }

    }
}


function raise_minus(value, max_value, min_value){

    let new_value = (+value) - (+min_value) > min_value? (+value) - (+min_value): min_value;

    worker.change_value('range', new_value);
    worker.inner_html([{id: 'raise', str: (new_value===max_value?'All in ':'Raise ') + shortcut_number_for_decision(new_value)}]);

}

function raise_plus(value, max_value, min_value){

    let new_value = (+value) + (+min_value) < max_value? (+value) + (+min_value) : max_value;

    worker.change_value('range', new_value);
    worker.inner_html([{id: 'raise', str: (new_value===max_value?'All in ':'Raise ') + shortcut_number_for_decision(new_value)}]);

}

function raise_all(max_value){

    worker.change_value('range', max_value);
    worker.inner_html([{id: 'raise', str: 'All in ' + shortcut_number_for_decision(max_value)}]);

}

function raise_pot(max_value){

    let in_pot = worker.socket.handler.seats.main_stack.money;

    for(let seat of worker.socket.handler.seats.all()){
        in_pot += seat.chipstack.money;
    }

    let raise_amount = in_pot + 2 * to_call;

    if(raise_amount > max_value){
        raise_amount = max_value;
    }

    worker.change_value('range', raise_amount);
    worker.inner_html([
        {id: 'raise', str: (raise_amount===max_value?'All in ':'Raise ') + shortcut_number_for_decision(raise_amount)}
    ]);

}

function t_info_click(){

    if(is_t_info_active === false){

        if(is_lh_info_active){
            lh_info_click();
        }

        is_t_info_active = true;
        worker.class_rem([{id: 'tournament_info', class: 'hidden'}]);
    }
    else{

        is_t_info_active = false;
        worker.class_add('tournament_info', 'hidden');

    }

}

function lh_info_click(){

    if(is_lh_info_active === false){

        if(is_t_info_active){
            t_info_click();
        }

        is_lh_info_active = true;
        worker.class_rem([{id: 'last_hand_info', class: 'hidden'}]);

    }
    else{

        is_lh_info_active = false;
        worker.class_add('last_hand_info', 'hidden');

    }

}

function premove(answer, checked){

    let all_premoves = [
        {id: 'premove1', checked: false},
        {id: 'premove2', checked: false},
        {id: 'premove3', checked: false}
    ];

    premove_first = false;
    premove_second = false;
    premove_third = false;

    if(checked){

        if(answer === '1'){
            all_premoves.push({id: 'premove1', checked: true});
            premove_first = true;
        }
        else if(answer === '2'){
            all_premoves.push({id: 'premove2', checked: true});
            premove_second = true;
        }
        else if(answer === '3'){
            all_premoves.push({id: 'premove3', checked: true});
            premove_third = true;
        }

    }

    worker.set_premove(all_premoves);

}

function clear_decision(){

    let to_place;
    let total_seats = worker.socket.handler.seats.total_seats;

    if(total_seats === 2){
        to_place = [1, 6];
    }
    else if(total_seats === 3){
        to_place = [1, 4, 7];
    }
    else if(total_seats === 4){
        to_place = [1, 3, 6, 8];
    }
    else if(total_seats === 5){
        to_place = [1, 3, 5, 6, 8];
    }
    else if(total_seats === 6){
        to_place = [1, 2, 4, 6, 7, 9];
    }
    else if(total_seats === 7){
        to_place = [1, 2, 4, 5, 6, 7, 9];
    }
    else if(total_seats === 8){
        to_place = [1, 2, 3, 4, 6, 7, 8, 9];
    }
    else if(total_seats === 9){
        to_place = [1, 2, 3, 4, 5, 6, 7, 8, 9];
    }

    let all_rem = [];

    for(let i = 0; i < to_place.length; i++){

        all_rem.push({id: 'p' + to_place[i], class: 'in_decision'});

    }

    worker.class_rem(all_rem);
}

function set_decision(to_send){

    worker.inner_html([{id: 'decisions', str: ''}]);
    worker.socket.send(JSON.stringify({type: 'decision', text: to_send}));

}

function made_controlled_player(is_fold){

    if(worker.socket.handler.game_mode){

        premove('1', false);

        if(is_fold){
            worker.socket.handler.in_game = false;
            worker.class_add('premoves', 'hidden');
        }
        else{
            worker.inner_html([
                {id: 'textpremove1', str: 'Check/Fold'},
                {id: 'textpremove2', str: 'Check'},
                {id: 'textpremove3', str: 'Call any'}
            ]);
        }

    }

    

}

function set_bet(id, count, reason=''){

    if(id !== -1){

        let seat = worker.socket.handler.seats.get_by_id(id);

        seat.stack -= count - seat.chipstack.money;
        seat.chipstack.money = count;

        update_info(id, reason, count);

    }

    let pot_count = worker.socket.handler.seats.main_stack.money;

    for(let seat of worker.socket.handler.seats.all()){
        pot_count += seat.chipstack.money;
    }

    worker.inner_html([{id: 'pot_count', str: shortcut_number_for_player(pot_count)}]);

    let amounts = [];

    for(let i = 0; i < available_chips.length; i++){
        if(count >= available_chips[i][0]){
            let int_amount = parseInt(count / available_chips[i][0]);
            amounts.push([available_chips[i][1], int_amount]);
            count -= int_amount * available_chips[i][0];
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

        amounts.remove(index_betweens + 1);

    }

    let seat_to_set_bet;

    if(id === -1){
        seat_to_set_bet = worker.socket.handler.seats.main_stack;
    }
    else{
        seat_to_set_bet = worker.socket.handler.seats.get_by_id(id);
    }

    let chip11 = seat_to_set_bet.ch11;
    let chip12 = seat_to_set_bet.ch12;
    let chip13 = seat_to_set_bet.ch13;
    let chip14 = seat_to_set_bet.ch14;
    let chip21 = seat_to_set_bet.ch21;
    let chip22 = seat_to_set_bet.ch22;
    let chip23 = seat_to_set_bet.ch23;
    let chip24 = seat_to_set_bet.ch24;

    let all_chips = [
        {id: chip11, str: ''},
        {id: chip12, str: ''},
        {id: chip13, str: ''},
        {id: chip14, str: ''},
        {id: chip21, str: ''},
        {id: chip22, str: ''},
        {id: chip23, str: ''},
        {id: chip24, str: ''}
    ];

    let chip_order;

    if(amounts.length === 8){
        chip_order = [chip21, chip22, chip23, chip24, chip11, chip12, chip13, chip14];
    }
    else if(amounts.length === 7){
        chip_order = [chip21, chip22, chip23, chip11, chip12, chip13, chip14];
    }
    else if(amounts.length === 6){
        chip_order = [chip21, chip22, chip11, chip12, chip13, chip14];
    }
    else if(amounts.length === 5){
        chip_order = [chip21, chip11, chip12, chip13, chip14];
    }
    else if(amounts.length === 4){
        chip_order = [chip11, chip12, chip13, chip14];
    }
    else if(amounts.length === 3){
        chip_order = [chip12, chip13, chip14];
    }
    else if(amounts.length === 2){
        chip_order = [chip12, chip13];
    }
    else if(amounts.length === 1){
        chip_order = [chip12];
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

function move_stacks_to_main(){

    frames_last -= 1;

    let all_margin = [];

    if(frames_last !== 0){

        let percent_done = gauss[frames_moving - frames_last - 1];

        for(let i = 0; i < save_positions_chipstacks.length; i++){

            let curr_chipstack = save_positions_chipstacks[i];

            all_margin.push({
                id: curr_chipstack[1],
                left: (curr_chipstack[2] + parseInt((curr_chipstack[4] - curr_chipstack[2]) * percent_done)) + 'px',
                top: (curr_chipstack[3] + parseInt((curr_chipstack[5] - curr_chipstack[3]) * percent_done)) + 'px'
            });

        }

        worker.margin(all_margin);

        setTimeout(move_stacks_to_main, 10);
    }
    else{

        cannot_move_chips = false;

        for(let i = 0; i < save_positions_chipstacks.length; i++){

            let curr_chipstack = save_positions_chipstacks[i];

            all_margin.push({id: curr_chipstack[1], left: curr_chipstack[2] + 'px', top: curr_chipstack[3] + 'px'});

            set_bet(worker.socket.handler.seats.seats.get(curr_chipstack[0]).id, 0);

        }

        set_bet(-1, worker.socket.handler.seats.main_stack.money);

        worker.margin(all_margin);

    }

}

function move_stack_from_main(){

    frames_last -= 1;

    if(frames_last !== 0){

        let percent_done = gauss[frames_last];

        worker.margin([{
            id: chipstack[1],
            left: (chipstack[2] + parseInt((chipstack[4] - chipstack[2]) * percent_done)) + 'px',
            top: (chipstack[3] + parseInt((chipstack[5] - chipstack[3]) * percent_done)) + 'px'
        }]);

        setTimeout(move_stack_from_main, 10);
    }
    else{

        cannot_move_chips = false;

        worker.margin([{id: chipstack[1], left: chipstack[2] + 'px', top: chipstack[3] + 'px'}]);

    }

}

function collect_money(){

    if(cannot_move_chips){
        return;
    }

    clear_decision();

    save_positions_chipstacks = [];

    let main_stack_margin_left = get_margin_left(0);
    let main_stack_margin_top = get_margin_top(0);

    let all_chips = [];

    for(let seat of worker.socket.handler.seats.all()){

        if(seat.chipstack.money > 0){

            worker.socket.handler.seats.main_stack.money += seat.chipstack.money;
            seat.stack -= seat.chipstack.money;

            chipstack = 'ch' + seat.local_seat;

            all_chips.push({id: chipstack});

            let chipstack_margin_left = get_margin_left(seat.local_seat);
            let chipstack_margin_top = get_margin_top(seat.local_seat);

            save_positions_chipstacks.push([
                seat.local_seat,
                chipstack,
                chipstack_margin_left,
                chipstack_margin_top,
                main_stack_margin_left,
                main_stack_margin_top
            ]);

            if(replay_in_pause || worker.socket.handler.reconnect_mode){
                set_bet(seat.id, 0);
            }

        }

    }

    worker.remove_style(all_chips);

    if(save_positions_chipstacks.length > 0){

        if(!replay_in_pause && !worker.socket.handler.reconnect_mode){

            frames_last = frames_moving;
            cannot_move_chips = true;

            setTimeout(move_stacks_to_main, 10);
        }
        else{
            set_bet(-1, worker.socket.handler.seats.main_stack.money);
        }

    }

}