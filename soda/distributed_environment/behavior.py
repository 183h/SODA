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

        return ",\n".join(str)


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
        return self.action + '[Args(' + (', '.join(filter(None, self.arguments)) if self.arguments is not None else '') + ')]'

    def execute(self, entity):
        action, arguments = self.action, self.arguments
        entity.actions[action](arguments)

        return self.next


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
        condition_result = eval(self.condition.replace("\"", ""), {}, entity.__dict__)

        if condition_result:
            n = self.next

            while (type(n) is not EndIfNode
                    and type(n) is not ElseNode):
                next_node = n.execute(entity)
                n = next_node

            if type(n) is ElseNode:
                n = self.jump_endif

            return n.next
        else:
            if self.jump_else is None:
                return self.jump_endif.next
            else:
                n = self.jump_else.next

                while type(n) is not EndIfNode:
                    next_node = n.execute(entity)
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