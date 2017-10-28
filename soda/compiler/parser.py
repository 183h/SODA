import ply.yacc as yacc
from soda.helpers import prepare_file


class Parser(object):
    def p_algorithm(self, p):
        ''' algorithm : first_section'''

    def p_first_section(self, p):
        ''' first_section : STATES EQUALS states_list SEMICOLON
                          | REGISTERS EQUALS register_list SEMICOLON
                          | INIT EQUALS init_list SEMICOLON
                          | TERM EQUALS term_list SEMICOLON
                          | second_section'''

    def p_states_list(self, p):
        ''' states_list  : state_term
                         | states_list COMMA state_term'''

    def p_state_term(self, p):
        ''' state_term : NAME'''
        self.behavior.states.append(p[1])

    def p_register_list(self, p):
        ''' register_list : register_term
                          | register_list COMMA register_term'''

    def p_register_term(self, p):
        ''' register_term : NAME'''
        self.behavior.registers.append(p[1])

    def p_init_list(self, p):
        ''' init_list : init_term
                      | init_list COMMA init_term'''

    def p_init_term(self, p):
        ''' init_term : NAME'''
        self.behavior.init_states.append(p[1])

    def p_term_list(self, p):
        ''' term_list : term_term
                      | term_list COMMA term_term'''

    def p_term_term(self, p):
        ''' term_term : NAME'''
        self.behavior.term_states.append(p[1])

    def p_second_section(self, p):
        ''' second_section : behaviors'''

    def p_behaviors(self, p):
        ''' behaviors : NAME begin end '''

    def p_error(self, p):
        print("Syntax error in input! -> {}".format(p))

    def __init__(self, lexer, behavior):
        self.lexer = lexer
        self.behavior = behavior
        self.tokens = lexer.tokens
        self._parser = yacc.yacc(module=self)

    @prepare_file
    def parsing(self, file):
        for line in file:
            try:
                parser_input = line
            except EOFError:
                break

            self._parser.parse(parser_input, lexer=self.lexer._lexer)