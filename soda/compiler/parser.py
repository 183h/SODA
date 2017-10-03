import ply.yacc as yacc

states, registers, init, term = [], [], [], []


class Parser(object):
    def p_algorithm(self, p):
        ''' algorithm : first_section'''

    def p_first_section(self, p):
        ''' first_section : STATUSES EQUALS status_list SEMICOLON
                          | REGISTERS EQUALS register_list SEMICOLON
                          | INIT EQUALS init_list SEMICOLON
                          | TERM EQUALS term_list SEMICOLON'''

    def p_status_list(self, p):
        ''' status_list  : status_term
                         | status_list COMMA status_term'''
    def p_status_term(self, p):
        ''' status_term : NAME'''
        states.append(p[1])

    def p_register_list(self, p):
        ''' register_list : register_term
                          | register_list COMMA register_term'''
    def p_register_term(self, p):
        ''' register_term : NAME'''
        registers.append(p[1])

    def p_init_list(self, p):
        ''' init_list : init_term
                      | init_list COMMA init_term'''
    def p_init_term(self, p):
        ''' init_term : NAME'''
        init.append(p[1])

    def p_term_list(self, p):
        ''' term_list : term_term
                      | term_list COMMA term_term'''
    def p_term_term(self, p):
        ''' term_term : NAME'''
        term.append(p[1])

    def p_error(self, p):
        print("Syntax error in input!")

    def __init__(self, tokens):
        self.tokens = tokens
        self._parser = yacc.yacc(module=self)

    def parsing(self, file):
        for line in file:
            try:
                parser_input = line
            except EOFError:
                break

            self._parser.parse(parser_input)