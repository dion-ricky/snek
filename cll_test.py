class Node:
    def __init__(self, data):
        self.data = data
        self.next = None
class CLL:
    def __init__(self):
        self.head = None
        self.tail = None
        self.count = 0

    def add_first(self, data):
        if self.count == 0:
            self.head = Node(data)
            self.tail = self.head
            self.head.next = self.head
            self.count += 1

        else:
            n = Node(data)
            n.next = self.head
            self.head = n
            self.tail.next = n
            self.count += 1

    def remove_first(self):
        if self.count == 0:
            return
        else:
            old = self.head
            self.head = self.head.next
            self.tail.next = self.head
            old = None
            self.count -= 1

    def add_last(self, data):
        if self.count == 0:
            self.add_first(data)
        else:
            n = Node(data)
            self.tail.next = n
            n.next = self.head
            self.tail = n
            self.count += 1

    def remove_last(self):
        if self.count == 0:
            return
        else:
            old = self.tail

            t = self.head
            while t.next != self.tail:
                t = t.next

            self.tail = t
            t.next = self.head
            self.count -= 1

    def remove(self, data):
        t = self.head
        while True:
            if t.next.data == data:
                temp = t.next
                t.next = t.next.next
                temp = None
                self.count -= 1
                break

            if t.next == self.head:
                break

            t = t.next

    def print_all(self):
        t = self.head
        while True:
            print(t.data, end='')

            if t.next == self.head:
                print()
                break

            print(" -> ", end='')

            t = t.next

if __name__ == "__main__":
    cll = CLL()

    cll.add_first((1, 10))
    cll.print_all()
    cll.add_last((0, 2))
    cll.add_last((0, 3))
    cll.add_last((0, 4))
    cll.add_last((0, 5))
    cll.add_last((0, 6))
    cll.print_all()
    cll.remove_last()
    cll.print_all()
    cll.remove((0,4))
    cll.print_all()
