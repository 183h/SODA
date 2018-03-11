import ply.yacc as yacc
from soda.helpers import open_file
from logging import getLogger
from soda.distributed_environment.behavior import Behavior, Node

logger = getLogger(__name__)


class AlgorithmParser(object):
    def p_algorithm(self, p):
        ''' algorithm : first_section second_section'''

    def p_first_section(self, p):
        ''' first_section : first_section_line
                          | first_section_line first_section'''

    def p_first_section_line(self, p):
        ''' first_section_line : STATES '=' states_list ';'
                               | REGISTERS '=' register_list ';'
                               | TERM '=' term_list ';' '''

    def p_states_list(self, p):
        ''' states_list  : state_term
                         | states_list ',' state_term'''

    def p_state_term(self, p):
        ''' state_term : IDENTIFIER'''
        self.behavior.states.append(p[1])

    def p_register_list(self, p):
        ''' register_list : register_term
                          | register_list ',' register_term'''

    def p_register_term(self, p):
        ''' register_term : IDENTIFIER'''
        self.behavior.registers.append(p[1])

    def p_term_list(self, p):
        ''' term_list : term_term
                      | term_list ',' term_term'''

    def p_term_term(self, p):
        ''' term_term : IDENTIFIER'''
        self.behavior.term_states.append(p[1])

    def p_second_section(self, p):
        ''' second_section : second_section_state_behavior
                          | second_section_state_behavior second_section'''

    def p_second_section_state_behavior(self, p):
        ''' second_section_state_behavior : IDENTIFIER begin commands end'''
        self.behavior.states_behaviors[p[1]] = self.test
        self.test = Behavior()

    def p_commands(self, p):
        ''' commands : command
                     | command f commands

                      '''
        self.state_commands.append(p[1])
        if p[1] != 'if':
            # self.test.insert(Node(p[1][0], p[1][1]))
            # print("y", p[:])
            pass
        else:
            pass# print("x", p[:])
        # print(p[:])

    def p_if_cond(self, p):
        ''' if_cond : testcondition then commands endif'''
        p[0]='if'
        # self.test.insert(Node("d", "D"))
        print(p[:])

    def p_d(self, p):
        ''' d : if'''
        node = Node('if'+str(self.c), 'if')
        self.test.insert(node)
        self.j = node
        print("d", self.c)
        self.c+=1
        # pass

    def p_f(self, p):
        ''' f : '''
        # print("f", p[-1])
        if p[-1] != 'if':
            pass
            print("c")
            # self.test.insert(Node(p[-1][0], p[-1][1]))
        else:
            node = Node('endif'+str(self.c), 'endif')
            self.test.insert(node)
            self.j.jump = node
            print("f", self.c)
            self.c+=1

    def p_command(self, p):
        ''' command : READ '(' read_arguments ')'
                    | SEND '(' send_arguments ')'
                    | BECOME '(' become_arguments ')'
                    | d if_cond
                    '''
        try:
            p[0] = (p[1], p[3])
            self.test.insert(Node(p[1], p[3]))
        except:
            p[0] = 'if'
        # self.test.insert(Node(p[1], p[3]))
        # print("y", p[:])

    def p_read_arguments(self, p):
        ''' read_arguments : EVAL '''
        p[0] = (p[1], )
        # print(p[:])

    def p_send_arguments(self, p):
        ''' send_arguments : EVAL '''
        p[0] = (p[1],)
        # print(p[:])

    def p_become_arguments(self, p):
        ''' become_arguments : IDENTIFIER '''
        p[0] = (p[1],)
        # print(p[:])

    def p_error(self, p):
        logger.info("Syntax error in input! -> {}".format(p))

    def build(self, lexer, behavior):
        self.lexer = lexer
        self.behavior = behavior
        self.tokens = lexer.tokens
        self._parser = yacc.yacc(module=self, debug=True)
        self.state_commands = []
        self.test = Behavior()
        self.j = None
        self.c = 1

    def reverse_list(self, head):
        new_head = None
        while head:
            head.next, head, new_head = new_head, head.next, head
        return new_head

    @open_file
    def parsing(self, file):
        def get_token():
            while True:
                token = self.lexer._lexer.token()
                if token is not None:
                    return token
                try:
                    line = next(file)
                    self.lexer._lexer.input(line)
                except StopIteration:
                    return None

        self._parser.parse("", lexer=self.lexer._lexer, tokenfunc=get_token)

        logger.info("REGISTERS {0}".format(self.behavior.registers))
        logger.info("TERM STATES {0}".format(self.behavior.term_states))

        # self.behavior.states_behaviors['INITIATOR'].head = self.reverse_list(self.behavior.states_behaviors['INITIATOR'].head)

        for b in self.behavior.states_behaviors:
            logger.info("BEHAVIOR [{0} -> {1}]".format(b, self.behavior.states_behaviors[b]))