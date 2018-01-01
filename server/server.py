from bottle import route, run, static_file, template, request, abort, redirect, error
from bottle import ERROR_PAGE_TEMPLATE
from websocket_server import WebsocketServer
from threading import Thread
from time import sleep
from json import loads, dumps
from json.decoder import JSONDecodeError
from datetime import datetime
from os import urandom, listdir, mkdir
from os.path import exists
from base64 import b64encode

# TODO - сделать чтобы появлялся экран о том, что человека кикнули за то, что просрочил время
# TODO - сделать не колл 600 а колл 300
# TODO - сделать так чтобы на каджой улице дефолт не ставился премув


class Server:

    Debug = 1

    if Debug:
        ip = '127.0.0.1'
        local_ip = '127.0.0.1'

    else:
        ip = '188.134.82.95'
        local_ip = '192.168.0.100'

    port = 9001

    MAX_THINKING_TIME = 60 * 100 * 100  # Число секунд, умноженное на сто
    MAX_CHAT_LENGTH = 100  # Максимально количество хранимых сообщений в чате и возвращаемых при перезагрузке страницы
    MAX_NICK_LENGTH = 14  # Максимально допустимая длина
    DEFAULT_NICK = 'Anon'  # Если удалось отдать на сервер невалидный ник

    def __init__(self):

        self.server = WebsocketServer(Server.port, Server.local_ip)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.message_received)

        self.unregistered_clients = []
        self.js_clients = []
        self.py_clients = []
        self.sp_clients = []
        self.tb_clients = []
        self.rp_clients = []

        self.main_client = None
        self.started_time = None
        self.is_game_started = False
        self.is_registration_started = False

        self.replays = []
        self.players_in_game = None
        self.game_name = None

    def run(self):
        self.server.run_forever()

    def send_http(self, message):

        self.server.send_message(self.main_client, message)

    def send(self, _id, message):

        self.main_client[_id] = None

        self.server.send_message(self.main_client, message)

        while self.main_client[_id] is None:
            sleep(0.1)

        receive = self.main_client[_id]
        del self.main_client[_id]

        return receive

    def thinking(self, client):

        client['to decide'] = True
        for _ in range(Server.MAX_THINKING_TIME):
            if not client['to decide']:
                break
            sleep(0.01)
        else:
            client['to decide'] = False
            self.server.send_message(client, '1')

    @staticmethod
    def dump_replay(obj):

        output = ''

        for d, s in obj:
            output += '%s %s %s %s %s %s %s' % (d.year, d.month, d.day, d.hour, d.minute, d.second, d.microsecond)
            output += '\n'
            output += s
            output += '\n'

        return output

    @staticmethod
    def load_replay(s):

        output = []

        by_str = iter(s.split('\n'))

        for d, s in zip(by_str, by_str):
            output += [(datetime(*map(int, d.split())), s)]

        return output

    def handle_replay(self, client):

        num, table = client['name'].split(':')
        hand = 0

        try:

            replays = sorted(listdir('files/replay/poker'))

            replay_info = listdir('files/replay/poker/' + replays[int(num)])

            table_info = 'files/replay/poker/' + replays[int(num)] + '/' + \
                         sorted(replay_info, key=lambda x: int(x.split()[0]))[int(table)]

            hand_info = Server.load_replay(open(table_info + '/0', 'r').read())

            curr_time = datetime.now()
            start_time = hand_info[0][0]

        except IndexError:

            self.server.send_message(client, dumps({'type': 'finish',
                                                    'msg': 'Can not find replay for this table.'}))

            client['loop'] = False
            client['handle'].finish()

        else:

            curr_action = 0

            while client['loop']:

                if exists(table_info + '/' + str(hand)):
                    hand_info = Server.load_replay(open(table_info + '/' + str(hand), 'r').read())

                    for time, message in hand_info[curr_action:]:

                        while time - start_time > datetime.now() - curr_time:
                            sleep(0.01)

                            if client['message'] is not None:
                                break

                            if not client['loop']:
                                return

                        if client['message'] is not None:
                            break

                        if not client['loop']:
                            return

                        self.server.send_message(client, message)
                        curr_action += 1

                    if client['message'] is not None:

                        if client['message'] == 'pause':

                            while True:

                                client['message'] = None

                                while client['message'] is None:
                                    sleep(0.01)

                                    if not client['loop']:
                                        return

                                if not client['loop']:
                                    return

                                if client['message'] == 'next step':

                                    if curr_action < len(hand_info):

                                        _, message = hand_info[curr_action]
                                        self.server.send_message(client, message)

                                        curr_action += 1

                                    else:

                                        hand += 1
                                        curr_action = 0

                                        if exists(table_info + '/' + str(hand)):
                                            hand_info = Server.load_replay(
                                                open(table_info + '/' + str(hand), 'r').read())

                                            _, message = hand_info[curr_action]
                                            self.server.send_message(client, message)

                                            curr_action += 1

                                        else:

                                            hand -= 1

                                            self.server.send_message(client, dumps({'type': 'info',
                                                                                    'msg': 'It was last hand.'}))

                                elif client['message'] == 'next hand':

                                    hand += 1
                                    curr_action = 0

                                    if exists(table_info + '/' + str(hand)):
                                        hand_info = Server.load_replay(open(table_info + '/' + str(hand), 'r').read())

                                        self.server.send_message(client, dumps({'type': 'clear'}))

                                        _, message = hand_info[curr_action]
                                        self.server.send_message(client, message)

                                        curr_action += 1

                                    else:

                                        hand -= 1

                                        self.server.send_message(client, dumps({'type': 'info',
                                                                                'msg': 'It was last hand.'}))

                                elif client['message'] == 'prev hand':

                                    hand -= 1
                                    curr_action = 0

                                    if exists(table_info + '/' + str(hand)):
                                        hand_info = Server.load_replay(open(table_info + '/' + str(hand), 'r').read())

                                        self.server.send_message(client, dumps({'type': 'clear'}))

                                        _, message = hand_info[curr_action]
                                        self.server.send_message(client, message)

                                        curr_action += 1

                                    else:

                                        hand += 1

                                        self.server.send_message(client, dumps({'type': 'info',
                                                                                'msg': 'It was first hand.'}))

                                elif client['message'] == 'play':

                                    client['message'] = None

                                    if curr_action < len(hand_info):

                                        start_time = hand_info[curr_action][0]
                                        curr_time = datetime.now()

                                        break

                                    else:

                                        hand += 1

                                        if exists(table_info + '/' + str(hand)):
                                            hand_info = Server.load_replay(
                                                open(table_info + '/' + str(hand), 'r').read())

                                            self.server.send_message(client, dumps({'type': 'clear'}))

                                            curr_action = 0
                                            start_time = hand_info[curr_action][0]
                                            curr_time = datetime.now()

                                        break

                        elif client['message'] == 'prev hand':

                            client['message'] = None

                            hand -= 1
                            curr_action = 0

                            if exists(table_info + '/' + str(hand)):
                                hand_info = Server.load_replay(open(table_info + '/' + str(hand), 'r').read())

                                self.server.send_message(client, dumps({'type': 'clear'}))

                                start_time = hand_info[curr_action][0]
                                curr_time = datetime.now()

                            else:

                                hand += 1

                                self.server.send_message(client, dumps({'type': 'info',
                                                                        'msg': 'It was first hand.'}))

                                hand_info = Server.load_replay(open(table_info + '/' + str(hand), 'r').read())

                                self.server.send_message(client, dumps({'type': 'clear'}))

                                start_time = hand_info[curr_action][0]
                                curr_time = datetime.now()

                        elif client['message'] == 'next hand':

                            client['message'] = None

                            hand += 1

                            if exists(table_info + '/' + str(hand)):
                                hand_info = Server.load_replay(open(table_info + '/' + str(hand), 'r').read())

                                self.server.send_message(client, dumps({'type': 'clear'}))

                                curr_action = 0
                                start_time = hand_info[curr_action][0]
                                curr_time = datetime.now()

                            else:

                                hand -= 1

                                self.server.send_message(client, dumps({'type': 'info',
                                                                        'msg': 'It was last hand.'}))

                    else:
                        hand += 1
                        curr_action = 0

                else:
                    self.server.send_message(client, dumps({'type': 'finish',
                                                            'msg': 'Replay ended.'}))
                    return

    # Called for every client connecting (after handshake)
    def new_client(self, client, _):
        print("New client connected and was given id %d" % client['id'])
        self.unregistered_clients += [client]

    # Called for every client disconnecting
    def client_left(self, client, _):

        if client is None:
            return

        print("Client(%d) disconnected" % client['id'])

        if client in self.unregistered_clients:
            del self.unregistered_clients[self.unregistered_clients.index(client)]
            print('DEL UNR')

        elif client in self.py_clients:
            del self.py_clients[self.py_clients.index(client)]

            if client['connect'] is not None and not client['busted']:
                self.server.send_message(client['connect'], dumps({'type': 'finish',
                                                                   'msg': 'Game was broken.'}))
                client['connect']['handler'].finish()

            print('DEL PY')

        elif client in self.js_clients:
            del self.js_clients[self.js_clients.index(client)]

            if self.is_game_started:
                client['connect']['connect'] = None
                client['connect']['disconnection'] = True

                if client['connect']['reconnection']:
                    print('CLIENT DISCONNECTED WHILE TRYING TO RECONNECT')
                    client['connect']['reconnection'] = False

                for msg in client['connect']['history'][::-1]:

                    if loads(msg)['type'] == 'set decision':
                        client['connect']['to decide'] = False
                        self.server.send_message(client['connect'], '1')
                        break

                    elif loads(msg)['type'] == 'switch decision':
                        break

            elif client['name'] in [cl['name'] for cl in self.py_clients]:
                self.send_http('delete ' + client['name'])

            print('DEL JS')

        elif client in self.sp_clients:
            del self.sp_clients[self.sp_clients.index(client)]
            del client['table']['watchers'][client['table']['watchers'].index(client)]

            print('DEL SP')

        elif client in self.tb_clients:
            del self.tb_clients[self.tb_clients.index(client)]

            if client['replay']:
                client['hands history'] += [client['replay']]

            self.replays += [(client['name'], client['hands'], client['hands history'])]

            for curr_client in client['watchers']:
                self.server.send_message(curr_client, dumps({'type': 'finish',
                                                             'msg': 'Table is closed.'}))
                curr_client['handler'].finish()

            print('DEL TB')

        elif client in self.rp_clients:
            del self.rp_clients[self.rp_clients.index(client)]

            client['loop'] = False
            client['thread'].join()

            print('DEL RP')

        elif client is self.main_client:
            self.main_client = None

            print('DEL MAIN')

            for curr_client in self.js_clients + self.py_clients + self.sp_clients + self.tb_clients + self.rp_clients:
                curr_client['handler'].finish()

            self.py_clients = []
            self.js_clients = []
            self.sp_clients = []
            self.tb_clients = []
            self.rp_clients = []

    # Called when a client sends a message
    def message_received(self, client, _, message):

        if client is None:
            return

        message = message.encode('ISO-8859-1').decode()

        if client in self.unregistered_clients:

            print("Client(%d) said: %s" % (client['id'], message))

            from_who, name = message.split()
            client['name'] = name

            if from_who == 'rp':

                del self.unregistered_clients[self.unregistered_clients.index(client)]
                self.rp_clients += [client]

                client['loop'] = True
                client['message'] = None
                client['thread'] = Thread(target=lambda: self.handle_replay(client))
                client['thread'].start()

            elif self.main_client is None and from_who != 'main':
                self.server.send_message(client, dumps({'type': 'finish',
                                                        'msg': 'Game server is offline.'}))
                client['handler'].finish()

            elif from_who == 'js' and name in [client['name'] for client in self.js_clients]:
                self.server.send_message(client, dumps({'type': 'finish',
                                                        'msg': 'Player with this name already exists.'}))
                client['handler'].finish()

            elif from_who == 'py':
                del self.unregistered_clients[self.unregistered_clients.index(client)]

                self.py_clients += [client]

                for curr_client in self.js_clients:
                    if curr_client['name'] == name:

                        curr_client['connect'] = client
                        client['connect'] = curr_client

                        client['history'] = []
                        client['disconnection'] = False
                        client['reconnection'] = False
                        client['was resit'] = False
                        client['first resit'] = True
                        client['to decide'] = False
                        client['busted'] = False
                        client['table'] = None

                        print('connected py', client["id"], 'and js', curr_client["id"])
                        break

            elif from_who == 'tb':

                del self.unregistered_clients[self.unregistered_clients.index(client)]
                self.tb_clients += [client]

                client['watchers'] = []
                client['history'] = []
                client['hands history'] = []
                client['chat history'] = []
                client['busy'] = False
                client['open cards replay'] = False
                client['replay'] = []
                client['hands'] = 0

            elif from_who == 'sp' and name in [cl['name'] for cl in self.tb_clients]:

                del self.unregistered_clients[self.unregistered_clients.index(client)]
                self.sp_clients += [client]

                for curr_client in self.tb_clients:
                    if curr_client['name'] == name:

                        curr_client['busy'] = True

                        self.server.send_message(client, dumps({'type': 'reconnect start'}))

                        for msg in curr_client['history']:
                            self.server.send_message(client, msg)
                            print('start spectate', client['name'], msg)

                        for chat_msg in curr_client['chat history']:
                            self.server.send_message(client, chat_msg)
                            print('start spectate chat', client['name'], chat_msg)

                        self.server.send_message(client, dumps({'type': 'reconnect end'}))

                        curr_client['watchers'] += [client]
                        client['table'] = curr_client
                        client['nick'] = None

                        curr_client['busy'] = False

                        break

            elif from_who == 'sp':
                self.server.send_message(client, dumps({'type': 'finish',
                                                        'msg': 'Table is not active.'}))
                client['handler'].finish()

            elif from_who == 'js' and not self.is_game_started and self.is_registration_started:

                del self.unregistered_clients[self.unregistered_clients.index(client)]
                self.js_clients += [client]

                self.send_http('add ' + name)

            elif from_who == 'js' and (self.is_game_started and name in [client['name'] for client in self.py_clients]
                                       and max(client for client in self.py_clients
                                               if client['name'] == name)['disconnection']):

                del self.unregistered_clients[self.unregistered_clients.index(client)]
                self.js_clients += [client]

                for curr_client in self.py_clients:
                    if curr_client['name'] == name and curr_client['disconnection']:

                        curr_client['reconnection'] = True

                        self.server.send_message(client, dumps({'type': 'reconnect start'}))

                        for msg in curr_client['history']:
                            self.server.send_message(client, msg)
                            print('restore', client['name'], msg)

                        table = curr_client['table']

                        for tb_client in self.tb_clients:

                            if tb_client['name'] == table:

                                for chat_msg in tb_client['chat history']:
                                    self.server.send_message(client, chat_msg)
                                    print('restore chat', client['name'], chat_msg)

                                break

                        self.server.send_message(client, dumps({'type': 'reconnect end'}))

                        curr_client['connect'] = client
                        client['connect'] = curr_client

                        print('reconnected py', curr_client["id"], 'and js', client["id"])

                        curr_client['disconnection'] = False
                        curr_client['reconnection'] = False

                        break

            elif from_who == 'main' and self.main_client is None:
                del self.unregistered_clients[self.unregistered_clients.index(client)]
                self.main_client = client

            elif from_who != 'main' and not self.is_registration_started and not self.is_game_started:
                self.server.send_message(client, dumps({'type': 'finish',
                                                        'msg': 'Registration is not started yet.'}))
                client['handler'].finish()

            else:
                self.server.send_message(client, dumps({'type': 'finish',
                                                        'msg': 'You are not in the game.'}))
                client['handler'].finish()

        elif client is self.main_client:

            print('main said:', message)

            to_whom, message = message.split()

            if to_whom == 'http':

                if message == 'start_registration':
                    self.is_registration_started = True

                elif message == 'start':
                    self.is_game_started = True
                    self.is_registration_started = False
                    self.started_time = datetime.now()

                elif message == 'end':
                    self.is_game_started = False
                    self.is_registration_started = False

                    total_tables = len(self.replays)
                    total_players = self.players_in_game
                    name = self.game_name
                    total_hands = sum(rep[1] for rep in self.replays)

                    if name == '':
                        tournament_path = ('files/replay/poker/' + str(self.started_time)[:-7]
                                           .replace(' ', '_').replace(':', '-') +
                                           ' %s %s %s' % (total_tables, total_players, total_hands))

                    else:
                        tournament_path = ('files/replay/poker/' + str(self.started_time)[:-7]
                                           .replace(' ', '_').replace(':', '-') +
                                           ' %s %s %s %s' % (total_tables, total_players, total_hands, name))

                    mkdir(tournament_path)

                    for table_num, hands, hands_history in self.replays:

                        table_path = tournament_path + '/%s %s' % (table_num, hands)

                        mkdir(table_path)

                        for num, hand in enumerate(hands_history):
                            open(table_path + '/%s' % (num, ), 'w').write(Server.dump_replay(hand))

                    self.replays = []
                    self.players_in_game = None
                    self.game_name = None

                elif message.startswith('players'):

                    self.players_in_game = int(message.split(':')[-1])

                elif message.startswith('name'):

                    self.game_name = message.split(':')[-1]

                elif message == 'broken':
                    self.is_game_started = False
                    self.is_registration_started = False
                    self.replays = []
                    self.players_in_game = None
                    self.game_name = None

            else:
                client[to_whom] = message

        else:

            if client in self.py_clients:

                if message == 'new hand':
                    client['history'] = []

                elif message == 'decision':

                    if client['disconnection']:
                        self.server.send_message(client, '1')

                    else:
                        Thread(target=lambda: self.thinking(client), name='Thinking').start()

                elif message == 'busted':
                    client['busted'] = True

                elif message.startswith('resit'):

                    if client['first resit']:

                        client['first resit'] = False

                        _, table = message.split()
                        client['table'] = table

                    else:

                        client['was resit'] = True

                        _, table = message.split()
                        client['table'] = table

                        for curr_client in self.tb_clients:
                            if curr_client['name'] == table:
                                client['history'] = curr_client['history'][:]
                                break
                        else:
                            client['history'] = []

                else:

                    if client['was resit']:

                        client['reconnection'] = True
                        client['was resit'] = False

                        print('to player', client['name'], '(' + str(client['id']) + ')', message)
                        self.server.send_message(client['connect'], message)

                        self.server.send_message(client['connect'], dumps({'type': 'reconnect start'}))

                        for msg in client['history']:
                            self.server.send_message(client['connect'], msg)
                            print('restore when resit', client['name'], msg)

                        self.server.send_message(client['connect'], dumps({'type': 'reconnect end'}))

                        print('reconnected when resit ', client["id"])
                        client['reconnection'] = False

                    else:

                        while client['reconnection']:
                            sleep(0.1)

                        client['history'] += [message]

                        if client['connect'] in self.js_clients:

                            print('to player', client['name'], '(' + str(client['id']) + ')', message)
                            self.server.send_message(client['connect'], message)

            elif client in self.tb_clients:

                if message == 'new hand':

                    if client['replay']:
                        client['hands history'] += [client['replay']]

                    client['history'] = []
                    client['replay'] = []
                    client['hands'] += 1

                elif message == 'end':
                    client['handler'].finish()

                elif message == 'open cards replay':
                    client['open cards replay'] = True

                elif client['open cards replay']:
                    client['open cards replay'] = False
                    client['replay'] += [(datetime.now(), message)]

                else:

                    while client['busy']:
                        sleep(0.1)

                    client['history'] += [message]
                    client['replay'] += [(datetime.now(), message)]

                    for curr_client in client['watchers']:

                        print('to spectator', curr_client['id'], ':', message)
                        self.server.send_message(curr_client, message)

            elif client in self.rp_clients:

                if client['message'] is None:

                    if message == 'pause':
                        client['message'] = 'pause'

                    elif message == 'play':
                        client['message'] = 'play'

                    elif message == 'next step':
                        client['message'] = 'next step'

                    elif message == 'prev hand':
                        client['message'] = 'prev hand'

                    elif message == 'next hand':
                        client['message'] = 'next hand'

            else:

                print("Client(%d) answered: %s" % (client['id'], message))

                if client in self.js_clients:

                    try:
                        json_message = loads(message)

                    except JSONDecodeError:
                        pass

                    else:

                        if json_message['type'] == 'decision':

                            if client['connect']['to decide']:
                                client['connect']['to decide'] = False
                                self.server.send_message(client['connect'], json_message['text'])

                        elif json_message['type'] == 'chat':

                            json_message['text'] = '[Player ' + client['name'] + ']: ' + json_message['text']
                            message = dumps(json_message)

                            table = client['connect']['table']

                            for curr_client in self.tb_clients:

                                if curr_client['name'] == table:

                                    curr_client['chat history'] += [message]

                                    if len(curr_client['chat history']) > Server.MAX_CHAT_LENGTH:
                                        _, curr_client['chat history'] = curr_client['chat history']

                                    curr_client['replay'] += [(datetime.now(), message)]

                                    for curr_watcher in curr_client['watchers']:
                                        print('to spectator', curr_watcher['id'], ':', message)
                                        self.server.send_message(curr_watcher, message)

                                    break

                            for curr_client in self.js_clients:
                                if curr_client['connect']['table'] == table:
                                    print('to player', curr_client['name'], ':', json_message)
                                    self.server.send_message(curr_client, message)

                elif client in self.sp_clients:

                    try:
                        json_message = loads(message)

                    except JSONDecodeError:
                        pass

                    else:

                        if json_message['type'] == 'chat':

                            if client['nick'] is None:
                                client['nick'] = 'Anon'

                            json_message['text'] = '[Watcher ' + client['nick'] + ']: ' + json_message['text']
                            message = dumps(json_message)

                            client['table']['chat history'] += [message]

                            if len(client['table']['chat history']) > Server.MAX_CHAT_LENGTH:
                                _, client['table']['chat history'] = client['table']['chat history']

                            client['table']['replay'] += [(datetime.now(), message)]

                            for curr_watcher in client['table']['watchers']:
                                print('to spectator', curr_watcher['id'], ':', message)
                                self.server.send_message(curr_watcher, message)

                            table = client['table']['name']

                            for curr_client in self.js_clients:
                                if curr_client['connect']['table'] == table:
                                    print('to player', curr_client['name'], ':', json_message)
                                    self.server.send_message(curr_client, message)

                        elif json_message['type'] == 'nick':

                            if client['nick'] is None:

                                if 0 < len(json_message['nick']) <= Server.MAX_NICK_LENGTH:
                                    client['nick'] = json_message['nick']

                                else:
                                    client['nick'] = Server.DEFAULT_NICK

                else:
                    raise OverflowError('I DO NOT KNOW WHAT TO DO')


class Key:

    used_keys_path = 'files/key'

    GetAdmin = open('files/admin').read()
    UsedKeys = open(used_keys_path, 'r').read().split()

    @staticmethod
    def get_random_key():

        while True:
            key = b64encode(urandom(48)).decode().replace('+', '0').replace('/', '1')

            if key not in Key.UsedKeys:
                break

        Key.UsedKeys += [key]
        Key.save_keys()

        return key

    @staticmethod
    def del_key(key):

        try:
            del Key.UsedKeys[Key.UsedKeys.index(key)]

        except IndexError:
            print('Wrong key to delete!')

        else:
            Key.save_keys()

    @staticmethod
    def save_keys():
        open(Key.used_keys_path, 'w').write('\n'.join(Key.UsedKeys))


class KeyServer:

    ip = Server.ip
    local_ip = Server.local_ip
    port = 9002

    def __init__(self):

        self.server = WebsocketServer(KeyServer.port, KeyServer.local_ip)
        self.server.set_fn_message_received(self.message_received)

    def run(self):
        self.server.run_forever()

    def message_received(self, client, _, message):

        print("Client(%d) said in key server: %s" % (client['id'], message))

        msg = message.split()

        if len(msg) == 2:
            action, text = msg
            key = ''

        else:
            action, text, key = msg

        if action == 'get':
            if text == Key.GetAdmin:

                key = Key.get_random_key()
                self.server.send_message(client, key)

            else:
                self.server.send_message(client, 'no')

        elif action == 'del':
            if text == Key.GetAdmin:

                Key.del_key(key)
                self.server.send_message(client, 'ok')

            else:
                self.server.send_message(client, 'no')

        elif action == 'test':
            if text in Key.UsedKeys:
                self.server.send_message(client, 'yes')

            else:
                self.server.send_message(client, 'no')


if __name__ == '__main__':

    server = Server()
    Thread(target=lambda: server.run(), name='TCP server').start()

    key_server = KeyServer()
    Thread(target=lambda: key_server.run(), name='Key server').start()

    @route('/')
    def index():
        return static_file('index.html', root='static')

    @route('/<img:re:favicon.ico>')
    @route('/img/<img:path>')
    def img_serve(img):
        return static_file(img, root='img')

    @route('/music/<music:path>')
    def music_serve(music):
        return static_file(music, root='music')

    @route('/static/<file:path>')
    def static_serve(file):
        return static_file(file, root='static')

    @route('/html/<file:path>')
    def static_serve(file):
        return static_file(file, root='static')

    @route('/chess')
    def chess():
        return static_file('chess/menu/chess.html', root='static')

    @route('/chess/engine')
    def engine():
        strength = request.query.strength if 'strength' in request.query else '10'
        return template('static/chess/game_with_engine/game', strength=strength)

    @route('/chess/analysis')
    def analysis():
        return static_file('chess/game_analysis/game.html', root='static')

    @route('/chess/engines')
    def engines():
        strength1 = request.query.strength1 if 'strength1' in request.query else '10'
        strength2 = request.query.strength2 if 'strength2' in request.query else '10'
        return template('static/chess/engines_match/game', strength1=strength1, strength2=strength2)

    @route('/rubiks')
    def rubiks():
        return static_file('rubiks/rubiks.html', root='static')

    @route('/poker')
    def poker():

        state = 'unknown state'

        if server.main_client is None:
            state = 'machine not work'

        elif not server.is_registration_started and not server.is_game_started:
            state = 'game not created'

        elif server.is_registration_started and not server.is_game_started:
            state = 'registration started'

        elif server.is_game_started:
            state = 'game started'

        return template('static/poker/menu/menu.html', state=state, ip=KeyServer.ip, port=KeyServer.port)

    @route('/poker/create')
    def create_game():

        key = request.query.key if 'key' in request.query else 'no key'

        if server.main_client is None or server.is_game_started:
            redirect('/poker')

        elif key not in Key.UsedKeys:
            abort(401, "Sorry, access denied.")

        else:
            return template('static/poker/create/create.html', ip=KeyServer.ip, port=KeyServer.port)

    @route('/poker/create/c')
    def create():

        key = request.query.key if 'key' in request.query else 'no key'

        if server.main_client is None or server.is_game_started:
            redirect('/poker')

        elif key not in Key.UsedKeys:
            abort(401, "Sorry, access denied.")

        else:

            total_count = int(request.query.total_count)
            unreal_count = int(request.query.unreal_count)
            table_count = int(request.query.table_count)
            chip_count = int(request.query.chip_count)

            real_count = total_count - unreal_count

            if real_count < 0:
                redirect('/poker')

            server.send_http('create %s %s %s %s rapid' % (real_count, unreal_count, table_count, chip_count))
            sleep(1)
            redirect('/poker')

    @route('/poker/break')
    def break_game():

        key = request.query.key if 'key' in request.query else 'no key'

        if server.main_client is None:
            redirect('/poker')

        elif key not in Key.UsedKeys:
            abort(401, "Sorry, access denied.")

        else:
            server.send_http('break')
            sleep(1)
            redirect('/poker')

    @route('/poker/watch')
    def poker_tables():

        if server.main_client is None or not server.is_game_started:
            redirect('/poker')

        else:

            info = []

            for client in server.tb_clients:
                info += [client['name']]

            return template('static/poker/watch/watch.html', info=info)

    @route('/poker/replay')
    def poker_replays():

        replays = sorted(listdir('files/replay/poker'))

        info = []

        for _id, replay_info in enumerate(replays):

            rep_split = replay_info.split()

            if len(rep_split) == 4:
                date, tables, players, hands = rep_split
                name = date

            else:
                date, tables, players, hands, name = rep_split[:5]

            info += [(str(_id), date, tables, players, hands, name)]

        return template('static/poker/replay/replays.html', info=info)


    @route('/poker/replay/<num:int>')
    def replay(num):

        replays = sorted(listdir('files/replay/poker'))

        replay_info = listdir('files/replay/poker/' + replays[num])

        info = []
        for rep in replay_info:

            _id, hands = rep.split()
            info += [(_id, hands)]

        return template('static/poker/replay/tables.html', info=sorted(info, key=lambda x: int(x[0])))

    @route('/poker/replay/<num:int>/<table:int>')
    def replay(num, table):
        return template('static/poker/play/poker.html', name='', table='', replay='%s:%s' % (num, table),
                        back_addr='/poker/replay/%s' % (num,), ip=Server.ip, port=Server.port)

    @route('/poker/play/<name>')
    def player(name):
        return template('static/poker/play/poker.html', name=name, table='', replay='', back_addr='/poker',
                        ip=Server.ip, port=Server.port)

    @route('/poker/watch/<table:int>')
    def spectate(table):
        return template('static/poker/play/poker.html', name='', table=table, replay='', back_addr='/poker/watch',
                        ip=Server.ip, port=Server.port)

    @error(404)
    def error404(_error):

        with open("files/404.txt", "a", encoding="utf-8") as file:
            file.write(_error.body.split("'")[1] + '\n')

        return template(ERROR_PAGE_TEMPLATE, e=_error)


    run(host=Server.local_ip, port=80)
