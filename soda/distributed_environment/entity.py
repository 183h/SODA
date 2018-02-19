from zmq import Context, REP, REQ
from threading import Thread
from pickle import dumps, loads
from logging import getLogger, info

logger = getLogger(__name__)


class Entity(Thread):
    def __init__(self, id, ip, in_port, state, term_states, behaviors, neighbours):
        Thread.__init__(self)
        self.id = id
        self.ip = ip
        self.in_port = in_port
        self.state = state
        self.term_states = term_states
        self.behaviors = behaviors
        self.neighbours = neighbours

        context = Context()
        self.in_socket = context.socket(REP)
        self.in_socket.bind("tcp://*:%s" % self.in_port)

        def read():
            pickled_message = self.in_socket.recv()
            message, entity_id = loads(pickled_message)
            print(self.id, "Received:", message, "| From:", entity_id)

        def send(message):
            for n in self.neighbours:
                for e in n:
                    out_socket = context.socket(REQ)
                    out_socket.connect("tcp://localhost:%s" % n[e]["in_port"])
                    message_content = (message, self.id)
                    pickled_message = dumps(message_content)
                    out_socket.send(pickled_message)
                    out_socket.disconnect("tcp://localhost:%s" % n[e]["in_port"])
                    out_socket.close()
                    print(self.id, "Sended:", message, "| To:", e)

        def become(new_state):
            self.state = new_state
            print(self.id, "Changed state to:", new_state)

        self.actions = {
            "READ": read,
            "SEND": send,
            "BECOME": become
        }

    def run(self):
        while self.state not in self.term_states:
            current_state = self.state

            for a in self.behaviors[current_state]:
                action, argument = a
                if argument is not None:
                    self.actions[action](argument)
                else:
                    self.actions[action]()