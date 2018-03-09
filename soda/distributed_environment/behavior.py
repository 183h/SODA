class Behavior(object):
    def __init__(self, head=None):
        self.head = head
        self.tail = head

    def insert(self, node):
        if self.head is None:
            self.head = node
            self.tail = node

        self.tail.next = node
        self.tail = node

    def __str__(self):
        str = []

        n = self.head
        while n is not None:
            str.append(n.action + "(" + " ".join(n.arguments) + ")")
            n = n.next

        return ", ".join(str)


class Node(object):
    def __init__(self, action, arguments):
        self.action = action
        self.arguments = arguments
        self.next = None
        self.jump = None