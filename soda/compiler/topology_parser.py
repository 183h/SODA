import ply.yacc as yacc
from soda.helpers import open_file


class TopologyParser(object):
    def p_algorithm(self, p):
        ''' topology : entities'''

    def p_first_section(self, p):
        ''' entities : entity_line
                     | entity_line entities'''

    def p_first_section_line(self, p):
        ''' entity_line : DIGIT SEMICOLON IP SEMICOLON DIGIT DIGIT SEMICOLON neighbours SEMICOLON NAME'''
        self.topology.entities[p[1]] = {"ip": p[3], "in_port": p[5], "out_port": p[6], "state": p[10]}
        self.topology.neighbours[p[1]] = [{n: {"ip": None, "in_port": None, "out_port": None}} for n in self.entity_neighbours]
        self.entity_neighbours = []

    def p_neighbours(self, p):
        ''' neighbours : DIGIT
                       | DIGIT neighbours'''
        self.entity_neighbours.append(p[1])

    def p_error(self, p):
        print("Syntax error in input! -> {}".format(p))

    def build(self, lexer, topology):
        self.lexer = lexer
        self.topology = topology
        self.tokens = lexer.tokens
        self._parser = yacc.yacc(module=self)
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

        print ("Started topology parsing...")
        self._parser.parse("", lexer=self.lexer._lexer, tokenfunc=get_token)

        # update entities neighbours with ip, in_port, out_port
        for entity in self.topology.neighbours:
            for neighbours in self.topology.neighbours[entity]:
                for neighbour in neighbours:
                    neighbours[neighbour]["ip"] = self.topology.entities[neighbour]["ip"]
                    neighbours[neighbour]["in_port"] = self.topology.entities[neighbour]["in_port"]
                    neighbours[neighbour]["out_port"] = self.topology.entities[neighbour]["out_port"]

        print ("Ended topology parsing...")