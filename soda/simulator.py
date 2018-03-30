from soda.distributed_environment.entity import Entity
from logging import getLogger

logger = getLogger(__name__)


class Simulator(object):
    def __init__(self, algorithm, topology):
        self.algorithm = algorithm
        self.topology = topology
        self.entities = []

    def create_entities(self):
        impulse_counter = 0

        for e in self.topology.entities:
            entity = Entity(
                e,
                self.topology.entities[e]["ip"],
                self.topology.entities[e]["in_port"],
                self.topology.entities[e]["state"],
                self.algorithm.term_states,
                self.algorithm.states_behaviors,
                self.topology.neighbours[e]
            )

            if ('IMPULSE' in self.algorithm.states_behaviors[self.topology.entities[e]["state"]]
                    and impulse_counter < 1):
                entity._impulse = True
                impulse_counter += 1

            self.entities.append(entity)

    def simulate(self):
        for e in self.entities:
            e.start()

        for e in self.entities:
            e.join()

        logger.info("Entities state's [{0}]".format([(e._id, e._state) for e in self.entities]))