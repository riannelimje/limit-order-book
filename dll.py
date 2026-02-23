class DLLNode:
    """Node in a doubly-linked list storing an Order."""
    def __init__(self, order):
        self.order = order
        self.prev = None
        self.next = None
        self.parent = None  # reference to parent DLL (price level)

class DoublyLinkedList:
    """FIFO queue implemented with a DLL."""
    def __init__(self, price):
        self.head = None
        self.tail = None
        self.size = 0
        self.price = price  # store price for easy access in order book

    def append(self, order):
        node = DLLNode(order)
        node.parent = self
        if not self.head:
            self.head = self.tail = node
        else:
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
        self.size += 1
        return node  # return node so we can store it in order_map

    def pop_front(self):
        if not self.head:
            return None
        node = self.head
        if self.head == self.tail:
            self.head = self.tail = None
        else:
            self.head = node.next
            self.head.prev = None
        node.next = node.prev = None
        self.size -= 1
        return node

    def remove(self, node):
        """Remove an arbitrary node in O(1)."""
        if node.prev:
            node.prev.next = node.next
        else:
            # node is head
            self.head = node.next

        if node.next:
            node.next.prev = node.prev
        else:
            # node is tail
            self.tail = node.prev

        node.prev = node.next = None
        self.size -= 1

    @property
    def _size(self):
        """Backward-compatible alias; some callers expect `_size`."""
        return self.size

    def is_empty(self):
        return self.size == 0
    
    def __len__(self):
        return self._size

    def __getitem__(self, index):
        """Allow list-style access (0-based) to orders in the queue."""
        if not isinstance(index, int) or index < 0:
            raise IndexError("index must be a non-negative integer")

        current = self.head
        i = 0
        while current and i < index:
            current = current.next
            i += 1

        if current is None:
            raise IndexError("index out of range")

        return current.order
    
    def first(self):
        return self.head.order if self.head else None
    
    def __iter__(self):
        """Iterate over orders in FIFO order."""
        current = self.head
        while current:
            yield current.order # memory efficient - no need to create temp list of orders + lazy evaluation - gives one order at a time
            current = current.next