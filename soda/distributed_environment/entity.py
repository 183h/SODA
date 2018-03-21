from zmq import Context, REP, REQ, DONTWAIT, Poller, POLLIN
from threading import Thread
from pickle import dumps, loads
from logging import getLogger
from soda.helpers import support_arguments
from soda.distributed_environment.behavior import ActionNode, IfNode

logger = getLogger(__name__)


class Entity(Thread):
    def __init__(self, id_e, ip, in_port, state, term_states, behaviors, neighbours):
        Thread.__init__(self)
        self.id_e = id_e
        self.ip = ip
        self.in_port = in_port
        self.state = state
        self.term_states = term_states
        self.behaviors = behaviors
        self.neighbours = neighbours

        context = Context()
        self.in_socket = context.socket(REP)
        self.in_socket.bind("tcp://*:%s" % self.in_port)

        poller = Poller()
        poller.register(self.in_socket, POLLIN)

        @support_arguments
        def read(message):
            message = eval(message, {}, self.__dict__) if message is not None else None

            while True:
                socks = dict(poller.poll())

                if socks.get(self.in_socket) == POLLIN:
                    pickled_received_message = self.in_socket.recv(flags=DONTWAIT)
                    received_message, sender_entity_id_e = loads(pickled_received_message)

                    if received_message == message or message is None:
                        logger.info("Entity: {0} | Action: READ | Message : {1} | From entity : {2} ".format(self.id_e, received_message, sender_entity_id_e))
                        break

        @support_arguments
        def send(message):
            message = eval(message, {}, self.__dict__)

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

        self.actions = {
            "READ": read,
            "SEND": send,
            "BECOME": become,
            "ASSIGN": assign
        }

    def run(self):
        while self.state not in self.term_states:
            current_state = self.state

            n = self.behaviors[current_state].head
            next_node = None
            while n is not None:
                if type(n) is ActionNode:
                    next_node = n.execute(self)
                elif type(n) is IfNode:
                    next_node = n.execute(self)

                n = next_node