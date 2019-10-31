var table = {
    a8: {id: 'br1', side: 'black', moves: 0, type: 'rook'}, 
    b8: {id: 'bn1', side: 'black', moves: 0, type: 'knight'},
    c8: {id: 'bb1', side: 'black', moves: 0, type: 'bishop'},
    d8: {id: 'bq1', side: 'black', moves: 0, type: 'queen'},
    e8: {id: 'bk',  side: 'black', moves: 0, type: 'king'},
    f8: {id: 'bb2', side: 'black', moves: 0, type: 'bishop'},
    g8: {id: 'bn2', side: 'black', moves: 0, type: 'knight'},
    h8: {id: 'br2', side: 'black', moves: 0, type: 'rook'},
    a7: {id: 'bp1', side: 'black', moves: 0, type: 'pawn'},
    b7: {id: 'bp2', side: 'black', moves: 0, type: 'pawn'},
    c7: {id: 'bp3', side: 'black', moves: 0, type: 'pawn'},
    d7: {id: 'bp4', side: 'black', moves: 0, type: 'pawn'},
    e7: {id: 'bp5', side: 'black', moves: 0, type: 'pawn'},
    f7: {id: 'bp6', side: 'black', moves: 0, type: 'pawn'},
    g7: {id: 'bp7', side: 'black', moves: 0, type: 'pawn'},
    h7: {id: 'bp8', side: 'black', moves: 0, type: 'pawn'},
    a6: 'nothing', b6: 'nothing', c6: 'nothing', d6: 'nothing',
    e6: 'nothing', f6: 'nothing', g6: 'nothing', h6: 'nothing',
    a5: 'nothing', b5: 'nothing', c5: 'nothing', d5: 'nothing',
    e5: 'nothing', f5: 'nothing', g5: 'nothing', h5: 'nothing',
    a4: 'nothing', b4: 'nothing', c4: 'nothing', d4: 'nothing',
    e4: 'nothing', f4: 'nothing', g4: 'nothing', h4: 'nothing',
    a3: 'nothing', b3: 'nothing', c3: 'nothing', d3: 'nothing',
    e3: 'nothing', f3: 'nothing', g3: 'nothing', h3: 'nothing',
    a2: {id: 'wp1', side: 'white', moves: 0, type: 'pawn'},
    b2: {id: 'wp2', side: 'white', moves: 0, type: 'pawn'},
    c2: {id: 'wp3', side: 'white', moves: 0, type: 'pawn'},
    d2: {id: 'wp4', side: 'white', moves: 0, type: 'pawn'},
    e2: {id: 'wp5', side: 'white', moves: 0, type: 'pawn'},
    f2: {id: 'wp6', side: 'white', moves: 0, type: 'pawn'},
    g2: {id: 'wp7', side: 'white', moves: 0, type: 'pawn'},
    h2: {id: 'wp8', side: 'white', moves: 0, type: 'pawn'},
    a1: {id: 'wr1', side: 'white', moves: 0, type: 'rook'},
    b1: {id: 'wn1', side: 'white', moves: 0, type: 'knight'},
    c1: {id: 'wb1', side: 'white', moves: 0, type: 'bishop'},
    d1: {id: 'wq1', side: 'white', moves: 0, type: 'queen'},
    e1: {id: 'wk' , side: 'white', moves: 0, type: 'king'},
    f1: {id: 'wb2', side: 'white', moves: 0, type: 'bishop'},
    g1: {id: 'wn2', side: 'white', moves: 0, type: 'knight'},
    h1: {id: 'wr2', side: 'white', moves: 0, type: 'rook'}
};

var moves_history = [];
var table_history = ['rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -']; // Start position in FEN notation
// target,from,to,notation,type[move,capture(captured:object)][castle_kingside,castle queenside,en_passant,promotion(new_figure:type)]
var side_to_move = 'white';
var board_position = 'standart'; // or 'reversed'
var possibles;
var candidate_move;
var black_king = 'e8';
var white_king = 'e1';
var promotion_mode = false;
var game_over = false;
var game_result;
var dont_touch = false;
var stockfish = STOCKFISH();

stockfish.onmessage = function(event) {
    var data = (event.data ? event.data : event).split(' ');
    //console.log(event.data ? event.data : event);
    //return;
    if(data[0] === 'bestmove' && !dont_touch){

        var from = data[1][0] + data[1][1];
        var to = data[1][2] + data[1][3];

        var moves = get_moves(side_to_move)[from], move;

        for(var i in moves){
            move = moves[i];
            if(move.to === to){

                if(move.promotion){
                    move.new_figure = data[1][4] === 'q'? 'queen': data[1][4] === 'n'? 'knight': data[1][4] === 'r'? 'rook': 'bishop';
                }

                make_move(move);
                
                move_graphic(move);
                if(move.promotion){
                    move_graphic(move);
                }

                if(!game_over){
                    if(side_to_move === 'white'? default_depth >=0: default_depth_2 >=0){

                        setTimeout(function(){
                            stockfish.postMessage("setoption name Skill Level value " + (side_to_move === 'white'? default_depth: default_depth_2));

                            var message = 'position startpos';
                            if(moves_history.length){
                                message += ' moves';
                                for(var move in moves_history){
                                    move = moves_history[move];
                                    message += ' ' + move.from + move.to;
                                    if(move.promotion){
                                        message += move.new_figure[0];
                                    }
                                }
                            }

                            stockfish.postMessage(message);
                            stockfish.postMessage("go depth " + ((side_to_move === 'white'? (default_depth <= 10? default_depth: 10 + (default_depth-10)/2|0) 
                                : (default_depth_2 <= 10? default_depth_2: 10 + (default_depth_2-10)/2|0) ) + (Math.random() * 5 | 0) - 2));
                        }, 100);

                    }
                    else{
                        setTimeout(function(){
                            make_random_move();
                        }, 100);
                    }
                }
                else{
                    document.getElementById('new_game').style.display = 'block';
                }

                break;
            }
        }

    }

    if(data[0] === 'info' && data[3] === 'seldepth'){

        var evaluation = data[9]/100 * (side_to_move === 'white'? 1: -1)

        if(!game_over){
            if(side_to_move === 'white' && !dont_touch){
                document.getElementById('result').innerHTML = 'Оценка белыми: <br>';
            }
            else{
                document.getElementById('result2').innerHTML = 'Оценка чёрными: <br>';
            }
        }
        else{
            if(side_to_move === 'white' && !dont_touch){
                document.getElementById('result').innerHTML = 'Белые - ';
            }
            else{
                document.getElementById('result2').innerHTML = 'Чёрные - ';
            }
        }

        if(data[8] === 'cp'){
            if(side_to_move === 'white' && !dont_touch){
                document.getElementById('result').innerHTML += evaluation + (data[9] % 100 === 0? '.0': '') + (data[9] % 10 === 0? '0': '');
            }
            else{
                document.getElementById('result2').innerHTML += evaluation + (data[9] % 100 === 0? '.0': '') + (data[9] % 10 === 0? '0': '');
            }
        }
        else{
            if(side_to_move === 'white' && !dont_touch){
                document.getElementById('result').innerHTML += '#' + (data[9] * (side_to_move === 'white'? 1: -1));
            }
            else{
                document.getElementById('result2').innerHTML += '#' + (data[9] * (side_to_move === 'white'? 1: -1));
            }
        }

    }

    if(data[0] === 'bestmove' && dont_touch){
        dont_touch = false;
        setTimeout(function(){
            stockfish.postMessage("setoption name Skill Level value " + (side_to_move === 'white'? default_depth: default_depth_2))
            stockfish.postMessage("position fen " + table_history[table_history.length - 1]);
            stockfish.postMessage("go depth " + ((side_to_move === 'white'? (default_depth <= 10? default_depth: 10 + (default_depth-10)/2|0) 
                : (default_depth_2 <= 10? default_depth_2: 10 + (default_depth_2-10)/2|0) ) + (Math.random() * 5 | 0) - 2));
        }, 100);
    }

};


function chr(char, num){
    return String.fromCharCode(char.charCodeAt(0) + num);
}

function clone(obj){
    var copy = {};
    for (var attr in obj) {
        copy[attr] = obj[attr];
    }
    return copy;
}

function set_history_of_moves(){
    
    var text = '', curr_move;
    if(moves_history.length){
        
        for(var index in moves_history){
            if(index % 2) continue;
            curr_move = moves_history[index];

            if(index < 198)text += ' ';
            if(index < 18)text += ' ';

            text += String(((+index+2) / 2)|0) + '. ' + curr_move.notation + ' ';
            if(moves_history[+index+1]){

                if(curr_move.notation.length === 2)text += '     ';
                if(curr_move.notation.length === 3)text += '    ';
                if(curr_move.notation.length === 4)text += '   ';
                if(curr_move.notation.length === 5)text += '  ';
                if(curr_move.notation.length === 6)text += ' ';

                curr_move = moves_history[+index+1];
                text += curr_move.notation + '\n';
            }

        }
    }
    else{
        text = ' ';
    }

    text = text.substring(0, text.length - 1);

    if(game_over){

        if(game_result !== '1/2 - 1/2'){
            text = text.substring(0, text.length - 1);
            text += '#';
        }

        text += '\n\n';

        if(game_result.length === 5){
            text += '       ' + game_result;
        }
        else{
            text += '     ' + game_result;
        }

    }

    var textarea = document.getElementById('moves');

    textarea.innerHTML = text;
    textarea.scrollTop = textarea.scrollHeight - textarea.clientHeight;
    
}

function check_table(){
    
    if(promotion_mode) return;
    
    var length = 0, index, moves = get_moves(side_to_move);
    
    for(index in moves) length += moves[index].length;
    
    if(length === 0){
        
        if(in_check(side_to_move)){
            return 'Checkmate to '+side_to_move;
        }
        else{
            return 'Draw my stalemate';
        }
    }
    
     
    var fifty_moves_rule = 100, history_elem;
    
    for(index in moves_history){
        history_elem = moves_history[index];
        
        fifty_moves_rule -= 1;
        
        if(history_elem.capture || history_elem.target === 'pawn') fifty_moves_rule = 100;
        
        if(fifty_moves_rule === 0){
            return 'Draw by 50 moves rule';
        }
    }
    
    var table_elem, black_points = 0, white_points = 0;
    for(index in table){
        table_elem = table[index];
        
        
        if(table_elem !== 'nothing'){
            
            if(table_elem.type === 'king') continue;
            
            if(table_elem.side === 'white'){
                
                if(table_elem.type === 'queen' || table_elem.type === 'rook' || table_elem.type === 'pawn')white_points += 10;
                else if(table_elem.type === 'knight')white_points += 2;
                else if(table_elem.type === 'bishop')white_points += 3;
                
            }
            else if(table_elem.side === 'black'){
                
                if(table_elem.type === 'queen' || table_elem.type === 'rook' || table_elem.type === 'pawn')black_points += 10;
                else if(table_elem.type === 'knight')black_points += 2;
                else if(table_elem.type === 'bishop')black_points += 3;
                
            }
            
        }
    }
    
    if(black_points < 4 && white_points < 4) return 'Draw by insufficient material';
    
    var only_bishops_of_same_colour = true, first_colour = '';
    for(index in table){
        table_elem = table[index];
        
        
        if(table_elem !== 'nothing'){
            
            if(table_elem.type === 'king') continue;
            if(table_elem.type === 'queen' || table_elem.type === 'rook' || table_elem.type === 'pawn' || table_elem.type === 'knight'){
                only_bishops_of_same_colour = false;
                break;
            };
            
            if(first_colour === ''){
                first_colour = (index.charCodeAt(0) + index.charCodeAt(1)) % 2;
            }
            else{
                if(first_colour !== (index.charCodeAt(0) + index.charCodeAt(1)) % 2){
                    only_bishops_of_same_colour = false;
                    break;
                }
            }
            
        }
    }
    
    if(only_bishops_of_same_colour) return 'Draw by insufficient material';
    
    var repetition = false; 
    var count_of_positions = {}, pos;
    
    for(index in table_history){
        pos = table_history[index];
        
        if(pos in count_of_positions){
            count_of_positions[pos] += 1;
        }
        else{
            count_of_positions[pos] = 1;
        }
        
        if(count_of_positions[pos] === 3){
            repetition = true;
            break;
        }
        
    }
    
    if(repetition) return 'Draw by threefold repetition';
    
    return 'Nothing';
}

function in_check(side){
    
    if(side === 'white'){
        var p = white_king;
        
        var possible_moves = [chr(p[0],1)+chr(p[1],2),
                              chr(p[0],2)+chr(p[1],1),
                              chr(p[0],2)+chr(p[1],-1),
                              chr(p[0],1)+chr(p[1],-2),
                              chr(p[0],-1)+chr(p[1],-2),
                              chr(p[0],-2)+chr(p[1],-1),
                              chr(p[0],-2)+chr(p[1],1),
                              chr(p[0],-1)+chr(p[1],2)];

        var index, possible_move;
        for(index in possible_moves){
            possible_move = possible_moves[index];

            if(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                
                if(table[possible_move] !== 'nothing' && table[possible_move].side === 'black' && 
                        table[possible_move].type === 'knight'){
                    return true;
                }
            }
        }
        
        possible_moves = [chr(p[0],1)+chr(p[1],1),
                              chr(p[0],1)+chr(p[1],0),
                              chr(p[0],1)+chr(p[1],-1),
                              chr(p[0],0)+chr(p[1],-1),
                              chr(p[0],0)+chr(p[1],1),
                              chr(p[0],-1)+chr(p[1],-1),
                              chr(p[0],-1)+chr(p[1],0),
                              chr(p[0],-1)+chr(p[1],1)];
                          
        for(index in possible_moves){
            possible_move = possible_moves[index];

            if(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                
                if(table[possible_move] !== 'nothing' && table[possible_move].side === 'black' && 
                        table[possible_move].type === 'king'){
                    return true;
                }
            }
        }
        
        
        var direction, directions = [[1, 1], [1, -1], [-1, -1], [-1, 1]];
        for(index in directions){
            direction = directions[index];

            possible_move = chr(p[0],direction[0])+chr(p[1],direction[1]);
            while(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){

                if(table[possible_move] !== 'nothing' && table[possible_move].side === 'black' && 
                        (table[possible_move].type === 'bishop' || table[possible_move].type === 'queen') ){
                    return true;
                }
                
                if(table[possible_move] !== 'nothing'){
                    break;
                }

                possible_move = chr(possible_move[0],direction[0])+chr(possible_move[1],direction[1]);

            }
        }
        
        
        directions = [[1, 0], [0, 1], [-1, 0], [0, -1]];
        for(index in directions){
            direction = directions[index];

            possible_move = chr(p[0],direction[0])+chr(p[1],direction[1]);
            while(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){

                if(table[possible_move] !== 'nothing' && table[possible_move].side === 'black' && 
                        (table[possible_move].type === 'rook' || table[possible_move].type === 'queen') ){
                    return true;
                }
                
                if(table[possible_move] !== 'nothing'){
                    break;
                }

                possible_move = chr(possible_move[0],direction[0])+chr(possible_move[1],direction[1]);

            }
        }
        
        
        if(p[1] < '7'){
            
            var left = table[chr(p[0],-1)+(+p[1]+1)];
            
            if(p[0] !== 'a' && left !== 'nothing' && left.side === 'black' && left.type === 'pawn'){
                return true;
            }
            
            var right = table[chr(p[0],1)+(+p[1]+1)];
            
            if(p[0] !== 'h' && right !== 'nothing' && right.side === 'black' && right.type === 'pawn'){
                return true;
            }
            
        }
        
        
    }
    else if(side === 'black'){
        
        var p = black_king;
        
        var possible_moves = [chr(p[0],1)+chr(p[1],2),
                              chr(p[0],2)+chr(p[1],1),
                              chr(p[0],2)+chr(p[1],-1),
                              chr(p[0],1)+chr(p[1],-2),
                              chr(p[0],-1)+chr(p[1],-2),
                              chr(p[0],-2)+chr(p[1],-1),
                              chr(p[0],-2)+chr(p[1],1),
                              chr(p[0],-1)+chr(p[1],2)];

        var index, possible_move;
        for(index in possible_moves){
            possible_move = possible_moves[index];

            if(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                
                if(table[possible_move] !== 'nothing' && table[possible_move].side === 'white' && 
                        table[possible_move].type === 'knight'){
                    return true;
                }
            }
        }
        
        
        possible_moves = [chr(p[0],1)+chr(p[1],1),
                              chr(p[0],1)+chr(p[1],0),
                              chr(p[0],1)+chr(p[1],-1),
                              chr(p[0],0)+chr(p[1],-1),
                              chr(p[0],0)+chr(p[1],1),
                              chr(p[0],-1)+chr(p[1],-1),
                              chr(p[0],-1)+chr(p[1],0),
                              chr(p[0],-1)+chr(p[1],1)];
                          
        for(index in possible_moves){
            possible_move = possible_moves[index];

            if(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                
                if(table[possible_move] !== 'nothing' && table[possible_move].side === 'white' && 
                        table[possible_move].type === 'king'){
                    return true;
                }
            }
        }
        
        
        var direction, directions = [[1, 1], [1, -1], [-1, -1], [-1, 1]];
        for(index in directions){
            direction = directions[index];

            possible_move = chr(p[0],direction[0])+chr(p[1],direction[1]);
            while(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){

                if(table[possible_move] !== 'nothing' && table[possible_move].side === 'white' && 
                        (table[possible_move].type === 'bishop' || table[possible_move].type === 'queen') ){
                    return true;
                }
                
                if(table[possible_move] !== 'nothing'){
                    break;
                }

                possible_move = chr(possible_move[0],direction[0])+chr(possible_move[1],direction[1]);

            }
        }
        
        
        directions = [[1, 0], [0, 1], [-1, 0], [0, -1]];
        for(index in directions){
            direction = directions[index];

            possible_move = chr(p[0],direction[0])+chr(p[1],direction[1]);
            while(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){

                if(table[possible_move] !== 'nothing' && table[possible_move].side === 'white' && 
                        (table[possible_move].type === 'rook' || table[possible_move].type === 'queen') ){
                    return true;
                }
                
                if(table[possible_move] !== 'nothing'){
                    break;
                }

                possible_move = chr(possible_move[0],direction[0])+chr(possible_move[1],direction[1]);

            }
        }
        
        
        if(p[1] > '2'){
            
            var left = table[chr(p[0],-1)+(+p[1]-1)];
            
            if(p[0] !== 'a' && left !== 'nothing' && left.side === 'white' && left.type === 'pawn'){
                return true;
            }
            
            var right = table[chr(p[0],1)+(+p[1]-1)];
            
            if(p[0] !== 'h' && right !== 'nothing' && right.side === 'white' && right.type === 'pawn'){
                return true;
            }
            
        }
        
    }
    
    return false;
}

function make_move(move){
    
    if(move.target === 'king'){
        
        if(side_to_move === 'white'){
            
            if(move.castle_kingside){

                table.g1 = table.e1;
                table.e1 = 'nothing';
                
                table.f1 = table.h1;
                table.h1 = 'nothing';
                
                white_king = 'g1';
                moves_history.push({target: 'king', from: 'e1', to: 'g1', castle_kingside: true, 
                                    castle_queenside: false, capture: false, notation: '0-0'+(in_check('black')?'+':'')});
                side_to_move = 'black';
                
                table.g1.moves++;
                table.f1.moves++;

            }
            else if(move.castle_queenside){
                
                table.c1 = table.e1;
                table.e1 = 'nothing';
                
                table.d1 = table.a1;
                table.a1 = 'nothing';
                
                white_king = 'c1';
                moves_history.push({target: 'king', from: 'e1', to: 'c1', castle_kingside: false, 
                                    castle_queenside: true, capture: false, notation: '0-0-0'+(in_check('black')?'+':'')});
                side_to_move = 'black';
                
                table.c1.moves++;
                table.d1.moves++;
                
            }
            else{
                
                var elem_history = {target: 'king', from: move.from, to: move.to, castle_kingside: false, 
                    castle_queenside: false, capture: move.capture, notation: 'K'+(move.capture?'x':'')+move.to};
                
                if(move.capture){
                    elem_history.captured = table[move.to];
                }
                
                table[move.to] = table[move.from];
                table[move.from] = 'nothing';
                
                white_king = move.to;

                if(in_check('black')){
                    elem_history.notation += '+';
                }

                moves_history.push(elem_history);
                side_to_move = 'black';
                
                table[move.to].moves++;
                
            }
            
        }
        else if(side_to_move === 'black'){
            
            if(move.castle_kingside){

                table.g8 = table.e8;
                table.e8 = 'nothing';
                
                table.f8 = table.h8;
                table.h8 = 'nothing';
                
                black_king = 'g8';
                moves_history.push({target: 'king', from: 'e8', to: 'g8', castle_kingside: true, 
                    castle_queenside: false, capture: false, notation: '0-0'+(in_check('white')?'+':'')});
                side_to_move = 'white';
                
                table.g8.moves++;
                table.f8.moves++;

            }
            else if(move.castle_queenside){
                
                table.c8 = table.e8;
                table.e8 = 'nothing';
                
                table.d8 = table.a8;
                table.a8 = 'nothing';
                
                black_king = 'c8';
                moves_history.push({target: 'king', from: 'e8', to: 'c8', castle_kingside: false, 
                    castle_queenside: true, capture: false, notation: '0-0-0'+(in_check('white')?'+':'')});
                side_to_move = 'white';
                
                table.c8.moves++;
                table.d8.moves++;
                
            }
            else{
                
                var elem_history = {target: 'king', from: move.from, to: move.to, castle_kingside: false, 
                    castle_queenside: false, capture: move.capture, notation: 'K'+(move.capture?'x':'')+move.to};
                
                if(move.capture){
                    elem_history.captured = table[move.to];
                }
                
                table[move.to] = table[move.from];
                table[move.from] = 'nothing';
                
                black_king = move.to;

                if(in_check('white')){
                    elem_history.notation += '+';
                }

                moves_history.push(elem_history);
                side_to_move = 'white';
                
                table[move.to].moves++;
                
            }
            
        }
        
    }
    
    else if(move.target === 'pawn' && move.en_passant){
        
        var pawn_object;

        if(side_to_move === 'white'){

            pawn_object = table[move.to[0]+chr(move.to[1], -1)];
            table[move.to[0]+chr(move.to[1], -1)] = 'nothing';
            table[move.to] = table[move.from];
            table[move.from] = 'nothing';
            
            moves_history.push({target: 'pawn', from: move.from, to: move.to, capture: true, en_passant: true, captured: pawn_object,
                                notation: move.from[0]+'x'+move.to+(in_check('black')?'+':'')});
            side_to_move = 'black';
            
            table[move.to].moves++;

        }
        else if(side_to_move === 'black'){

            pawn_object = table[move.to[0]+chr(move.to[1], 1)];
            table[move.to[0]+chr(move.to[1], 1)] = 'nothing';
            table[move.to] = table[move.from];
            table[move.from] = 'nothing';
            
            moves_history.push({target: 'pawn', from: move.from, to: move.to, capture: true, en_passant: true, captured: pawn_object,
                                notation: move.from[0]+'x'+move.to+(in_check('white')?'+':'')});
            side_to_move = 'white';
            
            table[move.to].moves++;

        }

    }
    
    else if(move.target === 'pawn' && move.promotion){
        
        var elem_history = {target: move.target, from: move.from, to: move.to, capture: move.capture, en_passant: false, promotion: true, 
            new_figure: move.new_figure, notation: (move.capture?move.from[0]+'x':'')+move.to+(move.new_figure === 'queen'?'Q':
                move.new_figure === 'knight'?'N':move.new_figure === 'bishop'?'B':'R')};

        if(move.capture){
            elem_history.captured = table[move.to];
        }

        table[move.to] = table[move.from];
        table[move.to].type = move.new_figure;
        table[move.from] = 'nothing';

        if(in_check(side_to_move === 'black'? 'white': 'black')){
            move.notation += '+';
        }

        moves_history.push(elem_history);
        side_to_move = side_to_move === 'black'? 'white': 'black';

        table[move.to].moves++;

    }
    
    else{
        
        var elem_history = {target: move.target, from: move.from, to: move.to, capture: move.capture};

        if(move.target === 'pawn'){
            elem_history.en_passant = false;
            elem_history.promotion = false;
        }

        if(move.capture){
            elem_history.captured = table[move.to];
        }

        table[move.to] = table[move.from];
        table[move.from] = 'nothing';

        if(move.target === 'pawn'){
            elem_history.notation = (move.capture?move.from[0]+'x':'')+move.to+(in_check(side_to_move === 'black'? 'white': 'black')?'+':'');
        }

        else{

            if(move.target === 'knight'){

                elem_history.notation = 'N';

                var p = move.to;

                var possible_moves = [chr(p[0],1)+chr(p[1],2),
                                      chr(p[0],2)+chr(p[1],1),
                                      chr(p[0],2)+chr(p[1],-1),
                                      chr(p[0],1)+chr(p[1],-2),
                                      chr(p[0],-1)+chr(p[1],-2),
                                      chr(p[0],-2)+chr(p[1],-1),
                                      chr(p[0],-2)+chr(p[1],1),
                                      chr(p[0],-1)+chr(p[1],2)];
                
                var index, possible_move, number_inaccuracy = false, file_inaccuracy = false, any_inaccuracy = false;
                for(index in possible_moves){
                    possible_move = possible_moves[index];
                    
                    if(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                        
                        if(table[possible_move] !== 'nothing' && table[possible_move].side === side_to_move && table[possible_move].type === 'knight'){
                            any_inaccuracy = true;
                            if(possible_move[0] === move.from[0]){
                                file_inaccuracy = true;
                            }
                            if(possible_move[1] === move.from[1]){
                                number_inaccuracy = true;
                            }
                        }
                        
                    }
                }

            }

            else if(move.target === 'bishop'){

                elem_history.notation = 'B';

                var p = move.to;

                var direction, possible_move, directions = [[1, 1], [1, -1], [-1, -1], [-1, 1]];
                var number_inaccuracy = false, file_inaccuracy = false, any_inaccuracy = false;
                for(index in directions){
                    direction = directions[index];
                    
                    possible_move = chr(p[0],direction[0])+chr(p[1],direction[1]);
                    while(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){

                        if(possible_move === move.from){
                            break;
                        }
                        
                        if(table[possible_move] !== 'nothing'){
                            if(table[possible_move].side === side_to_move && table[possible_move].type === 'bishop'){
                                any_inaccuracy = true;
                                if(possible_move[0] === move.from[0]){
                                    file_inaccuracy = true;
                                }
                                if(possible_move[1] === move.from[1]){
                                    number_inaccuracy = true;
                                }
                            }
                            break;
                        }
                        
                        possible_move = chr(possible_move[0],direction[0])+chr(possible_move[1],direction[1]);
                        
                    }
                }

            }

            else if(move.target === 'rook'){

                elem_history.notation = 'R';

                var p = move.to;

                var direction, possible_move, directions = [[1, 0], [0, 1], [-1, 0], [0, -1]];
                var number_inaccuracy = false, file_inaccuracy = false, any_inaccuracy = false;
                for(index in directions){
                    direction = directions[index];
                    
                    possible_move = chr(p[0],direction[0])+chr(p[1],direction[1]);
                    while(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                        
                        if(possible_move === move.from){
                            break;
                        }
                        
                        if(table[possible_move] !== 'nothing'){
                            if(table[possible_move].side === side_to_move && table[possible_move].type === 'rook'){
                                any_inaccuracy = true;
                                if(possible_move[0] === move.from[0]){
                                    file_inaccuracy = true;
                                }
                                if(possible_move[1] === move.from[1]){
                                    number_inaccuracy = true;
                                }
                            }
                            break;
                        }
                        
                        possible_move = chr(possible_move[0],direction[0])+chr(possible_move[1],direction[1]);
                        
                    }
                }

            }

            else if(move.target === 'queen'){

                elem_history.notation = 'Q';

                var p = move.to;
                        
                var direction, possible_move, directions = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, -1], [-1, 1]];
                var number_inaccuracy = false, file_inaccuracy = false, any_inaccuracy = false;
                for(index in directions){
                    direction = directions[index];
                    
                    possible_move = chr(p[0],direction[0])+chr(p[1],direction[1]);
                    while(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                        
                        if(possible_move === move.from){
                            break;
                        }
                        
                        if(table[possible_move] !== 'nothing'){
                            if(table[possible_move].side === side_to_move && table[possible_move].type === 'queen'){
                                any_inaccuracy = true;
                                if(possible_move[0] === move.from[0]){
                                    file_inaccuracy = true;
                                }
                                if(possible_move[1] === move.from[1]){
                                    number_inaccuracy = true;
                                }
                            }
                            break;
                        }
                        
                        possible_move = chr(possible_move[0],direction[0])+chr(possible_move[1],direction[1]);
                        
                    }
                }

            }

            if(any_inaccuracy){

                if(file_inaccuracy === false && number_inaccuracy === false){
                    number_inaccuracy = true;
                }

                elem_history.notation += (number_inaccuracy? move.from[0]: '') + (file_inaccuracy? move.from[1]: '');

            }

            elem_history.notation += (move.capture? 'x': '') + move.to + (in_check(side_to_move === 'black'? 'white': 'black')?'+':'');

        }

        moves_history.push(elem_history);
        side_to_move = side_to_move === 'black'? 'white': 'black';

        table[move.to].moves++;
        
    }
    
    
    var curr_str = '', t, index = 0, in_a_row = 0;
    for(var i in table){
        t = table[i];
        if(t !== 'nothing'){

            if(in_a_row){
                curr_str += in_a_row;
                in_a_row = 0;
            }
            
            if(t.side === 'white'){
                curr_str += t.type === 'knight'? 'N': chr(t.type, -32);
            }
            else{
                curr_str += (t.type === 'knight'? 'n': t.type[0]);
            }
            
        }
        else{
            in_a_row += 1;
        }

        index += 1;
        if(index % 8 === 0){
            if(in_a_row){
                curr_str += in_a_row;
                in_a_row = 0;
            }
            if(index !== 64){
                curr_str += '/';
            }

        }
    }

    curr_str += ' ' + side_to_move[0] + ' ';

    curr_str += ((table.e1 !== 'nothing' && table.e1.moves === 0 && table.h1 !== 'nothing' && table.h1.moves === 0 ? 'K' : '') +
                 (table.e1 !== 'nothing' && table.e1.moves === 0 && table.a1 !== 'nothing' && table.a1.moves === 0 ? 'Q' : '') +
                 (table.e8 !== 'nothing' && table.e8.moves === 0 && table.h8 !== 'nothing' && table.h8.moves === 0 ? 'k' : '') +
                 (table.e8 !== 'nothing' && table.e8.moves === 0 && table.a8 !== 'nothing' && table.a8.moves === 0 ? 'q' : '')) || '-';

    curr_str += ' ';
    candidate_en_passant = '-';

    if(move.target === 'pawn' && Math.abs(move.from[1]-move.to[1]) === 2){
        if(move.to[0] !== 'a'){
            left_square = chr(move.to[0], -1) + move.to[1];
            if(table[left_square] !== 'nothing' && table[left_square].type === 'pawn'){
                candidate_en_passant = move.to[0] + (move.to[1] === '5' ? '6' : '3');
            }
        }
        if(move.to[0] !== 'h'){
            right_square = chr(move.to[0], 1) + move.to[1];

            if(table[right_square] !== 'nothing' && table[right_square].type === 'pawn'){
                candidate_en_passant = move.to[0] + (move.to[1] === '5' ? '6' : '3');
            }
        }
    }

    curr_str += candidate_en_passant;
    
    table_history.push(curr_str);
    
    return curr_str;
    
}

function unmake_move(){
    
    var move = moves_history.pop();
    table_history.pop();
    side_to_move = side_to_move === 'black'? 'white': 'black';
    
    if(move.target === 'king'){
        
        if(side_to_move === 'white'){
            
            if(move.castle_kingside){
                
                table.f1.moves--;
                table.g1.moves--;
                
                white_king = 'e1';
                
                table.h1 = table.f1;
                table.f1 = 'nothing';

                table.e1 = table.g1;
                table.g1 = 'nothing';
                
                return move;

            }
            else if(move.castle_queenside){
                
                table.c1.moves--;
                table.d1.moves--;
                
                white_king = 'e1';
                
                table.a1 = table.d1;
                table.d1 = 'nothing';
                
                table.e1 = table.c1;
                table.c1 = 'nothing';
                
                return move;
                
            }
            else{
                
                table[move.to].moves--;
                
                white_king = move.from;
                
                table[move.from] = table[move.to];
                table[move.to] = 'nothing';
                
                if(move.capture){
                    table[move.to] = move.captured;
                }
                
                return move;
                
            }
            
        }
        else if(side_to_move === 'black'){
            
            if(move.castle_kingside){
                
                table.g8.moves--;
                table.f8.moves--;
                
                black_king = 'e8';
                
                table.h8 = table.f8;
                table.f8 = 'nothing';

                table.e8 = table.g8;
                table.g8 = 'nothing';
                
                return move;

            }
            else if(move.castle_queenside){
                
                table.c8.moves--;
                table.d8.moves--;
                
                black_king = 'e8';
                
                table.a8 = table.d8;
                table.d8 = 'nothing';
                
                table.e8 = table.c8;
                table.c8 = 'nothing';
                
                return move;
                
            }
            else{
                
                table[move.to].moves--;
                
                black_king = move.from;
                
                table[move.from] = table[move.to];
                table[move.to] = 'nothing';
                
                if(move.capture){
                    table[move.to] = move.captured;
                }
                
                return move;
                
            }
            
        }
        
    }
    
    if(move.target === 'pawn' && move.en_passant){

        if(side_to_move === 'white'){
            
            table[move.to].moves--;
            
            table[move.to[0]+chr(move.to[1], -1)] = move.captured;
            table[move.from] = table[move.to];
            table[move.to] = 'nothing';

            return move;

        }
        else if(side_to_move === 'black'){
            
            table[move.to].moves--;

            table[move.to[0]+chr(move.to[1], 1)] = move.captured;
            table[move.from] = table[move.to];
            table[move.to] = 'nothing';
            
            return move;

        }

    }
    
    if(move.target === 'pawn' && move.promotion){
        
        table[move.to].moves--;
        
        table[move.from] = table[move.to];
        table[move.from].type = 'pawn';
        table[move.to] = 'nothing';

        if(move.capture){
            table[move.to] = move.captured;
        }
        
        return move;

    }
    
    table[move.to].moves--;
    
    table[move.from] = table[move.to];
    table[move.to] = 'nothing';
    
    if(move.capture){
        table[move.to] = move.captured;
    }
    
    return move;
}

function get_moves(side){
    
    var p, curr_moves, figure;
    
    var moves = {};
    
    for(p in table){
        figure = table[p];
        if(figure !== 'nothing' && figure.side === side){
            curr_moves = moves[p] = [];
            
            
            if(side === 'white'){
                
                
                if(figure.type === 'pawn'){
                    
                    
                    if(table[p[0]+(+p[1]+1)] === 'nothing'){
                        curr_moves.push({to: p[0]+(+p[1]+1), from: p, target: 'pawn', capture: false, 
                            en_passant: false, promotion: false});
                        if(p[1] === '2' && table[p[0]+'4'] === 'nothing'){
                            curr_moves.push({to: p[0]+'4', from: p, target: 'pawn', capture: false, 
                                en_passant: false, promotion: false});
                        }
                    }
                    
                    var l = chr(p,-1)+(+p[1]+1);
                    var r = chr(p, 1)+(+p[1]+1);
                    
                    if(p[0] !== 'a' && table[l] !== 'nothing' && table[l].side === 'black'){
                        curr_moves.push({to: l, from: p, target: 'pawn', capture: true, 
                            en_passant: false, promotion: false});
                    }
                    if(p[0] !== 'h' && table[r] !== 'nothing' && table[r].side === 'black'){
                        curr_moves.push({to: r, from: p, target: 'pawn', capture: true, 
                            en_passant: false, promotion: false});
                    }
                    
                    if(moves_history.length > 0){
                        last_move = moves_history[moves_history.length - 1];

                        if(p[0] !== 'a' && p[1] === '5' && last_move.target === 'pawn'
                                && last_move.from[1] - last_move.to[1] === 2 && last_move.from[0] === l[0]){
                            curr_moves.push({to: l, from: p, target: 'pawn', capture: true, 
                                en_passant: true, promotion: false});
                        }
                        
                        if(p[0] !== 'h' && p[1] === '5' && last_move.target === 'pawn'
                                && last_move.from[1] - last_move.to[1] === 2 && last_move.from[0] === r[0]){
                            curr_moves.push({to: r, from: p, target: 'pawn', capture: true, 
                                en_passant: true, promotion: false});
                        }
                        
                    }
                    
                    
                    if(p[1] === '7' && curr_moves.length > 0){
                        
                        var new_moves = [], new_move;
                        
                        var index, move;
                        for(index in curr_moves){
                            move = curr_moves[index];
                            move.promotion = true;
                            
                            new_move = clone(move);
                            new_move.new_figure = 'queen';
                            new_moves.push(new_move);
                            
                            new_move = clone(move);
                            new_move.new_figure = 'knight';
                            new_moves.push(new_move);
                            
                            new_move = clone(move);
                            new_move.new_figure = 'bishop';
                            new_moves.push(new_move);
                            
                            new_move = clone(move);
                            new_move.new_figure = 'rook';
                            new_moves.push(new_move);
                            
                        }
                        
                        moves[p] = new_moves;
                        
                    }
                    
                    
                }
                
                
                else if(figure.type === 'knight'){
                    
                    
                    var possible_moves = [chr(p[0],1)+chr(p[1],2),
                                          chr(p[0],2)+chr(p[1],1),
                                          chr(p[0],2)+chr(p[1],-1),
                                          chr(p[0],1)+chr(p[1],-2),
                                          chr(p[0],-1)+chr(p[1],-2),
                                          chr(p[0],-2)+chr(p[1],-1),
                                          chr(p[0],-2)+chr(p[1],1),
                                          chr(p[0],-1)+chr(p[1],2)];
                    
                    var index, possible_move;
                    for(index in possible_moves){
                        possible_move = possible_moves[index];
                        
                        if(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                            
                            if(table[possible_move] === 'nothing'){
                                curr_moves.push({to: possible_move, from: p, target: 'knight', capture: false});
                            }
                            else if(table[possible_move].side === 'black'){
                                curr_moves.push({to: possible_move, from: p, target: 'knight', capture: true});
                            }
                            
                        }
                    }
                    
                    
                }
                
                
                
                else if(figure.type === 'bishop'){
                    
                    var direction, possible_move, directions = [[1, 1], [1, -1], [-1, -1], [-1, 1]];
                    for(index in directions){
                        direction = directions[index];
                        
                        possible_move = chr(p[0],direction[0])+chr(p[1],direction[1]);
                        while(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                            
                            if(table[possible_move] === 'nothing'){
                                curr_moves.push({to: possible_move, from: p, target: 'bishop', capture: false});
                            }
                            else if(table[possible_move].side === 'black'){
                                curr_moves.push({to: possible_move, from: p, target: 'bishop', capture: true});
                                break;
                            }
                            else if(table[possible_move].side === 'white'){
                                break;
                            }
                            
                            possible_move = chr(possible_move[0],direction[0])+chr(possible_move[1],direction[1]);
                            
                        }
                    }
                    
                    
                }
                
                
                else if(figure.type === 'rook'){
                    
                    var direction, possible_move, directions = [[1, 0], [0, 1], [-1, 0], [0, -1]];
                    for(index in directions){
                        direction = directions[index];
                        
                        possible_move = chr(p[0],direction[0])+chr(p[1],direction[1]);
                        while(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                            
                            if(table[possible_move] === 'nothing'){
                                curr_moves.push({to: possible_move, from: p, target: 'rook', capture: false});
                            }
                            else if(table[possible_move].side === 'black'){
                                curr_moves.push({to: possible_move, from: p, target: 'rook', capture: true});
                                break;
                            }
                            else if(table[possible_move].side === 'white'){
                                break;
                            }
                            
                            possible_move = chr(possible_move[0],direction[0])+chr(possible_move[1],direction[1]);
                            
                        }
                    }
                    
                    
                }
                
                
                
                else if(figure.type === 'queen'){
                    
                    var direction, possible_move, directions = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, -1], [-1, 1]];
                    for(index in directions){
                        direction = directions[index];
                        
                        possible_move = chr(p[0],direction[0])+chr(p[1],direction[1]);
                        while(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                            
                            if(table[possible_move] === 'nothing'){
                                curr_moves.push({to: possible_move, from: p, target: 'queen', capture: false});
                            }
                            else if(table[possible_move].side === 'black'){
                                curr_moves.push({to: possible_move, from: p, target: 'queen', capture: true});
                                break;
                            }
                            else if(table[possible_move].side === 'white'){
                                break;
                            }
                            
                            possible_move = chr(possible_move[0],direction[0])+chr(possible_move[1],direction[1]);
                            
                        }
                    }
                    
                    
                }
                
                
                else if(figure.type === 'king'){
                    
                    var direction, possible_move, directions = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, -1], [-1, 1]];
                    for(index in directions){
                        direction = directions[index];
                        
                        possible_move = chr(p[0],direction[0])+chr(p[1],direction[1]);
                        
                        if(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                            if(table[possible_move] === 'nothing'){
                                curr_moves.push({to: possible_move, from: p, target: 'king', capture: false, 
                                    castle_kingside: false, castle_queenside: false});
                            }
                            else if(table[possible_move].side === 'black'){
                                curr_moves.push({to: possible_move, from: p, target: 'king', capture: true, 
                                    castle_kingside: false, castle_queenside: false});
                            }
                        }
                    }
                    
                    
                    if(figure.moves === 0){
                        
                        if(table.h1 !== 'nothing' && table.h1.moves === 0 && 
                                table.f1 === 'nothing' && table.g1 === 'nothing'){
                            curr_moves.push({to: 'g1', from: p, target: 'king', capture: false, castle_kingside: true, castle_queenside: false});
                        }
                        
                        if(table.a1 !== 'nothing' && table.a1.moves === 0 && 
                                table.b1 === 'nothing' && table.c1 === 'nothing' && table.d1 === 'nothing'){
                            curr_moves.push({to: 'c1', from: p, target: 'king', capture: false, castle_kingside: false, castle_queenside: true});
                        }
                        
                    }
                    
                }
                
                
            }
            else if(side === 'black'){
                
                
                if(figure.type === 'pawn'){
                    
                    
                    if(table[p[0]+(+p[1]-1)] === 'nothing'){
                        curr_moves.push({to: p[0]+(+p[1]-1), from: p, target: 'pawn', capture: false, 
                            en_passant: false, promotion: false});
                        if(p[1] === '7' && table[p[0]+'5'] === 'nothing'){
                            curr_moves.push({to: p[0]+'5', from: p, target: 'pawn', capture: false, 
                                en_passant: false, promotion: false});
                        }
                    }
                    
                    var l = chr(p,-1)+(+p[1]-1);
                    var r = chr(p, 1)+(+p[1]-1);
                    
                    if(p[0] !== 'a' && table[l] !== 'nothing' && table[l].side === 'white'){
                        curr_moves.push({to: l, from: p, target: 'pawn', capture: true, 
                            en_passant: false, promotion: false});
                    }
                    if(p[0] !== 'h' && table[r] !== 'nothing' && table[r].side === 'white'){
                        curr_moves.push({to: r, from: p, target: 'pawn', capture: true, 
                            en_passant: false, promotion: false});
                    }
                    
                    if(moves_history.length > 0){
                        last_move = moves_history[moves_history.length - 1];

                        if(p[0] !== 'a' && p[1] === '4' && last_move.target === 'pawn'
                                && last_move.to[1] - last_move.from[1] === 2 && last_move.from[0] === l[0]){
                            curr_moves.push({to: l, from: p, target: 'pawn', capture: true, 
                                en_passant: true, promotion: false});
                        }
                        
                        if(p[0] !== 'h' && p[1] === '4' && last_move.target === 'pawn'
                                && last_move.to[1] - last_move.from[1] === 2 && last_move.from[0] === r[0]){
                            curr_moves.push({to: r, from: p, target: 'pawn', capture: true, 
                                en_passant: true, promotion: false});
                        }
                        
                    }
                    
                    if(p[1] === '2' && curr_moves.length > 0){
                        
                        var new_moves = [], new_move;
                        
                        var index, move;
                        for(index in curr_moves){
                            move = curr_moves[index];
                            move.promotion = true;
                            
                            new_move = clone(move);
                            new_move.new_figure = 'queen';
                            new_moves.push(new_move);
                            
                            new_move = clone(move);
                            new_move.new_figure = 'knight';
                            new_moves.push(new_move);
                            
                            new_move = clone(move);
                            new_move.new_figure = 'bishop';
                            new_moves.push(new_move);
                            
                            new_move = clone(move);
                            new_move.new_figure = 'rook';
                            new_moves.push(new_move);
                            
                        }
                        
                        moves[p] = new_moves;
                        
                    }
                    
                    
                }
                
                
                else if(figure.type === 'knight'){
                    
                    
                    var possible_moves = [chr(p[0],1)+chr(p[1],2),
                                          chr(p[0],2)+chr(p[1],1),
                                          chr(p[0],2)+chr(p[1],-1),
                                          chr(p[0],1)+chr(p[1],-2),
                                          chr(p[0],-1)+chr(p[1],-2),
                                          chr(p[0],-2)+chr(p[1],-1),
                                          chr(p[0],-2)+chr(p[1],1),
                                          chr(p[0],-1)+chr(p[1],2)];
                    
                    var index, possible_move;
                    for(index in possible_moves){
                        possible_move = possible_moves[index];
                        
                        if(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                            
                            if(table[possible_move] === 'nothing'){
                                curr_moves.push({to: possible_move, from: p, target: 'knight', capture: false});
                            }
                            else if(table[possible_move].side === 'white'){
                                curr_moves.push({to: possible_move, from: p, target: 'knight', capture: true});
                            }
                            
                        }
                    }
                    
                    
                }
                
                
                else if(figure.type === 'bishop'){
                    
                    var direction, possible_move, directions = [[1, 1], [1, -1], [-1, -1], [-1, 1]];
                    for(index in directions){
                        direction = directions[index];
                        
                        possible_move = chr(p[0],direction[0])+chr(p[1],direction[1]);
                        while(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                            
                            if(table[possible_move] === 'nothing'){
                                curr_moves.push({to: possible_move, from: p, target: 'bishop', capture: false});
                            }
                            else if(table[possible_move].side === 'white'){
                                curr_moves.push({to: possible_move, from: p, target: 'bishop', capture: true});
                                break;
                            }
                            else if(table[possible_move].side === 'black'){
                                break;
                            }
                            
                            possible_move = chr(possible_move[0],direction[0])+chr(possible_move[1],direction[1]);
                            
                        }
                    }
                    
                    
                }
                
                
                else if(figure.type === 'rook'){
                    
                    var direction, possible_move, directions = [[1, 0], [0, 1], [-1, 0], [0, -1]];
                    for(index in directions){
                        direction = directions[index];
                        
                        possible_move = chr(p[0],direction[0])+chr(p[1],direction[1]);
                        while(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                            
                            if(table[possible_move] === 'nothing'){
                                curr_moves.push({to: possible_move, from: p, target: 'rook', capture: false});
                            }
                            else if(table[possible_move].side === 'white'){
                                curr_moves.push({to: possible_move, from: p, target: 'rook', capture: true});
                                break;
                            }
                            else if(table[possible_move].side === 'black'){
                                break;
                            }
                            
                            possible_move = chr(possible_move[0],direction[0])+chr(possible_move[1],direction[1]);
                            
                        }
                    }
                    
                    
                }
                
                
                else if(figure.type === 'queen'){
                    
                    var direction, possible_move, directions = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, -1], [-1, 1]];
                    for(index in directions){
                        direction = directions[index];
                        
                        possible_move = chr(p[0],direction[0])+chr(p[1],direction[1]);
                        while(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                            
                            if(table[possible_move] === 'nothing'){
                                curr_moves.push({to: possible_move, from: p, target: 'queen', capture: false});
                            }
                            else if(table[possible_move].side === 'white'){
                                curr_moves.push({to: possible_move, from: p, target: 'queen', capture: true});
                                break;
                            }
                            else if(table[possible_move].side === 'black'){
                                break;
                            }
                            
                            possible_move = chr(possible_move[0],direction[0])+chr(possible_move[1],direction[1]);
                            
                        }
                    }
                    
                    
                }
                
                
                else if(figure.type === 'king'){
                    
                    var direction, possible_move, directions = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, -1], [-1, 1]];
                    for(index in directions){
                        direction = directions[index];
                        
                        possible_move = chr(p[0],direction[0])+chr(p[1],direction[1]);
                        
                        if(possible_move[0] >= 'a' && possible_move[0] <= 'h' && possible_move[1] >= '1' && possible_move[1] <= '8'){
                            if(table[possible_move] === 'nothing'){
                                curr_moves.push({to: possible_move, from: p, target: 'king', capture: false, 
                                    castle_kingside: false, castle_queenside: false});
                            }
                            else if(table[possible_move].side === 'white'){
                                curr_moves.push({to: possible_move, from: p, target: 'king', capture: true, 
                                    castle_kingside: false, castle_queenside: false});
                            }
                        }
                    }
                    
                    
                    if(figure.moves === 0){
                        
                        if(table.h8 !== 'nothing' && table.h8.moves === 0 && 
                                table.f8 === 'nothing' && table.g8 === 'nothing'){
                            curr_moves.push({to: 'g8', from: p, target: 'king', capture: false, castle_kingside: true, castle_queenside: false});
                        }
                        
                        if(table.a8 !== 'nothing' && table.a8.moves === 0 && 
                                table.b8 === 'nothing' && table.c8 === 'nothing' && table.d8 === 'nothing'){
                            curr_moves.push({to: 'c8', from: p, target: 'king', capture: false, castle_kingside: false, castle_queenside: true});
                        }
                        
                    }
                    
                }
                
                
            }
        }
        
    }
    
    
    
    var curr_pos, move, curr_index, to_index;
    for(curr_index in moves){
        curr_pos = moves[curr_index];
        
        
        
        for(to_index = curr_pos.length - 1; to_index >= 0; to_index-- ){
            move = curr_pos[to_index];
            
            if(move.target === 'king'){
                
                var cannot_castle;
                
                if(side === 'white'){
                    if(move.castle_kingside){
                        
                        cannot_castle = in_check('white');
                        
                        table.f1 = table.e1;
                        table.e1 = 'nothing';
                        white_king = 'f1';
                        
                        cannot_castle = cannot_castle || in_check('white');
                        
                        table.g1 = table.f1;
                        table.f1 = 'nothing';
                        white_king = 'g1';
                        
                        cannot_castle = cannot_castle || in_check('white');
                        
                        table.e1 = table.g1;
                        table.g1 = 'nothing';
                        white_king = 'e1';
                        
                        if(cannot_castle){
                            curr_pos.splice(to_index, 1);
                        }
                        continue;
                        
                    }
                    else if(move.castle_queenside){
                        
                        cannot_castle = in_check('white');
                        
                        table.d1 = table.e1;
                        table.e1 = 'nothing';
                        white_king = 'd1';
                        
                        cannot_castle = cannot_castle || in_check('white');
                        
                        table.c1 = table.d1;
                        table.d1 = 'nothing';
                        white_king = 'c1';
                        
                        cannot_castle = cannot_castle || in_check('white');
                        
                        table.e1 = table.c1;
                        table.c1 = 'nothing';
                        white_king = 'e1';
                        
                        if(cannot_castle){
                            curr_pos.splice(to_index, 1);
                        }
                        continue;
                        
                    }
                }
                else if(side === 'black'){
                    if(move.castle_kingside){
                        
                        cannot_castle = in_check('black');
                        
                        table.f8 = table.e8;
                        table.e8 = 'nothing';
                        black_king = 'f8';
                        
                        cannot_castle = cannot_castle || in_check('black');
                        
                        table.g8 = table.f8;
                        table.f8 = 'nothing';
                        black_king = 'g8';
                        
                        cannot_castle = cannot_castle || in_check('black');
                        
                        table.e8 = table.g8;
                        table.g8 = 'nothing';
                        black_king = 'e8';
                        
                        if(cannot_castle){
                            curr_pos.splice(to_index, 1);
                        }
                        continue;
                        
                    }
                    else if(move.castle_queenside){

                        cannot_castle = in_check('black');
                        
                        table.d8 = table.e8;
                        table.e8 = 'nothing';
                        black_king = 'd8';
                        
                        cannot_castle = cannot_castle || in_check('black');
                        
                        table.c8 = table.d8;
                        table.d8 = 'nothing';
                        black_king = 'c8';
                        
                        cannot_castle = cannot_castle || in_check('black');
                        
                        table.e8 = table.c8;
                        table.c8 = 'nothing';
                        black_king = 'e8';
                        
                        if(cannot_castle){
                            curr_pos.splice(to_index, 1);
                        }
                        continue;

                    }
                }
            }
            
            if(move.target === 'pawn' && move.en_passant){
                
                var cannot_en_passant, pawn_object;
                
                if(side === 'white'){
                    
                    pawn_object = table[move.to[0]+chr(move.to[1], -1)];
                    table[move.to[0]+chr(move.to[1], -1)] = 'nothing';
                    table[move.to] = table[move.from];
                    table[move.from] = 'nothing';
                    
                    cannot_en_passant = in_check('white');
                    
                    table[move.from] = table[move.to];
                    table[move.to] = 'nothing';
                    table[move.to[0]+chr(move.to[1], -1)] = pawn_object;
                    
                    if(cannot_en_passant){
                        curr_pos.splice(to_index, 1);
                    }
                    continue;
                    
                }
                else if(side === 'black'){
                    
                    pawn_object = table[move.to[0]+chr(move.to[1], 1)];
                    table[move.to[0]+chr(move.to[1], 1)] = 'nothing';
                    table[move.to] = table[move.from];
                    table[move.from] = 'nothing';
                    
                    cannot_en_passant = in_check('black');
                    
                    table[move.from] = table[move.to];
                    table[move.to] = 'nothing';
                    table[move.to[0]+chr(move.to[1], 1)] = pawn_object;
                    
                    if(cannot_en_passant){
                        curr_pos.splice(to_index, 1);
                    }
                    continue;
                    
                }
                
            }
            
            var save_object = move.capture? table[move.to]: 'nothing';
            
            table[move.to] = table[move.from];
            table[move.from] = 'nothing';
            
            if(move.target === 'king'){
                if(side === 'white'){
                    white_king = move.to;
                }
                else if(side === 'black'){
                    black_king = move.to;
                }
            }
            
            var is_not_correct = in_check(side);
            
            table[move.from] = table[move.to];
            table[move.to] = save_object;
            
            if(move.target === 'king'){
                if(side === 'white'){
                    white_king = move.from;
                }
                else if(side === 'black'){
                    black_king = move.from;
                }
            }
            
            if(is_not_correct){
                curr_pos.splice(to_index, 1);
            }
            
        }
    }
    
    return moves;
    
}

function move_graphic(move){
    
    
    if(promotion_mode){
        
        document.getElementById(move.to).innerHTML = "<img id='"+table[move.to].id+"' class='figure' src='/img/chess/pieces/"+(move.to[1] === '8'? 'w': 'b')+(table[move.to].type === 'knight'? 'n': table[move.to].type[0])+".png' draggable='true' ondragstart='drag(event)'>";
        promotion_mode = false;
        
        if(in_check(side_to_move)){
            if(side_to_move === 'white'){
                document.getElementById(white_king).classList.add('in_check');
            }
            else if(side_to_move === 'black'){
                document.getElementById(black_king).classList.add('in_check');
            }
        }
        
        additional_check();
        
        return;
        
    }
    
    for(var curr_pos in table){
        document.getElementById(curr_pos).classList.remove('last_move');
        document.getElementById(curr_pos).classList.remove('in_check');
    }

    document.getElementById(move.to).classList.add('last_move');
    document.getElementById(move.from).classList.add('last_move');
    
    document.getElementById(move.to).innerHTML = document.getElementById(move.from).innerHTML;
    document.getElementById(move.from).innerHTML = '';
    
    if(move.target === 'king'){
        
        if(move.castle_kingside){
            document.getElementById('f'+move.to[1]).innerHTML = document.getElementById('h'+move.to[1]).innerHTML;
            document.getElementById('h'+move.to[1]).innerHTML = '';
        }
        else if(move.castle_queenside){
            document.getElementById('d'+move.to[1]).innerHTML = document.getElementById('a'+move.to[1]).innerHTML;
            document.getElementById('a'+move.to[1]).innerHTML = '';
        }
        
    }
    else if(move.target === 'pawn' && move.en_passant){
        document.getElementById(move.to[0]+chr(move.to[1], move.to[1] === '6'? -1: 1)).innerHTML = '';
    }
    else if(move.target === 'pawn' && move.promotion){

        if(board_position === 'standart'){
            if(move.to[1] === '8'){
                document.getElementById(move.to).innerHTML += "<div id='q' class='promotion section' onclick=\"choose_new_figure('queen')\" style=\"position:absolute;margin-left: -90px; margin-top: -60px\"><img id='nq' class='figure' src='/img/chess/pieces/wq.png'></div><div id='r' class='promotion section' onclick=\"choose_new_figure('rook')\" style=\"position:absolute;margin-left: -30px; margin-top: -60px\"><img id='nr' class='figure' src='/img/chess/pieces/wr.png'></div><div id='b' class='promotion section' onclick=\"choose_new_figure('bishop')\" style=\"position:absolute;margin-left: 30px; margin-top: -60px\"><img id='nb' class='figure' src='/img/chess/pieces/wb.png'></div><div id='n' class='promotion section' onclick=\"choose_new_figure('knight')\" style=\"position:absolute;margin-left: 90px; margin-top: -60px\"><img id='nn' class='figure' src='/img/chess/pieces/wn.png'></div>";
            }
            else if(move.to[1] === '1'){
                document.getElementById(move.to).innerHTML += "<div id='q' class='promotion section' onclick=\"choose_new_figure('queen')\" style=\"position:absolute;margin-left: -90px; margin-top: 60px\"><img id='nq' class='figure' src='/img/chess/pieces/bq.png'></div><div id='r' class='promotion section' onclick=\"choose_new_figure('rook')\" style=\"position:absolute;margin-left: -30px; margin-top: 60px\"><img id='nr' class='figure' src='/img/chess/pieces/br.png'></div><div id='b' class='promotion section' onclick=\"choose_new_figure('bishop')\" style=\"position:absolute;margin-left: 30px; margin-top: 60px\"><img id='nb' class='figure' src='/img/chess/pieces/bb.png'></div><div id='n' class='promotion section' onclick=\"choose_new_figure('knight')\" style=\"position:absolute;margin-left: 90px; margin-top: 60px\"><img id='nn' class='figure' src='/img/chess/pieces/bn.png'></div>";
            }
        }
        else{
            if(move.to[1] === '8'){
                document.getElementById(move.to).innerHTML += "<div id='q' class='promotion section' onclick=\"choose_new_figure('queen')\" style=\"position:absolute;margin-left: -90px; margin-top: 60px\"><img id='nq' class='figure' src='/img/chess/pieces/wq.png'></div><div id='r' class='promotion section' onclick=\"choose_new_figure('rook')\" style=\"position:absolute;margin-left: -30px; margin-top: 60px\"><img id='nr' class='figure' src='/img/chess/pieces/wr.png'></div><div id='b' class='promotion section' onclick=\"choose_new_figure('bishop')\" style=\"position:absolute;margin-left: 30px; margin-top: 60px\"><img id='nb' class='figure' src='/img/chess/pieces/wb.png'></div><div id='n' class='promotion section' onclick=\"choose_new_figure('knight')\" style=\"position:absolute;margin-left: 90px; margin-top: 60px\"><img id='nn' class='figure' src='/img/chess/pieces/wn.png'></div>";
            }
            else if(move.to[1] === '1'){
                document.getElementById(move.to).innerHTML += "<div id='q' class='promotion section' onclick=\"choose_new_figure('queen')\" style=\"position:absolute;margin-left: -90px; margin-top: -60px\"><img id='nq' class='figure' src='/img/chess/pieces/bq.png'></div><div id='r' class='promotion section' onclick=\"choose_new_figure('rook')\" style=\"position:absolute;margin-left: -30px; margin-top: -60px\"><img id='nr' class='figure' src='/img/chess/pieces/br.png'></div><div id='b' class='promotion section' onclick=\"choose_new_figure('bishop')\" style=\"position:absolute;margin-left: 30px; margin-top: -60px\"><img id='nb' class='figure' src='/img/chess/pieces/bb.png'></div><div id='n' class='promotion section' onclick=\"choose_new_figure('knight')\" style=\"position:absolute;margin-left: 90px; margin-top: -60px\"><img id='nn' class='figure' src='/img/chess/pieces/bn.png'></div>";
            }
        }
        
        promotion_mode = true;
    }
    
    if(in_check(side_to_move)){
        if(side_to_move === 'white'){
            document.getElementById(white_king).classList.add('in_check');
        }
        else if(side_to_move === 'black'){
            document.getElementById(black_king).classList.add('in_check');
        }
    }
    
    if(!promotion_mode){
        additional_check();
    }
    
}

function additional_check(){
    
    var state = check_table();
    
    if(state === 'Checkmate to white'){
        document.getElementById('result').innerHTML = 'Мат белым';
        document.getElementById('result2').innerHTML = '';
        game_over = true;
        game_result = '0 - 1';
    }
    else if(state === 'Checkmate to black'){
        document.getElementById('result').innerHTML = 'Мат чёрным';
        document.getElementById('result2').innerHTML = '';
        game_over = true;
        game_result = '1 - 0';
    }
    else if(state === 'Draw my stalemate'){
        document.getElementById('result').innerHTML = 'Пат. Ничья';
        document.getElementById('result2').innerHTML = '';
        game_over = true;
        game_result = '1/2 - 1/2';
    }
    else if(state === 'Draw by 50 moves rule'){
        document.getElementById('result').innerHTML = 'Ничья по правилу 50-ти ходов';
        document.getElementById('result2').innerHTML = '';
        game_over = true;
        game_result = '1/2 - 1/2';
    }
    else if(state === 'Draw by insufficient material'){
        document.getElementById('result').innerHTML = 'Ничья из-за недостатка фигур';
        document.getElementById('result2').innerHTML = '';
        game_over = true;
        game_result = '1/2 - 1/2';
    }
    else if(state === 'Draw by threefold repetition'){
        document.getElementById('result').innerHTML = 'Ничья. Повтор позиции';
        document.getElementById('result2').innerHTML = '';
        game_over = true;
        game_result = '1/2 - 1/2';
    }

    if(game_over){
        document.getElementById(black_king).classList.remove('in_check');
        document.getElementById(white_king).classList.remove('in_check');
    }

    set_history_of_moves();
    
}

function unmake_move_graphic(move){
    
    
    for(var curr_pos in table){
        document.getElementById(curr_pos).classList.remove('last_move');
        document.getElementById(curr_pos).classList.remove('in_check');
        document.getElementById(curr_pos).classList.remove('chosen');
        document.getElementById(curr_pos).classList.remove('candidate_move');
        document.getElementById(curr_pos).classList.remove('candidate_capture');
    }
    
    document.getElementById(move.from).innerHTML = document.getElementById(move.to).innerHTML;
    document.getElementById(move.to).innerHTML = '';
    
    if(move.target === 'king'){
        if(move.castle_kingside){
            document.getElementById('h'+move.to[1]).innerHTML = document.getElementById('f'+move.to[1]).innerHTML;
            document.getElementById('f'+move.to[1]).innerHTML = '';
        }
        else if(move.castle_queenside){
            document.getElementById('a'+move.to[1]).innerHTML = document.getElementById('d'+move.to[1]).innerHTML;
            document.getElementById('d'+move.to[1]).innerHTML = '';
        }
        else if(move.capture){
            document.getElementById(move.to).innerHTML = "<img id='"+move.captured.id+"' class='figure' src='/img/chess/pieces/"+move.captured.side[0]+(move.captured.type === 'knight'? 'n': move.captured.type[0])+".png' draggable='true' ondragstart='drag(event)'>";
        }
        
    }
    else if(move.target === 'pawn' && move.en_passant){
        document.getElementById(move.to[0]+chr(move.to[1], move.to[1] === '6'? -1: 1)).innerHTML = "<img id='"+move.captured.id+"' class='figure' src='/img/chess/pieces/"+(move.to[1] === '6'? 'b': 'w')+"p.png' draggable='true' ondragstart='drag(event)'>";
    }
    else if(move.target === 'pawn' && move.promotion){
        
        if(move.capture){
            document.getElementById(move.to).innerHTML = "<img id='"+move.captured.id+"' class='figure' src='/img/chess/pieces/"+(move.to[1] === '8'? 'b': 'w')+(move.captured.type === 'knight'? 'n': move.captured.type[0])+".png' draggable='true' ondragstart='drag(event)'>";
        }
        
        document.getElementById(move.from).innerHTML = "<img id='"+table[move.from].id+"' class='figure' src='/img/chess/pieces/"+(move.to[1] === '8'? 'w': 'b')+"p.png' draggable='true' ondragstart='drag(event)'>";
    }
    else if(move.capture){
        document.getElementById(move.to).innerHTML = "<img id='"+move.captured.id+"' class='figure' src='/img/chess/pieces/"+move.captured.side[0]+(move.captured.type === 'knight'? 'n': move.captured.type[0])+".png' draggable='true' ondragstart='drag(event)'>";
    }
    
    
    if(moves_history.length){
        var last_move = moves_history[moves_history.length - 1];
        
        document.getElementById(last_move.to).classList.add('last_move');
        document.getElementById(last_move.from).classList.add('last_move');
    }
    
    if(in_check(side_to_move)){
        if(side_to_move === 'white'){
            document.getElementById(white_king).classList.add('in_check');
        }
        else if(side_to_move === 'black'){
            document.getElementById(black_king).classList.add('in_check');
        }
    }
    game_over = false;
    
    set_history_of_moves();
    additional_check();
    
}

function new_game_button(){
    
    if(!promotion_mode && !dont_touch){
        while(moves_history.length > 0){
            unmake_move_graphic(unmake_move());
        }

        document.getElementById('result').innerHTML = '';
        document.getElementById('new_game').style.display = 'none';

        if(default_depth >= 0){
            dont_touch = true;
            stockfish.postMessage("position fen " + table_history[table_history.length - 1]);
            stockfish.postMessage("go depth 1");
        }
        else{
            var moves = get_moves(side_to_move), moves_all = [];
            for(curr_moves in moves){
                for(curr_move in moves[curr_moves]){
                    moves_all.push(moves[curr_moves][curr_move]);
                }
            }
            var random_move =  moves_all[ Math.random() * moves_all.length | 0 ]
            make_move(random_move);
            move_graphic(random_move);
            if(random_move.promotion){
                move_graphic(random_move);
            }

            if(default_depth_2 >=0){
                setTimeout(function(){
                    stockfish.postMessage("setoption name Skill Level value " + (side_to_move === 'white'? default_depth: default_depth_2))
                    stockfish.postMessage("position fen " + table_history[table_history.length - 1]);
                    stockfish.postMessage("go depth " + ((side_to_move === 'white'? (default_depth <= 10? default_depth: 10 + (default_depth-10)/2|0) 
                        : (default_depth_2 <= 10? default_depth_2: 10 + (default_depth_2-10)/2|0) ) + (Math.random() * 5 | 0) - 2));
                }, 100);
            }
            else{
                setTimeout(function(){
                    make_random_move();
                }, 100);
            }
        }

        
        
    }
    
}

function make_random_move(){
    var moves = get_moves(side_to_move), moves_all = [];
    for(curr_moves in moves){
        for(curr_move in moves[curr_moves]){
            moves_all.push(moves[curr_moves][curr_move]);
        }
    }
    var random_move =  moves_all[ Math.random() * moves_all.length | 0 ]
    make_move(random_move);
    move_graphic(random_move);
    if(random_move.promotion){
        move_graphic(random_move);
    }


    if(!game_over){

        if(side_to_move === 'white'? default_depth >=0: default_depth_2 >=0){

            setTimeout(function(){
                stockfish.postMessage("setoption name Skill Level value " + (side_to_move === 'white'? default_depth: default_depth_2));

                var message = 'position startpos';
                if(moves_history.length){
                    message += ' moves';
                    for(var move in moves_history){
                        move = moves_history[move];
                        message += ' ' + move.from + move.to;
                        if(move.promotion){
                            message += move.new_figure[0];
                        }
                    }
                }

                stockfish.postMessage(message);
                stockfish.postMessage("go depth " + ((side_to_move === 'white'? (default_depth <= 10? default_depth: 10 + (default_depth-10)/2|0) 
                    : (default_depth_2 <= 10? default_depth_2: 10 + (default_depth_2-10)/2|0) ) + (Math.random() * 5 | 0) - 2));
            }, 100);

        }
        else{
            setTimeout(function(){
                make_random_move();
            }, 100);
        }
    }
    else{
        document.getElementById('new_game').style.display = 'block';
    }
}

function change_color_in(from_who){
    if(from_who === 'standart' && board_position === 'standart'){
        document.getElementById('chcolor').style.display = 'none';
        document.getElementById('chcolor2').style.display = 'block';
    }
    else if(from_who === 'reversed' && board_position === 'reversed'){
        document.getElementById('chcolor2').style.display = 'none';
        document.getElementById('chcolor').style.display = 'block';
    }
}

function change_color_out(from_who){
    if(from_who === 'reversed' && board_position === 'standart'){
        document.getElementById('chcolor').style.display = 'block';
        document.getElementById('chcolor2').style.display = 'none';
    }
    else if(from_who === 'standart' && board_position === 'reversed'){
        document.getElementById('chcolor2').style.display = 'block';
        document.getElementById('chcolor').style.display = 'none';
    }
}

function change_color_click(from_who){
    if(from_who === 'reversed'){
        board_position = 'reversed'
        index = 63
        for(curr_elem in table){
            curr_elem = document.getElementById(curr_elem)
            curr_elem.style['margin-top'] = Math.floor(index / 8) * 60 + 'px';
            curr_elem.style['margin-left'] = (index % 8) * 60 + 'px';
            index -= 1
        }
        for(i = 0; i < 8; i++){
            document.getElementById(i+1+'').style['margin-top'] = 12 + i * 60 + 'px';
            document.getElementById(String.fromCharCode(97+i)).style['margin-left'] = 441 - i * 60 + 'px';
        }
    }
    else{
        board_position = 'standart'
        index = 0
        for(curr_elem in table){
            curr_elem = document.getElementById(curr_elem)
            curr_elem.style['margin-top'] = Math.floor(index / 8) * 60 + 'px';
            curr_elem.style['margin-left'] = (index % 8) * 60 + 'px';
            index += 1
        }
        for(i = 0; i < 8; i++){
            document.getElementById(i+1+'').style['margin-top'] = 432 - i * 60 + 'px';
            document.getElementById(String.fromCharCode(97+i)).style['margin-left'] = 21 + i * 60 + 'px';
        }
    }
    change_color_in(from_who);
}