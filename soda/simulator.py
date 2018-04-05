from soda.distributed_environment.entity import Entity
from logging import getLogger
from soda.deadlock_inspector import DeadlockInspector

logger = getLogger(__name__)


class Simulator(object):
    def __init__(self, algorithm, topology):
        self.algorithm = algorithm
        self.topology = topology
        self.entities = []

    def create_entities(self):
        impulse_counter = 0

        for e in self.topology.entities:
            if "state" not in self.topology.entities[e]:
                continue

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

    def simulate(self, no_di):
        for e in self.entities:
            e.start()

        if not no_di:
            deadlock_inspector = DeadlockInspector(self.entities, self.algorithm.term_states)
            deadlock_inspector.start()

        for e in self.entities:
            e.join()

        logger.info("Sent messages per entity (entity id, count of sent messages) -> {0}".format([(e._id, e._count_sent_messages) for e in self.entities]))
        logger.info("Entities state's (entity id, state) -> {0}".format([(e._id, e._state) for e in self.entities]))

        logger.info("Total count of sent messages -> {0}".format(sum([e._count_sent_messages for e in self.entities])))