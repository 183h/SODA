import ply.lex as lex
from soda.helpers import open_file
from logging import getLogger

logger = getLogger(__name__)


class AlgorithmLexer(object):
    # V premennej keywords definujeme všetky kľúčové slová gramatiky.
    keywords = (
        'TERM',
        'IMPULSE', 'READ',
        'begin', 'end',
        'SEND', 'BECOME', 'LOG', 'EXEC',
        'if', 'then', 'endif', 'else',
        'int', 'string', 'float',
        'ADD', 'REMOVE', 'POP', 'LEN',
        'True', 'False', 'not', 'and', 'or'
    )

    tokens = keywords + (
        'IDENTIFIER', 'STRING', 'NUMBER'
    )

    # Premenná literals je špeciálna premenná modulu PLY. Slúži na definíciu tokenov, # ktoré sa skladajú z jedného znaku. Následne je ich potom možné použiť pri
    # definícii gramatiky v pôvodnom tvare napr '='.
    literals = ['=', ',', ';', '(', ')', '+', '-', '*', '/', '<', '>', '[', ']', '!']

    # Ignorovaný je znak nového riadku, tabulátor a medzera.
    t_ignore = ' \t\n'

    # Definícia tokenu cez metódu. Token IDENTIFIER slúži na identifikáciu stavov
    # alebo premenných.
    def t_IDENTIFIER(self, t):
        # Cez regulárny výraz, ktorý sa nachádza za definíciou názvu a argumentov
        # metódy, určujeme pri akom vstupe má byť token identifikovaný.
        # Identifikujeme iba slová zložené z veľkých a malých písmen abecedy.
        r'[a-zA-Z][a-zA-Z]*'

        # Token IDENTIFIER by normálne identifikoval aj kľúčové slová napr if, else.
        # Preto kontrolujeme či sa identifikovaná hodnota nachádza v atribúte keywords.
        # Ak áno tak nastavíme typ tokenu na hodnotu teda samotné kľúčové slovo.
        if t.value in self.keywords:  # is this a keyword?
            t.type = t.value
            return t

        # Ak sa jedná o premennú pridáme prefix „i_“ názvu premennej.
        t.value = 'i_' + t.value
        return t

    def t_STRING(self, t):
        # Token identifikuje dátový typ STRING - reťazec ohraničený úvodzovkami.
        r'"(?:[^"\\]|\\.)*"'
        return t

    def t_NUMBER(self, t):
        # Token identifikuje dátový typ NUMBER – celé, desatinné čísla.
        r'[0-9]+(\.[0-9]+)?'
        return t

    def t_error(self, t):
        logger.info("Illegal character {0} at line {1}".format(t.value[0], t.lineno))
        t.lexer.skip(1)
        exit()

    def build(self, **kwargs):
        self._lexer = lex.lex(module=self, **kwargs)

    @open_file
    def lexical_analysis(self, file):
        for line in file:
            try:
                lex_input = line
            except EOFError:
                break

            self._lexer.input(lex_input)
            while True:
                token = self._lexer.token()
                if not token:
                    break
                logger.info("{0}".format(token))