import ply.lex as lex
from soda.helpers import open_file


class AlgorithmLexer(object):
    keywords = (
        'INIT', 'TERM', 'STATES', 'REGISTERS',
        'begin', 'end',
        'SEND', 'BECOME'
    )

    tokens = keywords + (
        'NAME', 'EQUALS', 'COMMA', 'SEMICOLON',
        'LPAREN', 'RPAREN'
    )

    # Tokens
    t_EQUALS = r'='
    t_COMMA = r','
    t_SEMICOLON = r';'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'

    # Ignored characters
    t_ignore = ' \t\n'

    def t_NAME(self, t):
        r'[a-zA-Z][a-zA-Z]*'
        if t.value in self.keywords:  # is this a keyword?
            t.type = t.value
        return t

    def t_error(self, t):
        print ("Illegal character {0} at line {1}".format(t.value[0], t.lineno))
        t.lexer.skip(1)

    def build(self, **kwargs):
        self._lexer = lex.lex(module=self, **kwargs)

    @open_file
    def lexical_analysis(self, file):
        print ("Started lexical analysis...")

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
                print ("  ", token)

        print ("Ended lexical analysis...")