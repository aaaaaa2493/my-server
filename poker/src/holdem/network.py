from typing import Optional, List
from json import loads, dumps
from websocket import create_connection
from holdem.play.result import Result
from holdem.base_network import BaseNetwork
from special.debug import Debug


class Network(BaseNetwork):

    if Debug.Debug:
        ip = '127.0.0.1'

    else:
        ip = '188.134.82.95'

    port = 9001

    def __init__(self, identifier: dict):
        super().__init__()

        self.need_disconnect_info = True

        self.socket = create_connection(f'ws://{Network.ip}:{Network.port}')
        self.socket.send(dumps(identifier))

    def __del__(self):
        if self.socket.connected:
            self.socket.close()

    def send(self, obj: dict) -> None:
        if self.socket.connected:
            self.socket.send(dumps(obj))

    def send_raw(self, text: str) -> None:
        if self.socket.connected:
            self.socket.send(text)

    def receive(self) -> dict:
        if self.socket.connected:
            return loads(self.socket.recv())

    def receive_raw(self) -> str:
        if self.socket.connected:
            return self.socket.recv()

    def input_decision(self, available) -> Optional[List[str]]:

        to_send = dict()

        to_send['type'] = 'set decision'

        decisions = list()

        for decision in available:

            curr = dict()

            if decision[0] == Result.Fold:
                curr['type'] = 'fold'

            elif decision[0] == Result.Check:
                curr['type'] = 'check'

            elif decision[0] == Result.Call:
                curr['type'] = 'call'
                curr['money'] = decision[1]

            elif decision[0] == Result.Raise:
                curr['type'] = 'raise'
                curr['from'] = decision[1]
                curr['to'] = decision[2]

            elif decision[0] == Result.Allin:
                curr['type'] = 'all in'
                curr['money'] = decision[1]

            else:
                raise ValueError(f'THERE IS ANOTHER DECISION {decision[0]}')

            decisions += [curr]

        to_send['decisions'] = decisions

        self.send_raw(f'decision {dumps(to_send)}')

        reply = self.receive_raw()

        if reply is None:
            reply = '1'

        return reply.split()

    def busted(self, place: int) -> None:
        self.send_raw('busted')
        self.send({'type': 'busted', 'place': place})
        self.socket.close()

    def win(self) -> None:
        self.send({'type': 'win'})
        self.socket.close()
