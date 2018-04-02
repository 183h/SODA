from threading import Thread
from time import sleep
from logging import getLogger
from os import _exit, EX_OK

logger = getLogger(__name__)


class DeadlockInspector(Thread):
    def __init__(self, entities, term_states):
        Thread.__init__(self)
        self.entities = entities
        self.term_states = term_states

    def run(self):
        while True:
            result = []

            sleep(5)

            for e in self.entities:
                if e._state in self.term_states:
                    result.append(True)
                elif e._read_lock:
                    result.append("R")
                else:
                    result.append(False)

            if (("R" in result and True in result and False not in result)
                    or ("R" in result and True not in result and False not in result)):
                logger.info("DEADLOCK!")
                _exit(EX_OK)
            elif True in result and "R" not in result and False not in result:
                exit()

