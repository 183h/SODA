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

            sleep(5) # Kontrolu vykonávame každých 5 sekúnd.

            # Prejdeme všetky entity v distribuovanom prostredí.
            for e in self.entities:
                # Pre zistenie uviaznutia podľa stavu entity pridáme do premennej result
                # hodnotu True, False alebo „R“.
                # Ak je entita v terminujúcom stave uložíme do pola hodnotu True, ak
                # entita čaká na správu hodnotu „R“ a ak je entita v nejakom inom
                # definovanom stave hodnotu False.
                if e._state in self.term_states:
                    result.append(True)
                elif e._read_lock:
                    result.append("R")
                else:
                    result.append(False)

            # Následne kontrolujeme či sú v premennej result nasledujúce hodnoty.

            # Ak pole obsahuje iba hodnoty „R“ a True znamená to, že niektoré entity ukončili
            # svoje správanie a iné čakajú na správy aby mohli svoje správanie vykonať. To
            # však znamená, že správu v prostredí už nemá kto poslať a teda nastalo uviaznutie.

            # Ak pole obsahuje iba hodnoty „R“ znamená to, že v prostredí každý čaká na
            # správu avšak nie je prítomná žiadna entita, ktorá by správu poslala a preto nastalo
            # uviaznutie.
            if (("R" in result and True in result and False not in result)
                    or ("R" in result and True not in result and False not in result)):
                # Ak bolo identifikované uviaznutie zalogujú sa finálne dáta a simulácia sa
                # ukončí.
                logger.info("Sent messages per entity (entity id, count of sent messages) -> {0}".format(
                    [(e._id, e._count_sent_messages) for e in self.entities]))
                logger.info(
                    "Entities state's (entity id, state) -> {0}".format([(e._id, e._state) for e in self.entities]))
                logger.info(
                    "Total count of sent messages -> {0}".format(sum([e._count_sent_messages for e in self.entities])))

                logger.info("DEADLOCK!")
                _exit(EX_OK)
            elif True in result and "R" not in result and False not in result:
                exit()

