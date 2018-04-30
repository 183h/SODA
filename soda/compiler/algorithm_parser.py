import ply.yacc as yacc
from soda.helpers import open_file, flatten, str_to_int_or_float
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
        self.all_states.append(p[1])

    # Definujeme, že druhá sekcia algoritmu sa skladá zo stavov.
    def p_second_section(self, p):
        # Každý token v pravidle má svoju číselnú pozíciu, začínajúc od 0.
        # K hodnotena pozícii sa pristupuje pomocou premennej p.
        #          p[0]       p[1]
        ''' second_section : states '''
        # Definícia gramatického pravidla v BNF forme.

    # Tieto stavy v sebe definujú príslušné správania. Token IDENTIFIER na pozícii 1
    # reprezentuje názov stavu.
    def p_states(self, p):
        ''' states : IDENTIFIER seen_state states_behaviors
                   | IDENTIFIER seen_state states_behaviors states '''

    def p_seen_state(self, p):
        ''' seen_state : '''
        # Kód, ktorý sa nachádza za definíciou gramatického pravidla sa vykoná keď
        # syntaktický analyzátor vykoná redukciu pravidla.
        self.state = p[-1]
        self.all_states.append(self.state)

    # Toto gramatické pravidlo nám umožňuje definovať, že pre jeden stav dokážeme
    # spracovať viacero správaní. Využívame vlastnosť rekurzie formálnej gramatiky.
    def p_states_behaviors(self, p):
        ''' states_behaviors : behavior add_behaviors
                             | behavior states_behaviors '''

    def p_add_behaviors(self, p):
        ''' add_behaviors : '''
        # Do dátovej štruktúry algoritmu, ktorá je jedným zo vstupov syntaktického
        # analyzátora v tomto pravidle ukladáme pre identifikovaný stav slovník s
        # rôznymi správaniami.
        self.algorithm.states_behaviors[self.state] = self.state_behaviors
        self.state_behaviors = {}

    # Toto pravidlo definuje jednotlivé správania. Správania sa skladá z iniciačnej akcie
    # a následne jeho tela, ktoré je ohraničené tokenmi begin a end. Telo správania sa
    # skladá zase z množiny príkazov.
    def p_behavior(self, p):
        ''' behavior : initiation_event begin statements end '''
        if p[1] in self.state_behaviors:
            logger.info("State with same initiation action already defined! -> {}".format(p[1]))
            exit()

        self.state_behaviors[p[1]] = self.behavior
        self.behavior = Behavior()
        self.jump_ids = 0

    # V tejto metóde môžeme vidieť ďalšiu z vlastností modulu PLY. V zdrojovom kóde
    # priraďujeme do premennej p[0] nejakú hodnotu. Ak príde k redukcii tohto
    # pravidla, tak sa táto hodnota prenesie do pravidla, ktoré sa bude redukovať po
    # tomto. V tomto prípade do pravidla definovaného metódou p_behavior().
    def p_initiation_event(self, p):
        ''' initiation_event : IMPULSE
                             | READ '(' read_arguments ')'  '''
        p[0] = (p[1], self.read_arguments) if p[1] == 'READ' else p[1]
        self.read_arguments = ()

    def p_statements(self, p):
        ''' statements : statement
                       | statement statements '''

    # V tele správania sa môže vyskytnúť akcia, podmienka alebo priradenie.
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
                      | condition '<' '=' condition
                      | condition '>' '=' condition
                      | condition '!' '=' condition
                      | condition and condition
                      | condition or condition
                      | '(' condition ')'
                      | number_expr
                      | IDENTIFIER
                      | LEN '(' IDENTIFIER ')'
                      | not IDENTIFIER '''
        try:
            if p[1] == 'not':
                p[1] = ' not '
            elif p[2] == 'and':
                p[2] = ' and '
            elif p[2] == 'or':
                p[2] = ' or '
        except:
            pass

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

    # V nasledujúcej metóde definujeme jednotlivé akcie, ktoré môže entita vykonávať.
    # Podľa toho akú akciu identifikujeme sa vykoná vloženie uzla action do štruktúry
    # spájaného zoznamu reprezentujúceho správanie.
    def p_action(self, p):
        ''' action : SEND '(' send_arguments ')'
                   | BECOME '(' become_arguments ')'
                   | LOG '(' log_arguments ')'
                   | EXEC '(' exec_arguments ')'
                   | ADD '(' add_arguments ')'
                   | REMOVE '(' remove_arguments ')'
                   | POP '(' pop_arguments ')' '''
        if p[1] == 'BECOME':
            self.behavior.insert(ActionNode(p[1], p[3]))
        elif p[1] == 'SEND':
            self.behavior.insert(ActionNode(p[1], ('(' + ', '.join(self.send_arguments) + ')', p[3], )))
            self.send_arguments = ()
        elif p[1] == 'LOG':
            self.behavior.insert(ActionNode(p[1], ('+'.join(['str(' + str(a) + ')' for a in self.log_arguments]), )))
            self.log_arguments = ()
        elif p[1] == 'EXEC':
            self.behavior.insert(ActionNode(p[1], p[3]))
        elif p[1] == 'ADD':
            self.behavior.insert(ActionNode(p[1], p[3]))
        elif p[1] == 'REMOVE':
            self.behavior.insert(ActionNode(p[1], p[3]))
        elif p[1] == 'POP':
            self.behavior.insert(ActionNode(p[1], p[3]))

    def p_pop_arguments(self, p):
        '''pop_arguments : IDENTIFIER ',' IDENTIFIER '''
        if p[3] in self.special_identifiers:
            logger.info("Special identifier used as first argument! -> {}".format(p[1]))
            exit()

        p[0] = (p[1], p[3])

    def p_remove_arguments(self, p):
        ''' remove_arguments : IDENTIFIER ',' array_remove_value '''
        if p[1] in self.special_identifiers:
            logger.info("Special identifier used as first argument! -> {}".format(p[1]))
            exit()

        p[0] = (p[1], p[3])

    def p_array_remove_value(self, p):
        ''' array_remove_value : IDENTIFIER
                               | number_expr
                               | string_expr '''
        p[0] = p[1]

    def p_add_arguments(self, p):
        ''' add_arguments : IDENTIFIER ',' array_add_value '''
        if p[1] in self.special_identifiers:
            logger.info("Special identifier used as first argument! -> {}".format(p[1]))
            exit()

        p[0] = (p[1], p[3])

    def p_array_add_value(self, p):
        ''' array_add_value : number_expr
                            | string_expr
                            | IDENTIFIER '''
        p[0] = p[1]

    def p_exec_arguments(self, p):
        ''' exec_arguments : STRING ',' output_type ',' exec_output exec_input '''
        p[0] = (p[1], p[3], p[5] if p[5] is not None else None, p[6] if p[6] is not None else None)

    def p_output_type(self, p):
        ''' output_type : int
                        | string
                        | float '''
        p[0] = p[1]

    def p_exec_input(self, p):
        ''' exec_input : ',' IDENTIFIER
                       | NONE '''
        try:
            p[0] = p[2]
        except:
            p[0] = p[1]

    def p_exec_output(self, p):
        ''' exec_output : IDENTIFIER '''
        p[0] = p[1]

    def p_read_arguments(self, p):
        ''' read_arguments : read_arg
                           | read_arg ',' read_arguments '''

    def p_read_arg(self, p):
        ''' read_arg : IDENTIFIER identifier_seen_read
                     | STRING string_seen_read
                     | number_expr number_seen_read '''
        if p[2] == 'IDENTIFIER':
            self.read_arguments += ((p[1], p[2]),)
        elif p[2] == 'STRING':
            self.read_arguments += (p[1],)
        elif p[2] == 'number_expr':
            self.read_arguments += (str_to_int_or_float(p[1]),)

    def p_number_seen_read(self, p):
        ''' number_seen_read : '''
        p[0] = 'number_expr'

    def p_string_seen_read(self, p):
        ''' string_seen_read : '''
        p[0] = 'STRING'

    def p_identifier_seen_read(self, p):
        ''' identifier_seen_read : '''
        p[0] = 'IDENTIFIER'

    def p_send_arguments(self, p):
        ''' send_arguments : '(' message ')' ',' IDENTIFIER '''
        p[0] = p[5]

    def p_message(self, p):
        ''' message : message_part
                    | message_part ',' message '''

    def p_message_part(self, p):
        ''' message_part : STRING string_seen_read
                         | IDENTIFIER identifier_seen_read
                         | number_expr number_seen_read '''
        if p[2] == 'IDENTIFIER':
            self.send_arguments += (p[1],)
        elif p[2] == 'STRING':
            self.send_arguments += ("'" + p[1] + "'",)
        elif p[2] == 'number_expr':
            self.send_arguments += (p[1],)

    def p_become_arguments(self, p):
        ''' become_arguments : IDENTIFIER '''
        p[0] = (p[1],)
        self.used_states.append(p[1])

    def p_log_arguments(self, p):
        ''' log_arguments : log_arg
                          | log_arg ',' log_arguments '''

    def p_log_arg(self, p):
        ''' log_arg : STRING
                    | IDENTIFIER
                    | NUMBER'''
        self.log_arguments += (p[1], )

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
                       | string_expr string_seen_expression
                       | array_expr array_seen_expression
                       | boolean_expr boolean_seen_expression '''

    def p_boolean_expr(self, p):
        ''' boolean_expr : True
                         | False '''
        p[0] = p[1]

    def p_boolean_seen_expression(self, p):
        ''' boolean_seen_expression : '''
        self.expression = p[-1]

    def p_array_seen_expression(self, p):
        ''' array_seen_expression :  '''
        self.expression = p[-1]

    def p_array_expr(self, p):
        ''' array_expr : '[' ']' '''
        p[0] = '[]'

    def p_arithmetic_seen(self, p):
        '''arithmetic_seen : '''
        ae = flatten(self.arithmetic_expr[-1])
        ae = list(filter(lambda x: x is not None, ae))
        self.expression = ''.join(ae)

    def p_string_seen_expression(self, p):
        '''string_seen_expression : '''
        self.expression = p[-1]

    def p_arithmetic_expr(self, p):
        ''' arithmetic_expr : arithmetic_expr '+' arithmetic_expr
                            | arithmetic_expr '-' arithmetic_expr
                            | arithmetic_expr '*' arithmetic_expr
                            | arithmetic_expr '/' arithmetic_expr
                            | '(' arithmetic_expr ')'
                            | number_expr
                            | identifier_deep_copy
                            | LEN '(' IDENTIFIER ')' '''
        p[0] = p[:]
        self.arithmetic_expr.append(list(filter(lambda x: x is not None, p[1:])))

    def p_identifier_deep_copy(self, p):
        ''' identifier_deep_copy : IDENTIFIER '''
        p[0] = 'deepcopy(' + p[1] + ')'

    def p_string_expr(self, p):
        ''' string_expr : STRING '''
        p[0] = "'" + p[1] + "'"

    def p_number_expr(self, p):
        ''' number_expr : NUMBER
                        | '-' NUMBER '''
        p[0] = p[1:]

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
        self.used_states = []
        self.log_arguments = ()
        self.all_states = []

        self.special_identifiers = ['ID', 'NEIGHBOURS', 'SENDER', 'len', 'deepcopy']

    @open_file
    def parsing(self, file):
        # Metóda pre získanie tokenov zo súboru. Treba si všimnúť, že nevyužívame
        # metódu z príslušného lexikálneho analyzátora lexical_analysis().
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

        # Metóda parse() slúži na vykonanie parsovania. Prvý argument je vstup do
        # syntaktického analyzátora, avšak jeho hodnota je prázdny reťazec. Keďže chceme
        # spracovať súbor obsahujúci viac riadkov tak nastavíme argument lexer na
        # príslušný lexikálny analyzátor a zároveň v tele metódy parsing() zadefinujeme
        # funkciu get_token(), ktorá nám súbor postupne prejde a vráti každý token, ktorý
        # identifikuje.
        self._parser.parse("", lexer=self.lexer._lexer, tokenfunc=get_token, tracking=True)

        # Kontrola, či stavy použité v akcii BECOME sú definované v opise.
        for s in self.used_states:
            if s not in self.all_states:
                logger.info("Trying to change state of entity to undefined state! -> {}".format(s))
                exit()

        self.process_conditions_scopes()

        logger.info("TERM STATES {0}\n".format(self.algorithm.term_states))

        for s, bs in self.algorithm.states_behaviors.items():
            for i, b in bs.items():
                logger.info("STATE {0} [\n{1} -> \n\t{2}]\n".format(s, i, b))

    def process_conditions_scopes(self):
        # Prejdeme každý stav a k nemu príslušné správania.
        for s, bs in self.algorithm.states_behaviors.items():
            for i, b in bs.items():
                # Nastavíme sa na koniec spájaného zoznamu.
                n = b.tail

                while n is not None:
                    if type(n) is IfNode:
                        n1 = n

                        # Následne ak sme našli if uzol iterujeme od tohto uzlu smerom ku koncu
                        # zonamu.
                        while n1 is not None:
                            # Pri tejto iterácii smerujúcej ku koncu hľadáme najbližší endif uzol
                            # alebo else uzol, ktorý patrí k nájdenému if uzlu. Následne tieto uzly
                            # spárujeme. Ak sa jedná o else uzol vykoná sa ešte jedna iterácia
                            # smerom ku koncu zoznamu hľadajúca príslušný endif uzol. Aby sme
                            # pri ďalších iteráciách pre iné if uzly nenarazili na tie isté prvé endif
                            # a else uzly, nastavíme atribút uzlu scope_processed na True. Táto
                            # premenná značí, že uzol už bol spracovaný.
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