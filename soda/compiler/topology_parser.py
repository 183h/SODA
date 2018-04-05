import ply.yacc as yacc
from soda.helpers import open_file
from logging import getLogger

logger = getLogger(__name__)


class TopologyParser(object):
    def p_algorithm(self, p):
        ''' topology : entities'''

    def p_first_section(self, p):
        ''' entities : entity_line
                     | entity_line entities'''

    def p_first_section_line(self, p):
        ''' entity_line : DIGIT ';' IP ';' DIGIT ';' neighbours ';' STATE
                        | DIGIT ';' IP ';' DIGIT ';' EXTERNAL '''
        p[1] = int(p[1])
        if p[7] == 'EXTERNAL':
            self.topology.entities[p[1]] = {"ip": p[3], "in_port": p[5]}
        else:
            self.topology.entities[p[1]] = {"ip": p[3], "in_port": p[5], "state": p[9]}
            self.topology.neighbours[p[1]] = {int(n) : {"ip": None, "in_port": None} for n in self.entity_neighbours}
            self.entity_neighbours = []

    def p_neighbours(self, p):
        ''' neighbours : DIGIT
                       | DIGIT ',' neighbours'''
        self.entity_neighbours.append(p[1])

    def p_error(self, p):
        logger.info("Syntax error in input! -> {}".format(p))
        exit()

    def build(self, lexer, topology):
        self.lexer = lexer
        self.topology = topology
        self.tokens = lexer.tokens
        self._parser = yacc.yacc(module=self, debug=False)
        self.entity_neighbours = []

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

        # update entities neighbours with ip, in_port
        for entity in self.topology.neighbours:
            for neighbour in self.topology.neighbours[entity]:
                self.topology.neighbours[entity][neighbour]["ip"] = self.topology.entities[neighbour]["ip"]
                self.topology.neighbours[entity][neighbour]["in_port"] = self.topology.entities[neighbour]["in_port"]

        logger.info("ENTITIES [{}]".format(self.topology.entities))
        logger.info("NEIGHBOURS [{}]".format(self.topology.neighbours))