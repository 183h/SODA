from soda.helpers import flatten


class Behavior(object):
    def __init__(self, head=None):
        self.head = head
        self.tail = head

    def insert(self, node):
        if self.head is None:
            self.head = node
            self.tail = node
            return

        node.previous = self.tail
        self.tail.next = node
        self.tail = node

    def __str__(self):
        str = []

        n = self.head
        while n is not None:
            str.append(n.__str__())
            n = n.next

        return ",\n\t".join(str)


class Node(object):
    def __init__(self):
        self.next = None
        self.previous = None


class ActionNode(Node):
    def __init__(self, action, arguments=None):
        Node.__init__(self)
        self.action = action
        self.arguments = arguments

    def __str__(self):
        return self.action + '[Args(' + (', '.join(map(str, filter(None, flatten(self.arguments)))) if self.arguments is not None else '') + ')]'

    def execute(self, entity):
        action, arguments = self.action, self.arguments
        # Metóda vykoná akciu zodpovedajúcu kľúču action v slovníku entity._actions a
        # zároveň tejto metóde odovzdá argumenty z premennej arguments.
        entity._actions[action](arguments)

        if action == "BECOME":
            return "BECOME"

        return self.next # Po ukončení metóda vráti nasledujúci uzol v zozname.


class IfNode(Node):
    def __init__(self, condition):
        Node.__init__(self)
        self.condition = condition
        self.jump_endif = None
        self.jump_else = None

    def __str__(self):
        return ('If[Condition(' + self.condition + ')' +
                ', Endif(' + (str(self.jump_endif.id) if self.jump_endif is not None else '') + ')' +
                ', Else(' + (str(self.jump_else.id) if self.jump_else is not None else '') + ")]")

    def execute(self, entity):
        # Na začiatku testujeme, či platí podmienka uvedená v atribúte self.condition.
        # Pre toto testovanie používame akciu EVALUATE, ktorú obsahuje entita.
        condition_result = entity._actions["EVALUATE"](self.condition)

        if condition_result:
            n = self.next
            # Ak podmienka platí začneme vykonávať uzly, ktoré nasledujú za uzlom
            # IfNode pokiaľ nenarazíme na uzol EndIfNode alebo ElseNode. Ak narazíme
            # na uzol EndIfNode, ElseNode tak  metódu execute() ukončíme a vrátime
            # nasledujúci uzol tohto uzla v zozname.
            while (type(n) is not EndIfNode
                    and type(n) is not ElseNode):
                next_node = n.execute(entity)

                if next_node == "BECOME":
                    return "BECOME"

                n = next_node

            # Ak narazíme na uzol ElseNode nastavíme nasledujúci uzol na koniec
            # rozsahu ElseNode uzla. Podmienka platí takže správanie príslušné
            # ElseNode uzlu musíme preskočiť.
            if type(n) is ElseNode:
                n = self.jump_endif

            return n.next
        else:
            # Ak podmienka neplatí a IfNode nemá naviazaný ElseNode môžeme skočiť
            # na EndIfNode a pokračovať.
            if self.jump_else is None:
                return self.jump_endif.next
            # Ak IfNode má ElseNode tak vykonáme uzly, ktoré nasledujú za ElseNode
            # pokiaľ nenarazíme na IfNode.
            else:
                n = self.jump_else.next

                while type(n) is not EndIfNode:
                    next_node = n.execute(entity)

                    if next_node == "BECOME":
                        return "BECOME"

                    n = next_node

                return n.next


class ElseNode(Node):
    def __init__(self, id):
        Node.__init__(self)
        self.id = id
        self.scope_processed = False

    def __str__(self):
        return 'Else[' + 'Id(' + str(self.id) + ')]'

    def execute(self, entity):
        pass


class EndIfNode(Node):
    def __init__(self, id):
        Node.__init__(self)
        self.id = id
        self.scope_processed = False

    def __str__(self):
        return 'EndIf[' + 'Id(' + str(self.id) + ')]'

    def execute(self, entity):
        pass