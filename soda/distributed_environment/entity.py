from zmq import Context, DONTWAIT, Poller, POLLIN, DEALER
from threading import Thread
from pickle import dumps, loads
from logging import getLogger
from soda.helpers import support_arguments
from soda.distributed_environment.behavior import ActionNode, IfNode
from subprocess import run, PIPE
from shlex import split
from copy import deepcopy

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
        _self._read_lock = False
        _self._count_sent_messages = 0

        _context = Context()
        _self._in_socket = _context.socket(DEALER)
        _self._in_socket.bind("tcp://*:%s" % _self._in_port)

        _poller = Poller()
        _poller.register(_self._in_socket, POLLIN)

        _self.i_ID = int(_id)
        _self.i_NEIGHBOURS = [_n for _n in _neighbours]

        _self.__dict__['deepcopy'] = deepcopy
        _self.__dict__['LEN'] = len


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

                                        if type(_j) is str:
                                            _j = "'" + _j + "'"

                                        _expression = "%s = %s" % (_identifier, _j)

                                        _self._actions["ASSIGN"]((_expression, ))

                                # store sender id to usable identifier
                                _self.i_SENDER = _sender_entity_id

                                _logger.info("Entity: {0} | Action: READ | Message : {1} | From entity : {2} ".format(_self._id, _received_message, _sender_entity_id))

                                return _pattern

        @support_arguments
        def send(_message, _recipients):
            _message = _self._actions["EVALUATE"](str(_message))
            _recipients = _self._actions["EVALUATE"](str(_recipients))

            if type(_message) is not tuple:
                _message = (_message, )

            if type(_recipients) is int:
                _recipients = [_recipients] * 1

            for _n in _recipients:
                try:
                    _out_socket = _context.socket(DEALER)
                    _out_socket.connect("tcp://localhost:%s" % _self._neighbours[_n]["in_port"])
                    _message_content = (_message, _self._id)
                    _pickled_message = dumps(_message_content)
                    _out_socket.send(_pickled_message, flags=DONTWAIT)

                    _logger.info("Entity: {0} | Action: SEND | Message : {1} | To entity : {2} ".format(_self._id, _message, _n))
                    _self._count_sent_messages += 1
                except KeyError:
                    _logger.info("Entity: {0} | Action: SEND | Trying to send message to non existing neighbour! -> {1} ".format(_self._id, _n))

        @support_arguments
        def become(_new_state):
            _logger.info("Entity: {0} | Action: BECOME | Old state : {1} | New state : {2} ".format(_self._id, _self._state, _new_state))
            _self._state = _new_state

            if _self._state in _self._term_states:
                exit()

        @support_arguments
        def assign(_expression):
            try:
                exec(_expression, {}, _self.__dict__)
                _logger.info("Entity: {0} | Action: ASSIGN | Expression : {1} ".format(_self._id, _expression))
            except NameError as _Name:
                _logger.info("Entity: {0} | Action: ASSIGN | Undefined identifier! -> {1} -> {2} ".format(_self._id, _Name, _expression))
                exit()
            except AttributeError as _Attribute:
                _logger.info("Entity: {0} | Action: ASSIGN | Wrong type of identifier! -> {1} -> {2} ".format(_self._id, _Attribute, _expression))
                exit()
            except TypeError as _Type:
                _logger.info("Entity: {0} | Action: ASSIGN | Wrong type of identifier! -> {1} -> {2} ".format(_self._id, _Type, _expression))
                exit()

        @support_arguments
        def log(_expression):
            print("SODA: " + _self._actions["EVALUATE"](_expression))

        def evaluate(_expression):
            result = None

            try:
                result = eval(_expression, {}, _self.__dict__)
            except NameError as _Name:
                _logger.info("Entity: {0} | Action: EVALUATE | Undefined identifier! -> {1} -> {2}  ".format(_self._id, _Name, _expression))
                exit()
            except AttributeError as _Attribute:
                _logger.info("Entity: {0} | Action: EVALUATE | Wrong type of identifier! -> {1} -> {2}  ".format(_self._id, _Attribute, _expression))
                exit()
            except ValueError as _Value:
                _logger.info("Entity: {0} | Action: EVALUATE | Wrong value! -> {1} -> {2}  ".format(_self._id, _Value,_expression))
                exit()

            return result

        @support_arguments
        def execute(_command, _output_type,  _output, _input):
            _command = split(_command)
            _input = _self._actions["EVALUATE"](str(_input))
            _process_output= None

            _completed_process = run(_command, input=str(_input), stdout=PIPE, universal_newlines=True, shell=True)

            # cast to correct output type
            if _output_type == 'string':
                _process_output  = "'" + _completed_process.stdout + "'"
            elif _output_type == 'int':
                try:
                    _process_output = int(_completed_process.stdout)
                except ValueError as _Value:
                    _logger.info(
                        "Entity: {0} | Action: EXEC | Wrong value for output cast to int! -> {1} -> {2}  ".format(_self._id, _Value,
                                                                                               _completed_process.stdout))
                    exit()
            elif _output_type == 'float':
                try:
                    _process_output = float(_completed_process.stdout)
                except  ValueError as _Value:
                    _logger.info(
                        "Entity: {0} | Action: EXEC | Wrong value for output cast to float! -> {1} -> {2}  ".format(_self._id, _Value,
                                                                                               _completed_process.stdout))
                    exit()

            _expression = "%s = %s" % (_output, _process_output)
            _self._actions["ASSIGN"]((_expression,))

        @support_arguments
        def add(_array, _value):
            _expression = "%s.append(%s)" % (_array, _value)
            _self._actions["EVALUATE"](str(_expression))

        @support_arguments
        def remove(_array, _value):
            _expression = "%s.remove(%s)" % (_array, _value)
            _self._actions["EVALUATE"](str(_expression))

        @support_arguments
        def pop(_array, _output):
            _expression = "%s = %s.pop()" % (_output, _array)
            _self._actions["ASSIGN"]((_expression,))

        _self._actions = {
            "READ": read,
            "SEND": send,
            "BECOME": become,
            "ASSIGN": assign,
            "LOG": log,
            "EVALUATE": evaluate,
            "EXEC": execute,
            "ADD": add,
            "REMOVE": remove,
            "POP": pop
        }

    def run(_self):
        while _self._state not in _self._term_states:
            _current_state = _self._state

            if _self._impulse:
                _self._impulse = False
                _behavior = 'IMPULSE'

                _logger.info("Entity: {0} | Action: Started by IMPULSE ".format(_self._id))
            else:
                _self._read_lock = True
                _behavior = _self._actions["READ"]()
                _self._read_lock = False

            _n = _self._states_behaviors[_current_state][_behavior].head
            _next_node = None
            while _n is not None:
                if type(_n) is ActionNode:
                    _next_node = _n.execute(_self)
                elif type(_n) is IfNode:
                    _next_node = _n.execute(_self)

                if _next_node == "BECOME":
                    break

                _n = _next_node