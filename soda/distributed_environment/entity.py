from zmq import Context, DONTWAIT, Poller, POLLIN, DEALER
from threading import Thread
from pickle import dumps, loads
from logging import getLogger
from soda.helpers import support_arguments
from soda.distributed_environment.behavior import ActionNode, IfNode

_logger = getLogger(__name__)


class Entity(Thread):
    def __init__(_self, _id, _ip, _in_port, _state, _term_states, _states_behaviors, _neighbours):
        Thread.__init__(_self)
        _self._id = _id
        _self._ip = _ip
        _self._in_port = _in_port
        _self._state = _state
        _self._term_states = _term_states
        _self._states_behaviors = _states_behaviors
        _self._neighbours = _neighbours
        _self._impulse = False

        _context = Context()
        _self._in_socket = _context.socket(DEALER)
        _self._in_socket.bind("tcp://*:%s" % _self._in_port)

        _poller = Poller()
        _poller.register(_self._in_socket, POLLIN)

        _self.ID = int(_id)
        _self.NEIGHBOURS = [_n for _n in _neighbours]


        def read():
            while True:
                _socks = dict(_poller.poll())

                if _socks.get(_self._in_socket) == POLLIN:
                    _pickled_received_message = _self._in_socket.recv(flags=DONTWAIT)
                    _received_message, _sender_entity_id = loads(_pickled_received_message)

                    _logger.info("Entity: {0} | Action: RECEIVED | Message : {1} | From entity : {2} ".format(_self._id,
                                                                                                         _received_message,
                                                                                                         _sender_entity_id))

                    for _pattern in list(filter(lambda _p: _p != 'IMPULSE', _self._states_behaviors[_self._state])):
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

                                        _self._actions["ASSIGN"]((_expression, ))

                                _logger.info("Entity: {0} | Action: READ | Message : {1} | From entity : {2} ".format(_self._id, _received_message, _sender_entity_id))

                                return _pattern

        @support_arguments
        def send(_message):
            _message = eval(str(_message), {}, _self.__dict__)

            if type(_message) is str:
                _message = (_message[:], )

            for _n in _self._neighbours:
                _out_socket = _context.socket(DEALER)
                _out_socket.connect("tcp://localhost:%s" % _self._neighbours[_n]["in_port"])
                _message_content = (_message, _self._id)
                _pickled_message = dumps(_message_content)
                _out_socket.send(_pickled_message, flags=DONTWAIT)
                _logger.info("Entity: {0} | Action: SEND | Message : {1} | To entity : {2} ".format(_self._id, _message, _n))

        @support_arguments
        def become(_new_state):
            _logger.info("Entity: {0} | Action: BECOME | Old state : {1} | New state : {2} ".format(_self._id, _self._state, _new_state))
            _self._state = _new_state

            if _self._state in _self._term_states:
                exit()

        @support_arguments
        def assign(_expression):
            exec(_expression, {}, _self.__dict__)
            _logger.info("Entity: {0} | Action: ASSIGN | Expression : {1} ".format(_self._id, _expression))

        _self._actions = {
            "READ": read,
            "SEND": send,
            "BECOME": become,
            "ASSIGN": assign
        }

    def run(_self):
        while _self._state not in _self._term_states:
            _current_state = _self._state

            if _self._impulse:
                _self._impulse = False
                _behavior = 'IMPULSE'
            else:
                _behavior = _self._actions["READ"]()

            _n = _self._states_behaviors[_current_state][_behavior].head
            _next_node = None
            while _n is not None:
                if type(_n) is ActionNode:
                    _next_node = _n.execute(_self)
                elif type(_n) is IfNode:
                    _next_node = _n.execute(_self)

                _n = _next_node