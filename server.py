from bottle import route, run, static_file, template, request, abort, redirect, error
from bottle import ERROR_PAGE_TEMPLATE
from websocket_server import WebsocketServer, WebSocketHandler
from threading import Thread, Lock
from time import sleep
from json import loads, dumps
from json.decoder import JSONDecodeError
from datetime import datetime, timedelta
from os import urandom, listdir, mkdir, getcwd, chdir
from os.path import exists
from base64 import b64encode
from typing import List, Dict, Tuple


if 'server' in listdir('.'):
    chdir('server')


class Debug:
    Debug = 1
    PythonAndJSConnections = 0
    ClientTriesToLogin = 0
    SpectatorInit = 0
    JSClientRestore = 0
    GameEngineMessage = 0
    JSResittingRestore = 0
    MessageFromPythonToJS = 0
    MessageFromTableToSpectator = 0
    MessageReceivedFromJS = 0
    MessageReceivedFromSpectator = 0
    KotlinDebug = 0
    Send = 0
    ClientLeft = 0
    Errors = 1

    if PythonAndJSConnections:
        @staticmethod
        def connect(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def connect(*args, **kwargs):
            pass

    if ClientTriesToLogin:
        @staticmethod
        def login(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def login(*args, **kwargs):
            pass

    if SpectatorInit:
        @staticmethod
        def spectator_init(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def spectator_init(*args, **kwargs):
            pass

    if JSClientRestore:
        @staticmethod
        def js_restore(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def js_restore(*args, **kwargs):
            pass

    if GameEngineMessage:
        @staticmethod
        def engine_msg(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def engine_msg(*args, **kwargs):
            pass

    if JSResittingRestore:
        @staticmethod
        def resitting(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def resitting(*args, **kwargs):
            pass

    if MessageFromPythonToJS:
        @staticmethod
        def py_to_js(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def py_to_js(*args, **kwargs):
            pass

    if MessageFromTableToSpectator:
        @staticmethod
        def tb_to_sp(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def tb_to_sp(*args, **kwargs):
            pass

    if MessageReceivedFromJS:
        @staticmethod
        def from_js(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def from_js(*args, **kwargs):
            pass

    if MessageReceivedFromSpectator:
        @staticmethod
        def from_sp(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def from_sp(*args, **kwargs):
            pass

    if KotlinDebug:
        @staticmethod
        def from_kt(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def from_kt(*args, **kwargs):
            pass

    if Send:
        @staticmethod
        def send(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def send(*args, **kwargs):
            pass

    if ClientLeft:
        @staticmethod
        def client_left(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def client_left(*args, **kwargs):
            pass

    if Errors:
        @staticmethod
        def error(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def error(*args, **kwargs):
            pass


class AbstractClient:

    class ID:
        Unregistered = 'un'
        Python = 'py'
        JavaScript = 'js'
        Kotlin = 'kt'
        Replay = 'rp'
        Table = 'tb'
        Spectator = 'sp'
        GameHandler = 'gh'
        GameEngine = 'ge'

    def __init__(self, _id: int, name: str, handler: WebSocketHandler):
        self.id: int = _id  # Это внутренний ID клиента, присваиваемый сервером
        self.name: str = name
        self.handler: WebSocketHandler = handler

    def finish(self):
        try:
            self.handler.finish()
        except KeyError:
            Debug.error(f'Key error possibly double deleting id = {self.id}, name = {self.name}')

    def send_raw(self, message: str) -> None:
        try:
            Debug.send(f'Send to {self.id}: {message}')
            self.handler.send_message(message)
        except BrokenPipeError:
            Debug.error(f'Broken pipe error send raw id = {self.id}, name = {self.name}')

    def send(self, obj: dict) -> None:
        try:
            msg = dumps(obj)
            Debug.send(f'Send to {self.id}: {msg}')
            self.handler.send_message(msg)
        except BrokenPipeError:
            Debug.error(f'Broken pipe error send id = {self.id}, name = {self.name}')

    def receive(self, srv: 'Server', message: str, client: dict) -> None:
        raise NotImplementedError('Method "receive" is not implemented in derived class')

    def left(self, srv: 'Server') -> None:
        raise NotImplementedError('Method "left" is not implemented in derived class')


class GameEngineClient(AbstractClient):

    OnlyClient = None

    def __init__(self, _id: int, handler: WebSocketHandler):
        super().__init__(_id, AbstractClient.ID.GameEngine, handler)

        if GameEngineClient.OnlyClient is not None:
            raise ValueError("Game engine already exists")

        GameEngineClient.OnlyClient = self

    def receive(self, srv: 'Server', message: str, client: dict):
        pass

    def left(self, srv: 'Server') -> None:
        del srv.game_engine
        srv.game_engine = None

        GameEngineClient.OnlyClient = None

        Debug.client_left('DEL GAME ENGINE')


class GameHandlerClient(AbstractClient):

    def __init__(self, _id: int, json_message: dict, handler: WebSocketHandler):
        super().__init__(_id, AbstractClient.ID.GameHandler, handler)
        self.game_id = json_message['id']

        self.quick_game_name = ''

        if json_message['game type'] == 'tournament':
            self.is_tournament = True
            self.name = json_message['name']
            self.total_players = json_message['total players']
            self.initial_stack = json_message['initial stack']
            self.table_seats = json_message['table seats']
            self.password = json_message['password']
            self.players_left = json_message['players left']

        elif json_message['game type'] == 'quick':
            self.is_tournament = False
            self.name = json_message['name']  # name of the player who plays this quick game

        self.is_registration_started: bool = False
        self.is_game_started: bool = False
        self.started_time: datetime = datetime.now()
        self.replays = []
        self.tb_clients: Dict[str, TableClient] = dict()
        self.waiting_js_clients: Dict[str, JavaScriptClient] = dict()

    def receive(self, srv: 'Server', message: str, client: dict) -> None:

        Debug.engine_msg(f'GameHandler {self.game_id} said: {message}')

        json_message = loads(message)

        if json_message['type'] == 'start registration':
            self.is_registration_started = True

        elif json_message['type'] == 'start game':
            self.is_game_started = True
            self.is_registration_started = False
            self.started_time = datetime.now()

        elif json_message['type'] == 'end game':
            self.is_game_started = False
            self.is_registration_started = False

            if self.is_tournament:

                total_tables = len(self.replays)
                total_players = self.total_players
                name = self.name
                total_hands = sum(rep[1] for rep in self.replays)

                if name == '':
                    game_path = (str(self.started_time)[:-7].replace(' ', '_').replace(':', '-') +
                                 ' %s %s %s' % (total_tables, total_players, total_hands))

                else:
                    game_path = (str(self.started_time)[:-7].replace(' ', '_').replace(':', '-') +
                                 ' %s %s %s %s' % (total_tables, total_players, total_hands, name))

                tournament_path = 'files/replay/poker/games/' + game_path
                chat_messages_path = 'files/replay/poker/chat/' + game_path

                mkdir(tournament_path)
                mkdir(chat_messages_path)

                for table_num, hands, hands_history, chat_history in self.replays:

                    table_folder = '/%s %s' % (table_num, hands)

                    table_path = tournament_path + table_folder
                    chat_path = chat_messages_path + table_folder

                    mkdir(table_path)

                    open(chat_path, 'w').write(ReplayClient.dump_replay(chat_history))

                    for num, hand in enumerate(hands_history):
                        open(table_path + '/%s' % (num,), 'w').write(ReplayClient.dump_replay(hand))

            self.replays = []
            self.finish_all_clients()
            self.finish()

        elif json_message['type'] == 'broken':
            self.is_game_started = False
            self.is_registration_started = False
            self.replays = []
            self.finish_all_clients()
            self.finish()

        elif json_message['type'] == 'update players':
            self.players_left = json_message['left']

    def has_player(self, name: str) -> bool:
        for table in self.tb_clients.values():
            table: TableClient
            for player in table.players:
                if player.name == name:
                    return True
        return False

    def finish_all_clients(self):
        for curr in list(self.tb_clients.values()):
            for curr_sp in curr.spectators:
                curr_sp.finish()
            for curr_py in curr.players:
                if curr_py.connected_js is not None:
                    curr_py.connected_js.finish()
                curr_py.finish()
            curr.finish()
        self.tb_clients = dict()

    def left(self, srv: 'Server') -> None:
        del srv.gh_clients[self.game_id]
        Debug.client_left('DEL GAME HANDLER')
        self.finish_all_clients()


class UnregisteredClient(AbstractClient):

    def __init__(self, _id: int, handler: WebSocketHandler):
        super().__init__(_id, AbstractClient.ID.Unregistered, handler)

    def receive(self, srv: 'Server', message: str, client: dict) -> None:

        Debug.login(f'Unregistered client {self.id} said: {message}')

        try:
            json_message = loads(message)
            client_id = json_message['type']
            name = ''

            if client_id != AbstractClient.ID.Kotlin:
                name = json_message['name']

            game_id = ''

            if (client_id == AbstractClient.ID.JavaScript or
                    client_id == AbstractClient.ID.Table or
                    client_id == AbstractClient.ID.Spectator):
                game_id = json_message['id']

            if client_id == AbstractClient.ID.Python:
                game_id = json_message['game id']

        except JSONDecodeError:
            self.send(dumps({'type': 'bad login'}))
            return

        if client_id == AbstractClient.ID.Replay:
            del srv.unregistered_clients[self.id]
            Debug.login(f'Unregistered client {self.id} classified as replay client')
            rp_client = ReplayClient(self.id, name, self.handler)
            client['client'] = rp_client
            srv.rp_clients += [rp_client]

        elif client_id == AbstractClient.ID.Kotlin:
            del srv.unregistered_clients[self.id]
            Debug.login(f'Unregistered client {self.id} classified as kotlin client')
            kt_client = KotlinClient(self.id, name, self.handler)
            client['client'] = kt_client
            srv.kt_clients += [kt_client]

        elif client_id != AbstractClient.ID.GameEngine and srv.game_engine is None:
            Debug.login(f'Unregistered client {self.id} classified not as game engine client')
            self.send({'type': 'finish', 'msg': 'Game server is offline.'})
            self.finish()

        elif client_id == AbstractClient.ID.GameHandler:
            Debug.login(f'Unregistered client {self.id} classified as game handler client')
            gh_client = GameHandlerClient(self.id, json_message, self.handler)
            client['client'] = gh_client
            srv.gh_clients[json_message['id']] = gh_client
            if not gh_client.is_tournament:
                for kt_client in srv.kt_clients:
                    if kt_client.name == gh_client.name:
                        kt_client.send({'type': 'quick game is ready'})
                        break

        elif client_id == AbstractClient.ID.JavaScript and name in srv.js_clients:
            Debug.login(f'Unregistered client {self.id} classified as already exist javascript client')
            self.send({'type': 'finish', 'msg': 'Player with this name already exists.'})
            self.finish()

        elif client_id == AbstractClient.ID.Python:
            del srv.unregistered_clients[self.id]
            Debug.login(f'Unregistered client {self.id} classified as python client')
            js_client = srv.js_clients[name]
            tournament_id = json_message['id']
            py_client = PythonClient(self.id, tournament_id, game_id, js_client, self.handler)
            client['client'] = py_client
            srv.py_clients[name] = py_client

        elif client_id == AbstractClient.ID.Table:
            del srv.unregistered_clients[self.id]
            Debug.login(f'Unregistered client {self.id} classified as table client')
            tb_client = TableClient(self.id, name, srv.gh_clients[game_id], self.handler)
            client['client'] = tb_client

        elif client_id == AbstractClient.ID.Spectator and name in srv.gh_clients[game_id].tb_clients:
            del srv.unregistered_clients[self.id]
            Debug.login(f'Unregistered client {self.id} classified as spectator client')
            sp_client = SpectatorClient(self.id, name, self.handler)
            client['client'] = sp_client
            srv.sp_clients += [sp_client]
            srv.gh_clients[game_id].tb_clients[name].connect_spectator(sp_client)

        elif client_id == AbstractClient.ID.Spectator:
            Debug.login(f'Unregistered client {self.id} classified as spectator client trying to watch wrong table')
            self.send({'type': 'finish', 'msg': 'Table is not active.'})
            self.finish()

        elif client_id == AbstractClient.ID.JavaScript and game_id == -1 and \
                name in [game.name for game in srv.gh_clients.values() if not game.is_tournament]:
            Debug.login(f'Unregistered client {self.id} classified as javascript client connected to quick game')
            game = max([game for game in srv.gh_clients.values() if not game.is_tournament and name == game.name])
            del srv.unregistered_clients[self.id]
            js_client = JavaScriptClient(self.id, name, self.handler)
            client['client'] = js_client
            game.waiting_js_clients[name] = js_client
            srv.js_clients[name] = js_client
            game.send({'type': 'add player', 'name': json_message['name']})

        elif client_id == AbstractClient.ID.JavaScript and \
                not srv.gh_clients[game_id].is_game_started and srv.gh_clients[game_id].is_registration_started:
            Debug.login(f'Unregistered client {self.id} classified as javascript client')
            game = srv.gh_clients[game_id]
            if game.is_tournament and game.password == json_message['password']:
                del srv.unregistered_clients[self.id]
                js_client = JavaScriptClient(self.id, name, self.handler)
                client['client'] = js_client
                game.waiting_js_clients[name] = js_client
                srv.js_clients[name] = js_client
                game.send({'type': 'add player', 'name': json_message['name']})
            else:
                self.send({'type': 'error', 'msg': 'bad id or password'})

        elif client_id == AbstractClient.ID.JavaScript and srv.gh_clients[game_id].is_game_started and \
                name in srv.py_clients and srv.py_clients[name].is_disconnected:
            Debug.login(f'Unregistered client {self.id} classified as reconnected javascript client')
            if json_message['password'] == srv.gh_clients[game_id].password:
                del srv.unregistered_clients[self.id]
                py_client = srv.py_clients[name]
                js_client = JavaScriptClient.restore(self.id, py_client, self.handler)
                client['client'] = js_client
                srv.js_clients[name] = js_client
            else:
                self.send({'type': 'error', 'msg': 'bad id or password'})

        elif client_id == AbstractClient.ID.GameEngine and srv.game_engine is None:
            del srv.unregistered_clients[self.id]
            Debug.login(f'Unregistered client {self.id} classified as game engine client')
            game_client = GameEngineClient(self.id, self.handler)
            client['client'] = game_client
            srv.game_engine = game_client

        else:
            Debug.login(f'Unregistered client {self.id} classified as something wrong')
            self.send({'type': 'finish', 'msg': 'You are not in the game.'})
            self.finish()

    def left(self, srv: 'Server') -> None:
        del srv.unregistered_clients[self.id]
        Debug.client_left('DEL UNR')


class JavaScriptClient(AbstractClient):

    def __init__(self, _id: int, name: str, handler: WebSocketHandler):
        super().__init__(_id, name, handler)
        self.connected_python: PythonClient = None

    @staticmethod
    def restore(_id: int, py_client: 'PythonClient', handler: WebSocketHandler) -> 'JavaScriptClient':
        new_js = JavaScriptClient(_id, py_client.name, handler)
        py_client.reconnect_js(new_js)
        return new_js

    def receive(self, srv: 'Server', message: str, client: dict) -> None:

        Debug.from_js(f'Message from js {self.name}: {message}')

        try:
            json_message = loads(message)

        except JSONDecodeError:
            Debug.from_js(f'JSON decode error msg from js {self.name} {message}')

        else:

            if json_message['type'] == 'decision' and 'text' in json_message:
                if self.connected_python.in_decision:
                    self.connected_python.in_decision = False
                    self.connected_python.send_raw(json_message['text'])

            elif json_message['type'] == 'chat' and 'text' in json_message:
                json_message['text'] = f'[Player {self.name}]: {json_message["text"]}'
                self.connected_python.connected_table.chat_message(dumps(json_message))

    def left(self, srv: 'Server') -> None:
        del srv.js_clients[self.name]

        if not self.connected_python.connected_table.connected_game.is_tournament:
            self.connected_python.connected_table.connected_game.send({'type': 'break'})

        elif self.connected_python.connected_table.connected_game.is_game_started:

            self.connected_python.connected_js = None

            if not self.connected_python.is_busted:

                self.connected_python.is_disconnected = True

                disconnected_message = dumps({'type': 'disconnected',
                                              'id': self.connected_python.game_id})

                self.connected_python.connected_table.cast(disconnected_message)
                self.connected_python.connected_table.chat_message(dumps({'type': 'chat',
                                                                          'text': f'{self.name} disconnected'}))

                for msg in reversed(self.connected_python.history):

                    if loads(msg)['type'] == 'set decision':
                        self.connected_python.in_decision = False
                        self.connected_python.send_raw('1')
                        break

                    elif loads(msg)['type'] == 'switch decision':
                        break

        elif self.name in [cl.name for cl in srv.py_clients.values()]:
            Debug.client_left('SEND HTTP DELETE ' + self.name)
            self.connected_python.connected_table.connected_game.send({'type': 'delete', 'name': self.name})

        Debug.client_left('DEL JS')


class PythonClient(AbstractClient):

    def __init__(self, _id: int, game_id: int, game_handler_id: int,
         js_client: JavaScriptClient, handler: WebSocketHandler):

        super().__init__(_id, js_client.name, handler)
        self.game_id = game_id
        self.game_handler_id = game_handler_id

        self.history: List[str] = []

        self.is_disconnected: bool = False
        self.in_decision: bool = False
        self.is_busted: bool = False

        self.lock: Lock = Lock()

        self.connected_table: TableClient = None

        self.thinking_time: int = Server.MAX_THINKING_TIME
        self.back_counting: int = Server.START_COUNTING_TIME
        self.kicked_thinking_time: int = Server.MAX_THINKING_TIME_AFTER_KICK

        self.connected_js: JavaScriptClient = js_client
        js_client.connected_python = self

        Debug.connect(f'connected py and js {self.name}')

    def reconnect_js(self, js_client: JavaScriptClient) -> None:
        if self.connected_js is not None:
            raise ValueError(f'Python client {self.name} already has js client')

        if not self.is_disconnected:
            raise ValueError(f'Python client {self.name} is not disconnected')

        self.connected_js = js_client
        js_client.connected_python = self

        Debug.js_restore(f'Start restore client {js_client.name} js to py')

        with self.lock:

            js_client.send({'type': 'reconnect start'})

            for msg in self.history:
                js_client.send_raw(msg)
                Debug.js_restore(f'Restore js client {js_client.name} {msg}')

            for chat_msg in self.connected_table.get_last_chat_messages():
                js_client.send_raw(chat_msg)
                Debug.js_restore(f'Restore chat js client {js_client.name} {msg}')

            Debug.js_restore(f'End restore js client {js_client.name}')

            js_client.send({'type': 'reconnect end'})

            self.is_disconnected = False

        self.connected_table.cast(dumps({'type': 'connected', 'id': self.game_id}))
        self.connected_table.chat_message(dumps({'type': 'chat', 'text': f'{self.name} connected'}))

    def send_to_js(self, message: str, need_to_save: bool = False) -> None:
        if self.connected_js is not None:
            Debug.py_to_js(f'To js client {self.name} {message}')
            try:
                self.connected_js.send_raw(message)
            except AttributeError:
                pass
        if need_to_save:
            self.history += [message]

    def thinking(self):

        self.in_decision = True
        end_thinking_time = datetime.now() + timedelta(seconds=self.thinking_time)
        back_counting = self.back_counting + 1
        while datetime.now() < end_thinking_time:
            sleep(0.01)
            if not self.in_decision:
                break
            if (end_thinking_time - datetime.now()).seconds < back_counting:
                back_counting -= 1
                self.connected_table.cast(dumps({'type': 'back counting', 'time': back_counting, 'id': self.game_id}))
        else:
            self.send_to_js(dumps({'type': 'kick'}))
            self.thinking_time = self.kicked_thinking_time
            if self.connected_js is not None:
                self.connected_js.finish()

    def receive(self, srv: 'Server', message: str, client: dict):

        if message.startswith('new_hand'):
            self.history = []
            _, message = message.split(' ', 1)

            message = self.connected_table.inject_disconnections(message)
            with self.lock:
                self.send_to_js(message, True)

        elif message.startswith('decision'):

            if self.is_disconnected:
                self.send_raw('1')

            else:
                _, message = message.split(' ', 1)

                json_message = loads(message)
                json_message['time'] = self.thinking_time
                message = dumps(json_message)

                with self.lock:
                    self.send_to_js(message, True)

                Thread(target=lambda: self.thinking(), name=f'Thinking {self.name}').start()

        elif message == 'busted':
            self.is_busted = True

        elif message.startswith('resit'):

            _, game_id, table_num, message = message.split(' ', 3)

            gh_client: GameHandlerClient = srv.gh_clients[int(game_id)]
            new_table: TableClient = gh_client.tb_clients[table_num]

            if self.connected_table is not None:
                self.connected_table.players.remove(self)
                self.history = new_table.history[:]
                need_reconnection = True

            else:
                need_reconnection = False

            self.connected_table = new_table
            self.connected_table.players += [self]

            if need_reconnection:
                with self.lock:

                    Debug.resitting(f'Start resitting restore to client {self.name} {message}')
                    self.send_to_js(self.connected_table.inject_disconnections(message))

                    self.send_to_js(dumps({'type': 'reconnect start'}))

                    for msg in self.history:
                        self.send_to_js(msg)
                        Debug.resitting(f'Restore when resit {self.name} {msg}')

                    self.send_to_js(dumps({'type': 'reconnect end'}))

                    Debug.resitting(f'Reconnected when resit {self.name}')

        else:
            with self.lock:
                self.send_to_js(message, True)

    def left(self, srv: 'Server'):
        del srv.py_clients[self.name]

        if self.connected_js is not None and not self.is_busted:
            self.send_to_js(dumps({'type': 'finish', 'msg': 'Game was broken.'}))
            self.connected_js.finish()

        Debug.client_left('DEL PY')


class SpectatorClient(AbstractClient):

    def __init__(self, _id: int, name: str, handler: WebSocketHandler):
        super().__init__(_id, name, handler)

        self.connected_table: TableClient = None
        self.nick: str = None

    def receive(self, srv: 'Server', message: str, client: dict) -> None:

        Debug.from_sp(f'Message from spectator {self.name}: {message}')

        try:
            json_message = loads(message)

        except JSONDecodeError:
            Debug.from_sp(f'JSON decode error msg from spectator {self.name} {message}')

        else:

            if json_message['type'] == 'chat' and 'text' in json_message:
                if self.nick is None:
                    self.nick = Server.DEFAULT_NICK
                json_message['text'] = f'[Watcher {self.nick}]: {json_message["text"]}'
                self.connected_table.chat_message(dumps(json_message))

            elif json_message['type'] == 'nick' and 'nick' in json_message:
                if self.nick is None:
                    if 0 < len(json_message['nick']) <= Server.MAX_NICK_LENGTH:
                        self.nick = json_message['nick']
                    else:
                        self.nick = Server.DEFAULT_NICK

    def left(self, srv: 'Server') -> None:
        del srv.sp_clients[srv.sp_clients.index(self)]
        del self.connected_table.spectators[self.connected_table.spectators.index(self)]
        Debug.client_left('DEL SP')


class TableClient(AbstractClient):

    def __init__(self, _id: int, name: str, game: GameHandlerClient, handler: WebSocketHandler):
        super().__init__(_id, name, handler)

        self.spectators: List[SpectatorClient] = []
        self.players: List[PythonClient] = []

        self.connected_game: GameHandlerClient = game
        game.tb_clients[name] = self

        self.history: List[str] = []
        self.chat_history: List[Tuple[datetime, str]] = []
        self.replay: List[Tuple[datetime, str]] = []
        self.hands_history: List[List[Tuple[datetime, str]]] = []

        self.lock: Lock = Lock()

        self.is_first_hand: bool = True
        self.hands: int = 0

    def connect_spectator(self, spectator: SpectatorClient) -> None:

        with self.lock:
            spectator.send({'type': 'reconnect start'})

            Debug.spectator_init(f'Spectator {spectator.name} reconnect start')

            for msg in self.history:
                spectator.send_raw(msg)
                Debug.spectator_init(f'Start spectate {spectator.name} {msg}')

            for chat_msg in self.get_last_chat_messages():
                spectator.send_raw(chat_msg)
                Debug.spectator_init(f'Restore chat {spectator.name} {chat_msg}')

            Debug.spectator_init(f'Spectator {spectator.name} reconnect end')

            spectator.send({'type': 'reconnect end'})

            self.spectators += [spectator]
            spectator.connected_table = self

    def cast_to_spectators(self, message: str):
        with self.lock:
            for spectator in self.spectators:
                Debug.tb_to_sp(f'Table {self.name} to spectator {spectator.id} {message}')
                spectator.send_raw(message)

    def cast_to_javascript(self, message: str):
        with self.lock:
            for curr in self.players:
                curr.send_to_js(message, True)

    def cast(self, message: str, is_chat_message: bool = False):
        if not is_chat_message:
            # because chat messages restored separately with self.chat_history
            self.history += [message]
        self.replay += [(datetime.now(), message)]
        self.cast_to_spectators(message)
        self.cast_to_javascript(message)

    def chat_message(self, message: str):
        self.chat_history += [(datetime.now(), message)]
        self.cast(message, True)

    def get_last_chat_messages(self) -> List[str]:
        return [message[1] for message in self.chat_history[-Server.MAX_CHAT_LENGTH:]]

    def inject_disconnections(self, message: str) -> str:
        with self.lock:
            json_message = loads(message)
            players_ids = [curr.game_id for curr in self.players]
            for curr in json_message['players']:
                if curr['id'] in players_ids:
                    pl = max(pl for pl in self.players if pl.game_id == curr['id'])
                    curr['disconnected'] = pl.is_disconnected
                else:
                    curr['disconnected'] = False
            return dumps(json_message)

    def receive(self, srv: 'Server', message: str, client: dict) -> None:

        print("TABLE RECIEVE", message)

        if message.startswith('new_hand'):

            _, message = message.split(' ', 1)

            if self.replay:
                self.hands_history += [self.replay]

            self.history = []
            self.replay = []
            self.hands += 1

            message = self.inject_disconnections(message)
            self.history += [message]
            self.replay += [(datetime.now(), message)]
            self.cast_to_spectators(message)

        elif message.startswith('player_hand'):

            _, player_id, message = message.split(' ', 2)

            for pl in self.players:
                pl: PythonClient
                print('PLAYER HAND', pl.name, pl.game_id, pl.game_handler_id)

            # todo : very bad hack
            new_players = []
            names = []
            for pl in self.players:
                if pl.name not in names:
                    names += [pl.name]
                    new_players += [pl]
            
            self.players = new_players
            # endtodo : very bad hack

            player = max(pl for pl in self.players if pl.game_id == int(player_id))
            player.receive(srv, f'new_hand {message}', client)

        elif message == 'end':
            self.finish()

        elif message.startswith('add_player'):

            _, message = message.split(' ', 1)
            json_message = loads(message)

            curr_id = json_message['id']

            py_cl = None

            print('ADD PLAYERS', self.connected_game.waiting_js_clients)

            for js_cl in self.connected_game.waiting_js_clients.values():
                py_cl = js_cl.connected_python
                print('TESTING ID', py_cl.game_id, curr_id, py_cl.game_id == curr_id)
                if py_cl.game_id == curr_id:
                    self.players += [py_cl]
                    break
                py_cl = None
            
            if py_cl is not None:
                del self.connected_game.waiting_js_clients[py_cl.connected_js.name]

            # todo : very bad hack
            new_players = []
            names = []
            for pl in self.players:
                if pl.name not in names:
                    names += [pl.name]
                    new_players += [pl]
            
            self.players = new_players
            # endtodo : very bad hack

            if curr_id in [curr.game_id for curr in self.players]:
                pl = max(pl for pl in self.players if pl.game_id == curr_id)
                json_message['disconnected'] = pl.is_disconnected
                message = dumps(json_message)

            self.cast(message)

        elif message.startswith('for_replay'):

            _, message = message.split(' ', 1)

            deal_message = dumps({'type': 'deal cards'})
            init_time = self.replay[0][0]

            self.replay[1:1] = [(init_time, deal_message), (init_time, message)]
            self.history += [deal_message]
            self.cast_to_spectators(deal_message)

        elif message.startswith('give_cards'):

            _, player_id, message = message.split(' ', 2)
            player = max(pl for pl in self.players if pl.game_id == int(player_id))
            player.send_to_js(message, True)

        else:
            self.cast(message)

    def left(self, srv: 'Server') -> None:
        del self.connected_game.tb_clients[self.name]

        if self.replay:
            self.hands_history += [self.replay]

        self.connected_game.replays += [(self.name, self.hands, self.hands_history, self.chat_history)]

        for curr_client in self.spectators:
            curr_client.send({'type': 'finish', 'msg': 'Table is closed.'})
            curr_client.finish()

        for curr_client in self.players:
            curr_client.send({'type': 'finish', 'msg': 'Table is closed.'})
            curr_client.finish()

        Debug.client_left('DEL TB')


class ReplayClient(AbstractClient):

    def __init__(self, _id: int, name: str, handler: WebSocketHandler):
        super().__init__(_id, name, handler)

        self.loop: bool = True
        self.message: str = None
        self.thread: Thread = Thread(target=lambda: self.handle_replay())
        self.thread.start()

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

    def handle_replay(self):
        num, table = self.name.split(':')
        hand = 0

        try:
            replays = sorted(listdir('files/replay/poker/games'))

            replay_info = listdir('files/replay/poker/games/' + replays[int(num)])

            table_path = replays[int(num)] + '/' + sorted(replay_info, key=lambda x: int(x.split()[0]))[int(table)]

            table_info = 'files/replay/poker/games/' + table_path

            hand_info = ReplayClient.load_replay(open(table_info + '/0', 'r').read())

            chat_info = 'files/replay/poker/chat/' + table_path

            if exists(chat_info):
                chat_info = ReplayClient.load_replay(open(chat_info).read())
            else:
                chat_info = []

            curr_time = datetime.now()
            start_time = hand_info[0][0]

        except IndexError:
            self.send({'type': 'finish', 'msg': 'Can not find replay for this table.'})
            self.loop = False
            self.finish()

        else:

            curr_action = 0

            while self.loop:

                if exists(table_info + '/' + str(hand)):
                    hand_info = ReplayClient.load_replay(open(table_info + '/' + str(hand), 'r').read())

                    for time, message in hand_info[curr_action:]:

                        while time - start_time > datetime.now() - curr_time:
                            sleep(0.01)

                            if self.message is not None:
                                break

                            if not self.loop:
                                return

                        if self.message is not None:
                            break

                        if not self.loop:
                            return

                        self.send_raw(message)
                        curr_action += 1

                    if self.message is not None:

                        if self.message == 'pause':

                            while True:

                                self.message = None

                                while self.message is None:
                                    sleep(0.01)

                                    if not self.loop:
                                        return

                                if not self.loop:
                                    return

                                if self.message == 'next step':

                                    if curr_action < len(hand_info):
                                        _, message = hand_info[curr_action]
                                        self.send_raw(message)
                                        curr_action += 1

                                    else:
                                        hand += 1
                                        curr_action = 0

                                        if exists(table_info + '/' + str(hand)):
                                            hand_info = ReplayClient.load_replay(
                                                open(table_info + '/' + str(hand), 'r').read())

                                            _, message = hand_info[curr_action]
                                            self.send_raw(message)
                                            curr_action += 1

                                        else:
                                            hand -= 1
                                            self.send({'type': 'info', 'msg': 'It was last hand.'})

                                elif self.message == 'next hand':

                                    hand += 1
                                    curr_action = 0

                                    if exists(table_info + '/' + str(hand)):
                                        hand_info = ReplayClient.load_replay(
                                            open(table_info + '/' + str(hand), 'r').read())

                                        self.send({'type': 'clear'})
                                        time_hand_started, message = hand_info[curr_action]
                                        self.send_raw(message)

                                        chat_start_time = time_hand_started
                                        chat_messages_before_hand = []
                                        for curr_time_chat, curr_chat_msg in chat_info:
                                            if curr_time_chat < chat_start_time:
                                                chat_messages_before_hand += [curr_chat_msg]
                                                if len(chat_messages_before_hand) > 10:
                                                    _, *chat_messages_before_hand = chat_messages_before_hand
                                            else:
                                                break

                                        for chat_message in chat_messages_before_hand:
                                            self.send_raw(chat_message)

                                        curr_action += 1

                                    else:
                                        hand -= 1
                                        self.send({'type': 'info', 'msg': 'It was last hand.'})

                                elif self.message == 'prev hand':

                                    hand -= 1
                                    curr_action = 0

                                    if exists(table_info + '/' + str(hand)):
                                        hand_info = ReplayClient.load_replay(
                                            open(table_info + '/' + str(hand), 'r').read())

                                        self.send({'type': 'clear'})
                                        time_hand_started, message = hand_info[curr_action]
                                        self.send_raw(message)

                                        chat_start_time = time_hand_started
                                        chat_messages_before_hand = []
                                        for curr_time_chat, curr_chat_msg in chat_info:
                                            if curr_time_chat < chat_start_time:
                                                chat_messages_before_hand += [curr_chat_msg]
                                                if len(chat_messages_before_hand) > 10:
                                                    _, *chat_messages_before_hand = chat_messages_before_hand
                                            else:
                                                break

                                        for chat_message in chat_messages_before_hand:
                                            self.send_raw(chat_message)

                                        curr_action += 1

                                    else:
                                        hand += 1
                                        self.send({'type': 'info', 'msg': 'It was first hand.'})

                                elif self.message == 'play':

                                    self.message = None

                                    if curr_action < len(hand_info):
                                        start_time = hand_info[curr_action][0]
                                        curr_time = datetime.now()
                                        break

                                    else:
                                        hand += 1
                                        if exists(table_info + '/' + str(hand)):
                                            hand_info = ReplayClient.load_replay(
                                                open(table_info + '/' + str(hand), 'r').read())

                                            self.send({'type': 'clear'})
                                            curr_action = 0
                                            start_time = hand_info[curr_action][0]
                                            curr_time = datetime.now()
                                        break

                        elif self.message == 'prev hand':

                            self.message = None

                            hand -= 1
                            curr_action = 0

                            if exists(table_info + '/' + str(hand)):
                                hand_info = ReplayClient.load_replay(open(table_info + '/' + str(hand), 'r').read())
                                self.send({'type': 'clear'})
                                start_time = hand_info[curr_action][0]
                                curr_time = datetime.now()

                                chat_start_time = start_time
                                chat_messages_before_hand = []
                                for curr_time_chat, curr_chat_msg in chat_info:
                                    if curr_time_chat < chat_start_time:
                                        chat_messages_before_hand += [curr_chat_msg]
                                        if len(chat_messages_before_hand) > 10:
                                            _, *chat_messages_before_hand = chat_messages_before_hand
                                    else:
                                        break

                                for chat_message in chat_messages_before_hand:
                                    self.send_raw(chat_message)

                            else:
                                hand += 1
                                self.send({'type': 'info', 'msg': 'It was first hand.'})
                                hand_info = ReplayClient.load_replay(open(table_info + '/' + str(hand), 'r').read())
                                self.send({'type': 'clear'})
                                start_time = hand_info[curr_action][0]
                                curr_time = datetime.now()

                        elif self.message == 'next hand':

                            self.message = None

                            hand += 1

                            if exists(table_info + '/' + str(hand)):
                                hand_info = ReplayClient.load_replay(open(table_info + '/' + str(hand), 'r').read())
                                self.send({'type': 'clear'})
                                curr_action = 0
                                start_time = hand_info[curr_action][0]
                                curr_time = datetime.now()

                            else:

                                hand -= 1
                                self.send({'type': 'info', 'msg': 'It was last hand.'})

                            chat_start_time = hand_info[curr_action][0]
                            chat_messages_before_hand = []
                            for curr_time_chat, curr_chat_msg in chat_info:
                                if curr_time_chat < chat_start_time:
                                    chat_messages_before_hand += [curr_chat_msg]
                                    if len(chat_messages_before_hand) > 10:
                                        _, *chat_messages_before_hand = chat_messages_before_hand
                                else:
                                    break

                            for chat_message in chat_messages_before_hand:
                                self.send_raw(chat_message)

                    else:
                        hand += 1
                        curr_action = 0

                else:
                    self.send({'type': 'finish', 'msg': 'Replay ended.'})
                    return

    def receive(self, srv: 'Server', message: str, client: dict) -> None:

        if self.message is None:

            if message == 'pause':
                self.message = 'pause'

            elif message == 'play':
                self.message = 'play'

            elif message == 'next step':
                self.message = 'next step'

            elif message == 'prev hand':
                self.message = 'prev hand'

            elif message == 'next hand':
                self.message = 'next hand'

    def left(self, srv: 'Server'):
        del srv.rp_clients[srv.rp_clients.index(self)]

        self.loop = False
        self.thread.join()
        self.finish()

        Debug.client_left('DEL RP')


class KotlinClient(AbstractClient):

    def __init__(self, _id: int, name: str, handler: WebSocketHandler):
        super().__init__(_id, name, handler)
        self.send({'type': 'connected'})

    def receive(self, srv: 'Server', message: str, client: dict) -> None:
        Debug.from_kt(f'Message from kotlin {self.name}: {message}')

        try:
            json_message = loads(message)

        except JSONDecodeError:
            Debug.from_kt(f'JSON decode error msg from kotlin {self.name} {message}')
            self.send({'type': 'error', 'message': 'not a valid json'})

        else:

            if json_message['type'] == 'close':
                self.finish()

            elif json_message['type'] == 'get replays':
                replays = sorted(listdir('files/replay/poker/games'))
                info = []
                for _id, replay_info in enumerate(replays):

                    rep_split = replay_info.split()

                    if len(rep_split) == 4:
                        date, tables, players, hands = rep_split
                        name = ''

                    else:
                        date, tables, players, hands = rep_split[:4]
                        name = ' '.join(rep_split[4:])

                    info += [{'id': str(_id),
                              'date': date,
                              'tables': int(tables),
                              'players': int(players),
                              'hands': int(hands),
                              'name': name}]

                self.send({'type': 'replays', 'info': info})

            elif json_message['type'] == 'get replay tables' and 'id' in json_message:

                num = json_message['id']

                replays = sorted(listdir('files/replay/poker/games'))
                replay_info = listdir('files/replay/poker/games/' + replays[num])

                info = []
                for rep in replay_info:
                    _id, hands = rep.split()
                    info += [{'id': _id, 'hands': hands}]

                self.send({'type': 'replay tables', 'info': info})

            elif json_message['type'] == 'create tournament' and ('name' in json_message and
                                                                  'total count' in json_message and
                                                                  'bot count' in json_message and
                                                                  'chip count' in json_message and
                                                                  'players' in json_message and
                                                                  'blinds speed' in json_message and
                                                                  'start blinds' in json_message and
                                                                  'password' in json_message):
                srv.game_engine.send(json_message)

            elif json_message['type'] == 'create quick game' and 'name' in json_message:
                srv.game_engine.send(json_message)

            elif json_message['type'] == 'check name' and 'name' in json_message:
                if json_message['name'] in srv.NAMES:
                    answer = 'busy'
                else:
                    answer = 'free'
                self.send({'type': 'check name', 'answer': answer})

            elif json_message['type'] == 'check token' and 'name' in json_message and 'token' in json_message:
                if json_message['name'] not in srv.NAMES or srv.NAMES[json_message['name']] != json_message['token']:
                    answer = 'fail'
                else:
                    answer = 'success'
                    self.name = json_message['name']
                self.send({'type': 'check token', 'answer': answer})

            elif json_message['type'] == 'register name' and 'name' in json_message:
                if json_message['name'] in srv.NAMES:
                    self.send({'type': 'register', 'answer': 'fail'})
                else:
                    token = Key.generate_key()
                    srv.NAMES[json_message['name']] = token
                    open('files/names', 'w').write('\n'.join(dumps({'name': name, 'token': srv.NAMES[name]})
                                                        for name in srv.NAMES))
                    self.name = json_message['name']
                    self.send({'type': 'register', 'answer': 'success', 'token': token})

            elif json_message['type'] == 'change name' and ('token' in json_message and
                                                            'old name' in json_message and
                                                            'new name' in json_message):
                if json_message['old name'] not in srv.NAMES:
                    self.send({'type': 'change name', 'answer': 'fail'})
                elif srv.NAMES[json_message['old name']] != json_message['token']:
                    self.send({'type': 'change name', 'answer': 'fail'})
                else:
                    del srv.NAMES[json_message['old name']]
                    new_token = Key.generate_key()
                    srv.NAMES[json_message['new name']] = new_token
                    open('files/names', 'w').write('\n'.join(dumps({'name': name, 'token': srv.NAMES[name]})
                                                             for name in srv.NAMES))
                    self.name = json_message['new name']
                    self.send({'type': 'change name', 'answer': 'success', 'token': new_token})

            elif json_message['type'] == 'get tournaments' and 'name' in json_message and 'token' in json_message:
                reply = []

                token_fails = json_message['name'] not in srv.NAMES or srv.NAMES[json_message['name']] != json_message['token']

                for game in srv.gh_clients.values():
                    game: GameHandlerClient
                    if game.is_tournament:
                        if token_fails or game.is_game_started:
                            has_player = False
                        else:
                            has_player = game.has_player(json_message['name'])
                        reply += [
                            {
                                'id': game.game_id,
                                'name': game.name,
                                'total players': game.total_players,
                                'initial stack': game.initial_stack,
                                'table seats': game.table_seats,
                                'password': game.password,
                                'players left': game.players_left,
                                'started': game.is_game_started,
                                'can play': has_player
                            }
                        ]
                self.send({'type': 'get tournaments', 'info': reply})

            elif json_message['type'] == 'get tournament tables' and 'id' in json_message:
                reply = []

                if json_message['id'] not in srv.gh_clients:
                    self.send({'type': 'error', 'message': 'no such game id'})
                    return

                game_handler: GameHandlerClient = srv.gh_clients[json_message['id']]

                if not game_handler.is_tournament:
                    self.send({'type': 'error', 'message': 'this game is not tournament'})
                    return

                if not game_handler.is_game_started:
                    self.send({'type': 'error', 'message': 'this game not started'})
                    return

                for table in game_handler.tb_clients.values():
                    table: TableClient
                    reply += [
                        {
                            'id': table.name
                        }
                    ]

                self.send({'type': 'get tournament tables', 'info': reply})

            else:
                self.send({'type': 'error', 'message': 'bad request'})

    def left(self, srv: 'Server') -> None:
        del srv.kt_clients[srv.kt_clients.index(self)]
        Debug.client_left('DEL KT')


class Server:

    if Debug.Debug:
        ip = '127.0.0.1'
        local_ip = '127.0.0.1'

    else:
        ip = '188.134.82.95'
        local_ip = '192.168.0.200'

    port = 9001

    MAX_THINKING_TIME = 60  # Время раздумий в секундах
    MAX_THINKING_TIME_AFTER_KICK = 20  # Время на раздумье после одной просрочки
    START_COUNTING_TIME = 20  # Время с которого начать обратный отсчёт
    MAX_CHAT_LENGTH = 100  # Максимально количество хранимых сообщений в чате и возвращаемых при перезагрузке страницы
    MAX_NICK_LENGTH = 14  # Максимально допустимая длина
    DEFAULT_NICK = 'Anon'  # Если удалось отдать на сервер невалидный ник

    NAMES = dict()
    for name in open('files/names').readlines():
       json_ = loads(name)
       NAMES[json_['name']] = json_['token']

    def __init__(self):

        self.server = WebsocketServer(Server.port, Server.local_ip)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.message_received)

        self.unregistered_clients: Dict[int, UnregisteredClient] = dict()

        self.js_clients: Dict[str, JavaScriptClient] = dict()
        self.py_clients: Dict[str, PythonClient] = dict()
        self.sp_clients: List[SpectatorClient] = []
        self.rp_clients: List[ReplayClient] = []
        self.kt_clients: List[KotlinClient] = []
        self.gh_clients: Dict[int, GameHandlerClient] = dict()

        self.game_engine = None

    def run(self):
        self.server.run_forever()

    # Called for every client connecting (after handshake)
    def new_client(self, client, _):
        Debug.login(f'New client connected and was given id {client["id"]}')
        new_client = UnregisteredClient(client['id'], client['handler'])
        client['client'] = new_client
        self.unregistered_clients[new_client.id] = new_client

    # Called for every client disconnecting
    def client_left(self, client, _):

        if client is None:
            return

        Debug.client_left(f'Client {client["id"]} disconnected')
        try:
            client['client'].left(self)
        except KeyError:
            Debug.error(f'Key error possibly double deleting in client left id = {client["id"]}')
        except ValueError:
            Debug.error(f'Value error possibly double deleting in client left id = {client["id"]}')


    # Called when a client sends a message
    def message_received(self, client, _, message):
        if client is None:
            return
        message = message.encode('ISO-8859-1').decode()
        client['client'].receive(self, message, client)


class Key:

    used_keys_path = 'files/key'

    GetAdmin = open('files/admin').read()
    UsedKeys = open(used_keys_path, 'r').read().split()

    @staticmethod
    def get_random_key():

        while True:
            key = Key.generate_key()

            if key not in Key.UsedKeys:
                break

        Key.UsedKeys += [key]
        Key.save_keys()

        return key

    @staticmethod
    def generate_key():
        return b64encode(urandom(48)).decode().replace('+', '0').replace('/', '1')

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


# ABOUT VISUAL GITHUB

import re
from os import listdir
from os.path import isdir, isfile, join
from bottle import route, run, static_file, template
from github3 import GitHub
from github3.events import Event
from github3.exceptions import NotFoundError
from github3.exceptions import ServerError
from github3.exceptions import ConnectionError
from github3.exceptions import ForbiddenError
from threading import Thread, Lock
from typing import List, Dict
from time import sleep
from datetime import datetime, timedelta
from json import dumps, loads
from json.decoder import JSONDecodeError
from websocket_server import WebsocketServer, WebSocketHandler
from pprint import pprint


event_queue: List[Event] = []
list_to_send: List[dict] = []
events_to_send_lock: Lock = Lock()
event_queue_lock: Lock = Lock()


def get_current_time(git_time) -> datetime:
    now: datetime = datetime.now() - timedelta(hours=3, minutes=5)
    time_to_send = datetime(now.year, now.month, now.day,
                            git_time.hour, git_time.minute, git_time.second)
    return time_to_send + timedelta(hours=3, minutes=5, seconds=30)


def split_repo_name(full_repo_name):
    repo_owner, repo_subname = full_repo_name.split('/', 1)
    return repo_owner, repo_subname


def remove_duplicates():
    if len(list_to_send) < 2:
        return

    duplicate = list_to_send[-1]
    for num, event in enumerate(list_to_send[-2::-1], 1):
        if event['type'] != duplicate['type']:
            continue
        if event['owner'] != duplicate['owner']:
            continue
        if event['repo'] != duplicate['repo']:
            continue
        if event['time'] != duplicate['time']:
            continue

        list_to_send.pop()
        return


def download_events():
    global event_queue

    print('Download events started')

    git = GitHub(token="78424da6d275052ec0cd159497b68ff34c06b1f2")
    print("Requests remaining this hour:", git.ratelimit_remaining, '\n')

    last_event = None
    seconds_to_sleep = 4
    while True:
        try:
            new_events: List[Event] = []
            need_skip = False
            need_reduce_sleep = False
            need_increase_sleep = False
            skipped_events = 0

            for event in git.all_events():
                if not need_skip:
                    if last_event is None or event.id != last_event.id:
                        new_events += [event]
                    else:
                        need_skip = True
                else:
                    skipped_events += 1

            new_events_count = len(new_events)
            if new_events_count > 0:
                if skipped_events / new_events_count < 0.4:
                    need_reduce_sleep = True
                elif skipped_events / new_events_count > 1:
                    need_increase_sleep = True

            if need_reduce_sleep and seconds_to_sleep > 1:
                seconds_to_sleep -= 1
            if need_increase_sleep:
                seconds_to_sleep += 1

            if new_events_count:
                last_event = new_events[0]
            with event_queue_lock:
                event_queue[0:0] = new_events

        except ServerError:
            print("Server error occurred")
        except ConnectionError:
            print("Connection error occurred")
        except ConnectionAbortedError:
            print("Connection aborted error occurred")
        except ForbiddenError:
            print("Forbidden Error")

        with event_queue_lock:
            if len(event_queue):
                pushes = sum(event.type == "PushEvent" for event in event_queue)
                print(f'{event_queue[-1].created_at.time()}-'
                      f'{event_queue[0].created_at.time()}, '
                      f'events: {len(event_queue):>3} '
                      f'pushes: {pushes:>3} '
                      f'sleep: {seconds_to_sleep:>2}s '
                      f'limit: {git.ratelimit_remaining:>4}')

        sleep(seconds_to_sleep)


def handle_events():
    global event_queue, list_to_send, events_to_send_lock

    print('Handle events started')

    while True:
        if len(event_queue) == 0:
            sleep(1)
            continue

        with events_to_send_lock:
            remove_duplicates()

        with event_queue_lock:
            event: Event = event_queue.pop()

        try:

            if event.type == 'PushEvent':

                if not (event.payload['size'] > 0 and event.public):
                    continue

                time_created = event.created_at.time()
                repo_name = event.repo['name']
                repo_owner, repo_subname = repo_name.split('/', 1)
                total_commits = len(event.payload['commits'])
                commit_hash = event.payload['commits'][-1]['sha']
                url = f'https://github.com/{repo_name}/commit/{commit_hash}'

                with events_to_send_lock:
                    list_to_send += [
                        {
                            'type': 'push',
                            'time': get_current_time(time_created),
                            'owner': repo_owner,
                            'repo': repo_subname,
                            'commits': total_commits,
                            'url': url,
                            'hash': commit_hash
                        }
                    ]

            elif event.type == 'PullRequestEvent':

                time_created = event.created_at.time()
                event = event.as_dict()

                url = event['payload']['pull_request']['html_url']
                author = event['actor']['login']
                title = event['payload']['pull_request']['title']
                commits = event['payload']['pull_request']['commits']
                changed = event['payload']['pull_request']['changed_files']

                full_name_repo = event['repo']['name']
                owner, repo = split_repo_name(full_name_repo)

                with events_to_send_lock:
                    list_to_send += [
                        {
                            'type': 'pull_request',
                            'time': get_current_time(time_created),
                            'owner': owner,
                            'repo': repo,
                            'commits': commits,
                            'url': url,
                            'author': author,
                            'title': title,
                            'changed_files': changed
                        }
                    ]

            elif event.type == 'CreateEvent':
                continue

                time_created = event.created_at.time()
                event = event.as_dict()

                url = f'https://github.com/{event["repo"]["name"]}'

                full_name_repo = event['repo']['name']
                owner, repo = split_repo_name(full_name_repo)

                with events_to_send_lock:
                    list_to_send += [
                        {
                            'type': 'create_repo',
                            'time': get_current_time(time_created),
                            'owner': owner,
                            'repo': repo,
                            'url': url
                        }
                    ]

            elif event.type == 'ForkEvent':

                time_created = event.created_at.time()
                event = event.as_dict()

                url = event['payload']['forkee']['html_url']
                full_name_repo = event['payload']['forkee']['full_name']
                owner, repo = split_repo_name(full_name_repo)

                with events_to_send_lock:
                    list_to_send += [
                        {
                            'type': 'fork_repo',
                            'time': get_current_time(time_created),
                            'owner': owner,
                            'repo': repo,
                            'url': url
                        }
                    ]

            elif event.type == 'WatchEvent':
                pass

            elif event.type == 'IssuesEvent':

                time_created = event.created_at.time()
                event = event.as_dict()
                url = event['payload']['issue']['html_url']
                owner, repo = split_repo_name(event['repo']['name'])

                with events_to_send_lock:
                    list_to_send += [
                        {
                            'type': 'issue',
                            'time': get_current_time(time_created),
                            'owner': owner,
                            'repo': repo,
                            'url': url
                        }
                    ]

            elif event.type == 'DeleteEvent':
                pass

            elif event.type == 'IssueCommentEvent':

                time_created = event.created_at.time()
                event = event.as_dict()
                owner, repo = split_repo_name(event['repo']['name'])
                url = event['payload']['comment']['html_url']

                with events_to_send_lock:
                    list_to_send += [
                        {
                            'type': 'issue_comment',
                            'time': get_current_time(time_created),
                            'owner': owner,
                            'repo': repo,
                            'url': url
                        }
                    ]

            elif event.type == 'PullRequestReviewCommentEvent':

                time_created = event.created_at.time()
                event = event.as_dict()
                owner, repo = split_repo_name(event['repo']['name'])
                url = event['payload']['comment']['html_url']

                with events_to_send_lock:
                    list_to_send += [
                        {
                            'type': 'pull_request_review',
                            'time': get_current_time(time_created),
                            'owner': owner,
                            'repo': repo,
                            'url': url
                        }
                    ]

            elif event.type == 'GollumEvent':

                time_created = event.created_at.time()
                event = event.as_dict()
                owner, repo = split_repo_name(event['repo']['name'])

                if len(event['payload']['pages']) == 0:
                    continue

                url = event['payload']['pages'][-1]['html_url']

                with events_to_send_lock:
                    list_to_send += [
                        {
                            'type': 'wiki_page',
                            'time': get_current_time(time_created),
                            'owner': owner,
                            'repo': repo,
                            'url': url
                        }
                    ]

            elif event.type == 'ReleaseEvent':

                time_created = event.created_at.time()
                event = event.as_dict()
                owner, repo = split_repo_name(event['repo']['name'])
                url = event['payload']['release']['html_url']

                with events_to_send_lock:
                    list_to_send += [
                        {
                            'type': 'release',
                            'time': get_current_time(time_created),
                            'owner': owner,
                            'repo': repo,
                            'url': url
                        }
                    ]

            elif event.type == 'PublicEvent':
                pass

            elif event.type == 'CommitCommentEvent':

                time_created = event.created_at.time()
                event = event.as_dict()
                owner, repo = split_repo_name(event['repo']['name'])
                url = event['payload']['comment']['html_url']

                with events_to_send_lock:
                    list_to_send += [
                        {
                            'type': 'commit_comment',
                            'time': get_current_time(time_created),
                            'owner': owner,
                            'repo': repo,
                            'url': url
                        }
                    ]

            elif event.type == 'MemberEvent':
                pass

            else:
                pprint(event.as_dict())
                pass

        except NotFoundError:
            pass

        except JSONDecodeError:
            pass


def send_events():

    print('Send events started')

    global list_to_send

    while True:

        for item in list_to_send:
            cur_time: datetime = item['time']
            same_time_list = [i for i in list_to_send if i['time'] == cur_time]
            if len(same_time_list) > 1:

                divider = len(same_time_list)
                for i, same_item in enumerate(same_time_list):
                    increase = timedelta(milliseconds=i / divider * 1000)
                    same_item['time'] += increase

        now = datetime.now()

        with events_to_send_lock:
            list_to_send_now = [i for i in list_to_send if i['time'] < now]
            list_to_send = [i for i in list_to_send if i['time'] >= now]

        for send_item in list_to_send_now:
            # print('send', send_item['time'])
            del send_item['time']
            websocket_server.broadcast(send_item)

        sleep(0.01)


class DebugLog:
    Debug = Debug.Debug
    Send = 0
    Connected = 1
    ClientLeft = 1
    Errors = 1

    if Send:
        @staticmethod
        def send(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def send(*args, **kwargs):
            pass

    if Connected:
        @staticmethod
        def connected(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def connected(*args, **kwargs):
            pass

    if ClientLeft:
        @staticmethod
        def client_left(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def client_left(*args, **kwargs):
            pass

    if Errors:
        @staticmethod
        def error(*args, **kwargs):
            print(*args, **kwargs)
    else:
        @staticmethod
        def error(*args, **kwargs):
            pass


class VisualGithubClient:

    def __init__(self, _id: int, handler: WebSocketHandler):
        # Это внутренний ID клиента, присваиваемый сервером
        self.id: int = _id
        self.handler: WebSocketHandler = handler
        self.owner_filter = re.compile('')
        self.repo_filter = re.compile('')
        self.type_filters = {
            'pull_request': False,
            'push': False,
            'issue': False,
            'fork_repo': False,
            'wiki_page': False,
            'release': False,
            'pull_request_review': False,
            'commit_comment': False,
            'issue_comment': False
        }

        self.send({
            'type': 'init',
            'categories': audio_lengths
        })

    def finish(self):
        try:
            self.handler.finish()
        except KeyError:
            DebugLog.error(f'Key error possibly double '
                           f'deleting id = {self.id}')

    def send(self, obj: dict) -> None:
        try:
            msg = dumps(obj)
            DebugLog.send(f'Send to {self.id}: {msg}')
            self.handler.send_message(msg)
        except BrokenPipeError:
            DebugLog.error(f'Broken pipe error send id = {self.id}')

    def pass_filters(self, event: dict):
        return self.pass_type_filters(event) and self.pass_regexp_filters(event)

    def pass_type_filters(self, event: dict):
        return self.type_filters[event['type']]

    def set_type_filters(self, event: dict):
        del event['type']
        for curr_type in event:
            self.type_filters[curr_type] = event[curr_type]

    def pass_regexp_filters(self, event: dict):
        owner_match = self.owner_filter.fullmatch(event['owner']) is not None
        repo_match = self.repo_filter.fullmatch(event['repo']) is not None
        return owner_match and repo_match

    def set_regexp_filters(self, owner: str, repo: str):
        try:
            owner = owner.lower()
            if owner == '':
                owner = '.*'
            self.owner_filter = re.compile(owner, re.IGNORECASE)
        except re.error:
            self.send({
                'type': 'error',
                'where': 'owner'
            })

        try:
            repo = repo.lower()
            if repo == '':
                repo = '.*'
            self.repo_filter = re.compile(repo, re.IGNORECASE)
        except re.error:
            self.send({
                'type': 'error',
                'where': 'repo'
            })

    def receive(self, srv: 'WebSocketServer', message: str, client: dict):
        try:
            json_msg = loads(message)
            if json_msg['type'] == 'filter_regexp':
                self.set_regexp_filters(json_msg['owner'], json_msg['repo'])
            elif json_msg['type'] == 'filter_types':
                self.set_type_filters(json_msg)
        except JSONDecodeError:
            print('JSONDecodeError', message)

    def left(self, srv: 'WebSocketServer') -> None:
        del srv.clients[self.id]
        # Debug.client_left('DEL VISUAL GITHUB', self.id)


class WebSocketServer:

    if DebugLog.Debug:
        ip = '127.0.0.1'
        local_ip = '127.0.0.1'

    else:
        ip = '188.134.82.95'
        local_ip = '192.168.0.200'

    port = 11001

    def __init__(self):

        self.server = WebsocketServer(WebSocketServer.port, WebSocketServer.local_ip)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_client_left(self.client_left)
        self.server.set_fn_message_received(self.message_received)

        self.clients: Dict[int, VisualGithubClient] = {}

    def run(self):
        self.server.run_forever()

    # Called for every client connecting (after handshake)
    def new_client(self, client, _):
        DebugLog.connected(f'New client connected '
                        f'and was given id {client["id"]}')
        new_client = VisualGithubClient(client['id'], client['handler'])
        client['client'] = new_client
        self.clients[new_client.id] = new_client

    # Called for every client disconnecting
    def client_left(self, client, _):

        if client is None:
            return

        DebugLog.client_left(f'Client {client["id"]} disconnected')
        try:
            client['client'].left(self)
        except KeyError:
            DebugLog.error(f'Key error possibly double deleting '
                           f'in client left id = {client["id"]}')
        except ValueError:
            DebugLog.error(f'Value error possibly double deleting '
                           f'in client left id = {client["id"]}')

    # Called when a client sends a message
    def message_received(self, client, _, message):
        if client is None:
            return
        message = message.encode('ISO-8859-1').decode()
        client['client'].receive(self, message, client)

    def broadcast(self, message: dict):
        for client in list(self.clients.values()):
            if client.pass_filters(message):
                client.send(message)


def get_audio_files():
    files = {}
    for folder in listdir('static/github/audio'):
        full_folder = join('static/github/audio', folder)
        if not isdir(full_folder):
            continue
        for file in listdir(full_folder):
            full_file = join(full_folder, file)
            if not isfile(full_file) or not file.endswith('.mp3'):
                continue
            if folder not in files:
                files[folder] = []
            static, *other_path = full_folder.split('/')
            files[folder] += [join('/'.join(other_path), file)]
    return files


audio_files = get_audio_files()
audio_lengths = {folder: len(audio_files[folder]) for folder in sorted(audio_files.keys(), key=lambda x: x.lower())}
audio_lengths = dumps(audio_lengths)


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
        if 'github' in file and file.endswith('.mp3'):
            path = file.split('/')
            filename = path[-1]
            folder = path[-2]
            file_num = filename.split('.')[0]  # without ".mp3"
            print(filename, file_num, folder)
            file = audio_files[folder][int(file_num)]

            print(file)

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

        if server.game_engine is None:
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

        if server.game_engine is None:
            redirect('/poker')

        elif key not in Key.UsedKeys:
            abort(401, "Sorry, access denied.")

        else:
            return template('static/poker/create/create.html', ip=KeyServer.ip, port=KeyServer.port)

    @route('/poker/create/c')
    def create():

        key = request.query.key if 'key' in request.query else 'no key'

        if server.game_engine is None:
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

        if server.game_engine is None:
            redirect('/poker')

        elif key not in Key.UsedKeys:
            abort(401, "Sorry, access denied.")

        else:
            server.send_http('break')
            sleep(1)
            redirect('/poker')

    @route('/poker/watch')
    def poker_tables():

        if server.game_engine is None or not server.is_game_started:
            redirect('/poker')

        else:

            info = []

            tables: List[TableClient] = list(server.tb_clients.values())

            if len(tables) == 1:
                return template('static/poker/play/poker.html',
                                name='', table=tables[0].name,
                                replay='', back_addr='/poker',
                                ip=Server.ip, port=Server.port)

            else:
                for client in server.tb_clients.values():
                    info += [client.name]

                return template('static/poker/watch/watch.html', info=info)

    @route('/poker/replay')
    def poker_replays():

        replays = sorted(listdir('files/replay/poker/games'))

        info = []

        for _id, replay_info in enumerate(replays):

            rep_split = replay_info.split()

            if len(rep_split) == 4:
                date, tables, players, hands = rep_split
                name = ''

            else:
                date, tables, players, hands = rep_split[:4]
                name = ' '.join(rep_split[4:])

            info += [(str(_id), date, tables, players, hands, name)]

        return template('static/poker/replay/replays.html', info=info)


    @route('/poker/replay/<num:int>')
    def replay_chose_table(num):

        replays = sorted(listdir('files/replay/poker/games'))

        replay_info = listdir('files/replay/poker/games/' + replays[num])

        if len(replay_info) == 1:
            return template('static/poker/play/poker.html',
                            name='', table='', replay='%s:%s' % (num, replay_info[0].split()[0]),
                            back_addr='/poker/replay', ip=Server.ip, port=Server.port)

        else:
            info = []
            for rep in replay_info:

                _id, hands = rep.split()
                info += [(_id, hands)]

            return template('static/poker/replay/tables.html', info=sorted(info, key=lambda x: int(x[0])))

    @route('/poker/replay/<num:int>/<table:int>')
    def replay_mode(num, table):
        return template('static/poker/play/poker.html', name='', table='', replay='%s:%s' % (num, table),
                        back_addr='/poker/replay/%s' % (num,), ip=Server.ip, port=Server.port)

    @route('/poker/play/<name>')
    def player_mode(name):
        return template('static/poker/play/poker.html', name=name, table='', replay='', back_addr='/poker',
                        ip=Server.ip, port=Server.port)

    @route('/poker/watch/<table:int>')
    def spectate_mode(table):
        return template('static/poker/play/poker.html', name='', table=table, replay='', back_addr='/poker/watch',
                        ip=Server.ip, port=Server.port)

    @error(404)
    def error404(_error):

        with open("files/404.txt", "a", encoding="utf-8") as file:
            file.write(_error.body.split("'")[1] + '\n')

        return template(ERROR_PAGE_TEMPLATE, e=_error)

    @route('/lib/<file:path>')
    def static_serve(file):
        return static_file(file, root='lib')


    websocket_server = WebSocketServer()
    Thread(target=lambda: websocket_server.run(), name='WebSocket server').start()
    Thread(target=download_events, name="Download events").start()
    Thread(target=handle_events, name="Handle events").start()
    Thread(target=send_events, name="Send events").start()

    @route('/github')
    def github():
        return template('static/github/frontend.html',
                        ip=WebSocketServer.ip, port=WebSocketServer.port, audio_size=len(audio_files))

    run(host=Server.local_ip, port=80)
