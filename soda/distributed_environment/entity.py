from zmq import Context, REP, REQ, DONTWAIT, Poller, POLLIN
from threading import Thread
from pickle import dumps, loads
from logging import getLogger
from soda.helpers import support_arguments
from soda.distributed_environment.behavior import ActionNode, IfNode

logger = getLogger(__name__)


class Entity(Thread):
    def __init__(self, id_e, ip, in_port, state, term_states, states_behaviors, neighbours):
        Thread.__init__(self)
        self.id_e = id_e
        self.ip = ip
        self.in_port = in_port
        self.state = state
        self.term_states = term_states
        self.states_behaviors = states_behaviors
        self.neighbours = neighbours
        self.impulse = False

        context = Context()
        self.in_socket = context.socket(REP)
        self.in_socket.bind("tcp://*:%s" % self.in_port)

        poller = Poller()
        poller.register(self.in_socket, POLLIN)


        def read():
            while True:
                socks = dict(poller.poll())

                if socks.get(self.in_socket) == POLLIN:
                    pickled_received_message = self.in_socket.recv(flags=DONTWAIT)
                    received_message, sender_entity_id_e = loads(pickled_received_message)

                    for pattern in list(filter(lambda p: p != 'IMPULSE', self.states_behaviors[self.state])):

                        result = []

                        if len(pattern[1]) == len(received_message):
                            for i, j in zip(pattern[1], received_message):
                                if i == j and type(i) is not tuple:
                                    result.append(True)
                                elif i != j and type(i) is not tuple:
                                    result.append(False)
                                else:
                                    result.append(None)

                            if False not in result:
                                for i, j in zip(pattern[1], received_message):
                                    if type(i) is tuple:
                                        _identifier, _ = i
                                        _expression = "%s = %s" % (_identifier, j)

                                        self.actions["ASSIGN"]((_expression, ))

                                logger.info("Entity: {0} | Action: READ | Message : {1} | From entity : {2} ".format(self.id_e, received_message, sender_entity_id_e))

                                return pattern

        @support_arguments
        def send(message):
            message = eval(str(message), {}, self.__dict__)

            if type(message) is str:
                message = (message[:], )

            for n in self.neighbours:
                for e in n:
                    out_socket = context.socket(REQ)
                    out_socket.connect("tcp://localhost:%s" % n[e]["in_port"])
                    message_content = (message, self.id_e)
                    pickled_message = dumps(message_content)
                    out_socket.send(pickled_message, flags=DONTWAIT)
                    logger.info("Entity: {0} | Action: SEND | Message : {1} | To entity : {2} ".format(self.id_e, message, e))

        @support_arguments
        def become(new_state):
            logger.info("Entity: {0} | Action: BECOME | Old state : {1} | New state : {2} ".format(self.id_e, self.state, new_state))
            self.state = new_state

            if self.state in self.term_states:
                exit()

        @support_arguments
        def assign(expression):
            exec(expression, {}, self.__dict__)
            logger.info("Entity: {0} | Action: ASSIGN | Expression : {1} ".format(self.id_e, expression))

        self.actions = {
            "READ": read,
            "SEND": send,
            "BECOME": become,
            "ASSIGN": assign
        }

    def run(self):
        while self.state not in self.term_states:
            behavior = None
            current_state = self.state

            if self.impulse:
                self.impulse = False
                behavior = 'IMPULSE'
            else:
                behavior = self.actions["READ"]()

            n = self.states_behaviors[current_state][behavior].head
            next_node = None
            while n is not None:
                if type(n) is ActionNode:
                    next_node = n.execute(self)
                elif type(n) is IfNode:
                    next_node = n.execute(self)

                n = next_node