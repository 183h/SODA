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
                self.topology.entities[e]["out_port"],
                self.topology.entities[e]["state"],
                self.behavior.states_behaviors,
                self.topology.neighbours[e]
            )

            self.entities.append(entity)

    def simulate(self):
        for e in self.entities:
            e.start()
