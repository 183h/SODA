import ply.lex as lex
from soda.helpers import open_file


class TopologyLexer(object):
    tokens = (
        'IP', 'NAME', 'DIGIT'
    )

    literals = [';']

    # Tokens
    # t_SEMICOLON = r';'
    t_IP = r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}'
    t_DIGIT = r'[0-9][0-9]*'

    # Ignored characters
    t_ignore = ' \t\n'

    def t_NAME(self, t):
        r'[a-zA-Z][a-zA-Z]*'
        return t

    def t_error(self, t):
        print ("Illegal character {0} at line {1}".format(t.value[0], t.lineno))
        t.lexer.skip(1)

    def build(self, **kwargs):
        self._lexer = lex.lex(module=self, **kwargs)

    @open_file
    def lexical_analysis(self, file):
        print ("Started topology lexical analysis...")

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

        print ("Ended topology lexical analysis...")