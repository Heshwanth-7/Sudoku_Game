"""A singly linked list with head and tail pointers (written from scratch)."""


class Node:
    __slots__ = ("data", "next")

    def __init__(self, data, next=None):
        self.data = data
        self.next = next


class LinkedList:
    def __init__(self, items=None):
        self.head = None
        self.tail = None
        self._size = 0
        if items is not None:
            for item in items:
                self.append(item)

    def __len__(self):
        return self._size

    def __iter__(self):
        node = self.head
        while node is not None:
            yield node.data
            node = node.next

    def __repr__(self):
        return " -> ".join(repr(x) for x in self) + " -> None"

    def is_empty(self):
        return self._size == 0

    def append(self, data):
        """Add to the end. O(1) thanks to the tail pointer."""
        node = Node(data)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._size += 1

    def prepend(self, data):
        """Add to the front. O(1)."""
        node = Node(data, self.head)
        self.head = node
        if self.tail is None:
            self.tail = node
        self._size += 1

    def pop_front(self):
        """Remove and return the first item. O(1)."""
        if self.head is None:
            raise IndexError("pop from empty linked list")
        node = self.head
        self.head = node.next
        if self.head is None:
            self.tail = None
        self._size -= 1
        return node.data

    def remove_first(self, predicate):
        """Remove the first item for which predicate(item) is True. O(n)."""
        prev, cur = None, self.head
        while cur is not None:
            if predicate(cur.data):
                if prev is None:
                    self.head = cur.next
                else:
                    prev.next = cur.next
                if cur is self.tail:
                    self.tail = prev
                self._size -= 1
                return True
            prev, cur = cur, cur.next
        return False

    def clear(self):
        self.head = self.tail = None
        self._size = 0

    def to_list(self):
        return list(self)
