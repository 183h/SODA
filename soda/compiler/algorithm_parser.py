import ply.yacc as yacc
from soda.helpers import open_file
from logging import getLogger
from soda.distributed_environment.behavior import Behavior, ActionNode, IfNode, EndIfNode, ElseNode

logger = getLogger(__name__)


class AlgorithmParser(object):
    def p_algorithm(self, p):
        ''' algorithm : first_section second_section '''

    def p_first_section(self, p):
        ''' first_section : first_section_line
                          | first_section_line first_section '''

    def p_first_section_line(self, p):
        ''' first_section_line : STATES '=' states_list ';'
                               | REGISTERS '=' register_list ';'
                               | TERM '=' term_list ';' '''

    def p_states_list(self, p):
        ''' states_list  : state_term
                         | states_list ',' state_term '''

    def p_state_term(self, p):
        ''' state_term : IDENTIFIER '''
        self.algorithm.states.append(p[1])

    def p_register_list(self, p):
        ''' register_list : register_term
                          | register_list ',' register_term '''

    def p_register_term(self, p):
        ''' register_term : IDENTIFIER '''
        self.algorithm.registers.append(p[1])

    def p_term_list(self, p):
        ''' term_list : term_term
                      | term_list ',' term_term '''

    def p_term_term(self, p):
        ''' term_term : IDENTIFIER '''
        self.algorithm.term_states.append(p[1])

    def p_second_section(self, p):
        ''' second_section : second_section_state_behavior
                          | second_section_state_behavior second_section '''

    def p_second_section_state_behavior(self, p):
        ''' second_section_state_behavior : IDENTIFIER begin statements end '''
        self.algorithm.states_behaviors[p[1]] = self.state_behavior
        self.state_behavior = Behavior()
        self.jump_ids = 0

    def p_statements(self, p):
        ''' statements : statement
                       | statement statements '''

    def p_statement(self, p):
        ''' statement : action
                      | if_statement
                      | assignment '''

    def p_if_statement(self, p):
        ''' if_statement : if condition if_seen then statements endif endif_seen
                         | if condition if_seen then statements else else_seen statements endif endif_seen '''

    def p_condition(self, p):
        ''' condition : EVAL '''
        p[0] = p[1]

    def p_if_seen(self, p):
        ''' if_seen : '''
        self.state_behavior.insert(IfNode(p[-1]))

    def p_endif_seen(self, p):
        ''' endif_seen : '''
        self.state_behavior.insert(EndIfNode(self.jump_ids))
        self.jump_ids += 1

    def p_else_seen(self, p):
        ''' else_seen : '''
        self.state_behavior.insert(ElseNode(self.jump_ids))
        self.jump_ids += 1

    def p_action(self, p):
        ''' action :  READ '(' read_arguments ')'
                    | SEND '(' send_arguments ')'
                    | BECOME '(' become_arguments ')' '''
        p[0] = (p[1], p[3])
        self.state_behavior.insert(ActionNode(p[1], p[3]))

    def p_read_arguments(self, p):
        ''' read_arguments : IDENTIFIER
                           | NONE '''
        p[0] = (p[1], )

    def p_send_arguments(self, p):
        ''' send_arguments : IDENTIFIER '''
        p[0] = (p[1],)

    def p_become_arguments(self, p):
        ''' become_arguments : IDENTIFIER '''
        p[0] = (p[1],)

    def p_NONE(self, p):
        ''' NONE : '''
        p[0] = None

    def p_assignemnt(self, p):
        ''' assignment : IDENTIFIER '=' arithmetic_expr '''
        self.state_behavior.insert(ActionNode('ASSIGN', (p[1] +'='+ ''.join(self.arithmetic_expr[-1]),)))
        self.arithmetic_expr = []

    def p_arithmetic_expr(self, p):
        ''' arithmetic_expr : arithmetic_expr '+' arithmetic_expr
                            | arithmetic_expr '-' arithmetic_expr
                            | arithmetic_expr '*' arithmetic_expr
                            | arithmetic_expr '/' arithmetic_expr
                            | '(' arithmetic_expr ')'
                            | NUMBER
                            | IDENTIFIER '''
        p[0] = p[1]
        self.arithmetic_expr.append(list(filter(lambda x: x is not None, p[1:])))

    def p_error(self, p):
        logger.info("Syntax error in input! -> {}".format(p))
        exit()

    def build(self, lexer, algorithm):
        self.lexer = lexer
        self.algorithm = algorithm
        self.tokens = lexer.tokens
        self._parser = yacc.yacc(module=self, debug=False)
        self.state_behavior = Behavior()
        self.jump_ids = 0
        self.arithmetic_expr = []

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
        self.process_conditions_scopes()

        logger.info("REGISTERS {0}".format(self.algorithm.registers))
        logger.info("TERM STATES {0}".format(self.algorithm.term_states))

        for s, b in self.algorithm.states_behaviors.items():
            logger.info("BEHAVIOR [{0} -> \n{1}]".format(s, b))

    def process_conditions_scopes(self):
        for s, b in self.algorithm.states_behaviors.items():
            n = b.tail

            while n is not None:
                if type(n) is IfNode:
                    n1 = n

                    while n1 is not None:
                        if (type(n1) is EndIfNode
                                and not n1.scope_processed):
                            n.jump_endif = n1
                            n1.scope_processed = True
                            break
                        elif (type(n1) is ElseNode
                                and not n1.scope_processed):
                            n2 = n1

                            while n2 is not None:
                                if (type(n2) is EndIfNode
                                        and not n2.scope_processed):
                                    n.jump_else = n1
                                    n.jump_endif = n2
                                    n1.scope_processed = True
                                    n2.scope_processed = True
                                    break
                                n2 = n2.next

                            break

                        n1 = n1.next

                n = n.previous