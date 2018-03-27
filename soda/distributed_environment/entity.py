from zmq import Context, DONTWAIT, Poller, POLLIN, DEALER
from threading import Thread
from pickle import dumps, loads
from logging import getLogger
from soda.helpers import support_arguments
from soda.distributed_environment.behavior import ActionNode, IfNode

_logger = getLogger(__name__)


class Entity(Thread):
    def __init__(self, _id, _ip, _in_port, _state, _term_states, _states_behaviors, _neighbours):
        Thread.__init__(self)
        self._id = _id
        self._ip = _ip
        self._in_port = _in_port
        self._state = _state
        self._term_states = _term_states
        self._states_behaviors = _states_behaviors
        self._neighbours = _neighbours
        self._impulse = False

        _context = Context()
        self._in_socket = _context.socket(DEALER)
        self._in_socket.bind("tcp://*:%s" % self._in_port)

        _poller = Poller()
        _poller.register(self._in_socket, POLLIN)

        self.id = int(_id)


        def read():
            while True:
                _socks = dict(_poller.poll())

                if _socks.get(self._in_socket) == POLLIN:
                    _pickled_received_message = self._in_socket.recv(flags=DONTWAIT)
                    _received_message, _sender_entity_id = loads(_pickled_received_message)

                    _logger.info("Entity: {0} | Action: RECEIVED | Message : {1} | From entity : {2} ".format(self._id,
                                                                                                         _received_message,
                                                                                                         _sender_entity_id))

                    for _pattern in list(filter(lambda _p: _p != 'IMPULSE', self._states_behaviors[self._state])):

                        _result = []

                        if len(_pattern[1]) == len(_received_message):
                            for _i, _j in zip(_pattern[1], _received_message):
                                if _i == _j and type(_i) is not tuple:
                                    _result.append(True)
                                elif _i != _j and type(_i) is not tuple:
                                    _result.append(False)
                                else:
                                    _result.append(None)

                            if False not in _result:
                                for _i, _j in zip(_pattern[1], _received_message):
                                    if type(_i) is tuple:
                                        _identifier, _ = _i
                                        _expression = "%s = %s" % (_identifier, _j)

                                        self._actions["ASSIGN"]((_expression, ))

                                _logger.info("Entity: {0} | Action: READ | Message : {1} | From entity : {2} ".format(self._id, _received_message, _sender_entity_id))

                                return _pattern

        @support_arguments
        def send(_message):
            _message = eval(str(_message), {}, self.__dict__)

            if type(_message) is str:
                _message = (_message[:], )

            for _n in self._neighbours:
                for _e in _n:
                    _out_socket = _context.socket(DEALER)
                    _out_socket.connect("tcp://localhost:%s" % _n[_e]["in_port"])
                    _message_content = (_message, self._id)
                    _pickled_message = dumps(_message_content)
                    _out_socket.send(_pickled_message, flags=DONTWAIT)
                    _logger.info("Entity: {0} | Action: SEND | Message : {1} | To entity : {2} ".format(self._id, _message, _e))

        @support_arguments
        def become(_new_state):
            _logger.info("Entity: {0} | Action: BECOME | Old state : {1} | New state : {2} ".format(self._id, self._state, _new_state))
            self._state = _new_state

            if self._state in self._term_states:
                exit()

        @support_arguments
        def assign(_expression):
            exec(_expression, {}, self.__dict__)
            _logger.info("Entity: {0} | Action: ASSIGN | Expression : {1} ".format(self._id, _expression))

        self._actions = {
            "READ": read,
            "SEND": send,
            "BECOME": become,
            "ASSIGN": assign
        }

    def run(self):
        while self._state not in self._term_states:
            _behavior = None
            _current_state = self._state

            if self._impulse:
                self._impulse = False
                _behavior = 'IMPULSE'
            else:
                _behavior = self._actions["READ"]()

            _n = self._states_behaviors[_current_state][_behavior].head
            _next_node = None
            while _n is not None:
                if type(_n) is ActionNode:
                    _next_node = _n.execute(self)
                elif type(_n) is IfNode:
                    _next_node = _n.execute(self)

                _n = _next_node