from soda.distributed_environment.entity import Entity


class Simulator(object):
    """docstring for Simulator"""
    def __init__(self, behavior, topology):
        self.behavior = behavior
        self.topology = topology
        self.entities = []

    def create_entities(self):
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

            # initiate attributes serving as registers
            c = 0
            for r in self.behavior.registers:
                setattr(entity, str(r), c)
                c += 1

            self.entities.append(entity)

    def simulate(self):
        for e in self.entities:
            e.start()
