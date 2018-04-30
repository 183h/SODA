from soda.distributed_environment.entity import Entity
from logging import getLogger
from soda.deadlock_inspector import DeadlockInspector

logger = getLogger(__name__)


class Simulator(object):
    def __init__(self, algorithm, topology):
        self.algorithm = algorithm
        self.topology = topology
        self.entities = []

    def create_entities(self, count_impulses):
        impulse_counter = 0

        # Prejdeme všetky entity nachádzajúce sa v dátovej štruktúre topológie a
        # vytvoríme jednotlivé inštancie entít reprezentované triedou Entity.
        for e in self.topology.entities:
            # Preskočíme externé entity.
            if "state" not in self.topology.entities[e]:
                continue

            # Použitie konštruktora triedy Entity.
            entity = Entity(
                e, # Identifikátor entity.
                self.topology.entities[e]["ip"], # IP adresa soketu pre prijímanie správ.
                self.topology.entities[e]["in_port"], # Port soketu pre prijímanie správ.
                self.topology.entities[e]["state"], # Počiatočný stav entity.
                self.algorithm.term_states, # Terminujúce stavy.
                self.algorithm.states_behaviors, # Všetky stavy a k nim príslušné správania.
                self.topology.neighbours[e] # Susedia entity.
            )

            if ('IMPULSE' in self.algorithm.states_behaviors[self.topology.entities[e]["state"]]
                    and impulse_counter < count_impulses):
                entity._impulse = True
                impulse_counter += 1

            # Uloženie inštancie entity do atribútu self.entities.
            self.entities.append(entity)

    def simulate(self, no_di):
        logger.info("Start of simulation.")

        # Spustenie súbežného správania entít. Metóda start() spustí v inštancii entity
        # vykonávanie implementovanej metódy run().
        for e in self.entities:
            e.start()

        # Ak používateľ použil prepínač --no-di tak sa inšpektor uviaznutia nespustí.
        if not no_di:
            deadlock_inspector = DeadlockInspector(self.entities, self.algorithm.term_states)
            deadlock_inspector.start()

        # Metódou join() čakáme postupne na koniec vykonania súbežného správania
        # jednotlivých entít. Až keď sú správania všetkých entít ukončené program
        # pokračuje ďalej.
        for e in self.entities:
            e.join()

        # Ďalej nasleduje už len zalogovanie prenesených správ vzhľadom na jednotlivé
        # entity, finálnych stavov entít a správ prenesených počas celej simulácie.
        logger.info("End of simulation.\n")
        logger.info("Sent messages per entity (entity id, count of sent messages) -> {0}".format([(e._id, e._count_sent_messages) for e in self.entities]))
        logger.info("Entities state's (entity id, state) -> {0}".format([(e._id, e._state) for e in self.entities]))

        logger.info("Total count of sent messages -> {0}".format(sum([e._count_sent_messages for e in self.entities])))