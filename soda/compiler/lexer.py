import ply.lex as lex


class Lexer(object):
    keywords = (
        'INIT', 'TERM', 'BEGIN', 'END',
        'SEND', 'BECOME', 'DASH', 'STATUSES', 'REGISTERS'
    )
    tokens = keywords + (
        'NAME', 'EQUALS', 'LPAREN', 'RPAREN',
        'COMMA', 'SEMICOLON',
    )

    # Tokens

    t_EQUALS = r'='
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_COMMA = r','
    t_SEMICOLON = r';'
    t_DASH = r'-'
    t_STATUSES = r'STATUSES'
    t_REGISTERS = r'REGISTERS'
    t_INIT = r'INIT'
    t_TERM = r'TERM'
    t_BEGIN = r'begin'
    t_END = r'end'
    t_SEND = r'SEND'
    t_BECOME = r'BECOME'

    # Ignored characters
    t_ignore = " \t"

    def t_NAME(self, t):
        r'[a-zA-Z][a-zA-Z]*'
        if t.value in self.keywords:  # is this a keyword?
            t.type = t.value
        return t

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print "Illegal character {0} at line {1}".format(t.value[0], t.lineno)
        t.lexer.skip(1)

    def __init__(self, **kwargs):
        self.lexer = lex.lex(object=self, **kwargs)

    def lexical_analysis(self, file):
        for line in file:
            try:
                lex_input = line
            except EOFError:
                break
            self.lexer.input(lex_input)
            while True:
                token = self.lexer.token()
                if not token:
                    break
                print token