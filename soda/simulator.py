from soda.distributed_environment.entity import Entity
from logging import getLogger

logger = getLogger(__name__)


class Simulator(object):
    """docstring for Simulator"""
    def __init__(self, behavior, topology):
        self.behavior = behavior
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
                self.behavior.term_states,
                self.behavior.states_behaviors,
                self.topology.neighbours[e]
            )

            if ('IMPULSE' in self.behavior.states_behaviors[self.topology.entities[e]["state"]]
                    and impulse_counter < 1):
                entity.impulse = True
                impulse_counter += 1

            # initiate attributes serving as registers
            for r in self.behavior.registers:
                setattr(entity, str(r), None)

            self.entities.append(entity)

    def simulate(self):
        for e in self.entities:
            e.start()

        for e in self.entities:
            e.join()

        logger.info("Entities state's [{0}]".format([(e.id_e, e.state) for e in self.entities]))