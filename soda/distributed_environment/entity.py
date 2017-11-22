from zmq import Context, REP, REQ
from threading import Thread


class Entity(Thread):
    def __init__(self, id, ip, in_port, out_port, state, behaviors, neighbours):
        Thread.__init__(self)
        self.id = id
        self.ip = ip
        self.in_port = in_port
        self.out_port = out_port
        self.state = state
        self.behaviors = behaviors
        self.neighbours = neighbours

        context = Context()
        self.in_socket = context.socket(REP)
        self.out_socket = context.socket(REQ)

    def run(self):
        for b in self.behaviors[self.state]:
            print (self.id, b)