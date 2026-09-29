"""A LIFO stack built on top of our own LinkedList (top = head of the list)."""

from .linked_list import LinkedList


class Stack:
    def __init__(self):
        self._items = LinkedList()

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        """Iterate from top to bottom."""
        return iter(self._items)

    def is_empty(self):
        return self._items.is_empty()

    def push(self, item):
        self._items.prepend(item)  # O(1)

    def pop(self):
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop_front()  # O(1)

    def peek(self):
        if self.is_empty():
            raise IndexError("peek at empty stack")
        return self._items.head.data

    def clear(self):
        self._items.clear()
