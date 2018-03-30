import ply.yacc as yacc
from soda.helpers import open_file, flatten
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
        ''' first_section_line : TERM '=' term_list ';' '''

    def p_term_list(self, p):
        ''' term_list : term_term
                      | term_list ',' term_term '''

    def p_term_term(self, p):
        ''' term_term : IDENTIFIER '''
        self.algorithm.term_states.append(p[1])

    def p_second_section(self, p):
        ''' second_section : states '''

    def p_states(self, p):
        ''' states : IDENTIFIER seen_state states_behaviors
                   | IDENTIFIER seen_state states_behaviors states '''

    def p_seen_state(self, p):
        ''' seen_state : '''
        self.state = p[-1]

    def p_states_behaviors(self, p):
        ''' states_behaviors : behavior add_behaviors
                             | behavior states_behaviors '''

    def p_add_behaviors(self, p):
        ''' add_behaviors : '''
        self.algorithm.states_behaviors[self.state] = self.state_behaviors
        self.state_behaviors = {}

    def p_behavior(self, p):
        ''' behavior : initiation_event begin statements end '''
        self.state_behaviors[p[1]] = self.behavior
        self.behavior = Behavior()
        self.jump_ids = 0

    def p_initiation_event(self, p):
        ''' initiation_event : IMPULSE
                             | READ '(' read_arguments ')'  '''
        p[0] = (p[1], self.read_arguments) if p[1] == 'READ' else p[1]
        self.read_arguments = ()

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
        ''' condition : condition '=' '=' condition
                      | condition '>' condition
                      | condition '<' condition
                      | '(' condition ')'
                      | NUMBER
                      | IDENTIFIER '''
        p[0] = p[:]
        self.condition.append(list(filter(lambda x: x is not None, p[1:])))

    def p_if_seen(self, p):
        ''' if_seen : '''
        c = flatten(self.condition[-1])
        c = list(filter(lambda x: x is not None, c))
        self.condition = ''.join(c)
        self.behavior.insert(IfNode(self.condition))
        self.condition = []

    def p_endif_seen(self, p):
        ''' endif_seen : '''
        self.behavior.insert(EndIfNode(self.jump_ids))
        self.jump_ids += 1

    def p_else_seen(self, p):
        ''' else_seen : '''
        self.behavior.insert(ElseNode(self.jump_ids))
        self.jump_ids += 1

    def p_action(self, p):
        ''' action : SEND '(' send_arguments ')'
                   | BECOME '(' become_arguments ')' '''
        # p[0] = (p[1], p[3])
        if p[1] == 'BECOME':
            self.behavior.insert(ActionNode(p[1], p[3]))
        if p[1] == 'SEND':
            self.behavior.insert(ActionNode(p[1], ('(' + ', '.join(self.send_arguments) + ')', )))
            self.send_arguments = ()

    def p_read_arguments(self, p):
        ''' read_arguments : read_arg
                           | read_arg ',' read_arguments
                           | NONE '''

    def p_read_arg(self, p):
        ''' read_arg : IDENTIFIER identifier_seen
                     | STRING '''
        try:
            self.read_arguments += ((p[1], p[2]), )
        except:
            self.read_arguments += (p[1].replace('"', '') , )

    def p_identifier_seen(self, p):
        ''' identifier_seen : '''
        p[0] = 'IDENTIFIER'

    def p_send_arguments(self, p):
        ''' send_arguments : send_arg
                           | send_arg ',' send_arguments '''

    def p_send_args(self, p):
        ''' send_arg : STRING
                     | IDENTIFIER '''
        self.send_arguments += (p[1], )

    def p_become_arguments(self, p):
        ''' become_arguments : IDENTIFIER '''
        p[0] = (p[1],)

    def p_NONE(self, p):
        ''' NONE : '''
        p[0] = None

    def p_assignemnt(self, p):
        ''' assignment : IDENTIFIER '=' expression '''
        if p[1] in self.special_identifiers:
            logger.info("Special identifier used on left side of assignment! -> {}".format(p[1]))
            exit()

        self.behavior.insert(ActionNode('ASSIGN', (p[1] + ' = ' + self.expression,)))
        self.expression = None
        self.arithmetic_expr = []

    def p_expression(self, p):
        ''' expression : arithmetic_expr arithmetic_seen
                       | string_expr string_seen '''

    def p_arithmetic_seen(self, p):
        '''arithmetic_seen : '''
        ae = flatten(self.arithmetic_expr[-1])
        ae = list(filter(lambda x: x is not None, ae))
        self.expression = ''.join(ae)

    def p_string_seen(self, p):
        '''string_seen : '''
        self.expression = p[-1]

    def p_arithmetic_expr(self, p):
        ''' arithmetic_expr : arithmetic_expr '+' arithmetic_expr
                            | arithmetic_expr '-' arithmetic_expr
                            | arithmetic_expr '*' arithmetic_expr
                            | arithmetic_expr '/' arithmetic_expr
                            | '(' arithmetic_expr ')'
                            | NUMBER
                            | IDENTIFIER '''
        p[0] = p[:]
        self.arithmetic_expr.append(list(filter(lambda x: x is not None, p[1:])))

    def p_string_expr(self, p):
        ''' string_expr : STRING '''
        p[0] = p[1]

    def p_error(self, p):
        logger.info("Syntax error in input! -> {}".format(p))
        exit()

    def build(self, lexer, algorithm):
        self.lexer = lexer
        self.algorithm = algorithm
        self.tokens = lexer.tokens
        self._parser = yacc.yacc(module=self, debug=False)

        self.state_behaviors = {}
        self.behavior = Behavior()
        self.jump_ids = 0
        self.arithmetic_expr = []
        self.expression = None
        self.state = None
        self.read_arguments = ()
        self.send_arguments = ()
        self.condition = []

        self.special_identifiers = ['ID', 'NEIGHBOURS']

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

        logger.info("TERM STATES {0}".format(self.algorithm.term_states))

        for s, bs in self.algorithm.states_behaviors.items():
            for i, b in bs.items():
                logger.info("STATE {0} [\n{1} -> \n\t{2}]".format(s, i, b))

    def process_conditions_scopes(self):
        for s, bs in self.algorithm.states_behaviors.items():
            for i, b in bs.items():
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