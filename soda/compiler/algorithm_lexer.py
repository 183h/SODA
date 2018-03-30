import ply.lex as lex
from soda.helpers import open_file
from logging import getLogger

logger = getLogger(__name__)


class AlgorithmLexer(object):
    keywords = (
        'TERM',
        'IMPULSE', 'begin', 'end',
        'SEND', 'BECOME', 'READ',
        'if', 'then', 'endif', 'else'
    )

    tokens = keywords + (
        'IDENTIFIER', 'NUMBER', 'STRING'
    )

    literals = ['=', ',', ';', '(', ')', '+', '-', '*', '/', '<', '>']

    # Ignored characters
    t_ignore = ' \t\n'

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z][a-zA-Z]*'
        if t.value in self.keywords:  # is this a keyword?
            t.type = t.value
        return t

    def t_STRING(self, t):
        r'"(?:[^"\\]|\\.)*"'
        return t

    # def t_EVAL(self, t):
    #     r'([a-zA-Z][a-zA-Z]*|"(?:[^"\\]|\\.)*")(\+[a-zA-Z][a-zA-Z]*|\+"(?:[^"\\]|\\.)*"){0,}'
    #     return t

    def t_NUMBER(self, t):
        r'[1-9]\d*|0'
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