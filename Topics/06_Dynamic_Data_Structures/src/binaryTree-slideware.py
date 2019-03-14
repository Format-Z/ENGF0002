class TreeNode():
    def __init__(self, key, value):
        self.left = None
        self.right = None
        self.key = key
        self.value = value

    def add(self, node):
        if node.key < self.key:
            if self.left is None:
                self.left = node
            else:
                self.left.add(node)
        else:
            if self.right is None:
                self.right = node
            else:
                self.right.add(node)

    # find the node with the specified key
    def find(self, key):
        if key == self.key:
            return self
        elif key < self.key:
            if self.left is None:
                return None
            else:
                return self.left.find(key)
        else:
            if self.right is None:
                return None
            else:
                return self.right.find(key)

    def child_count(self):
        count = 0
        if self.left is not None:
            count += 1
        if self.right is not None:
            count += 1
        return count

    def max(self):
        if self.right is None:
            return self.key
        else:
            return self.right.max()

    # see binaryTree.py for more fully commented version of this function
    def delete(self, key):
        if key == self.key: # this node is being deleted
            if self.left is None and self.right is None:
                return None          # Case 1: it's a leaf
            elif self.left is None:
                return self.right    # Case 2: no left child
            elif self.right is None:
                return self.left     # Case 3: no right child
            else:                    # Case 4: two children
                maxkey = self.left.max()
                maxnode = self.left.find(maxkey)
                self.left = self.left.delete(maxkey)
                self.key = maxnode.key
                self.value = maxnode.value
        elif key < self.key:
            if self.left is not None:
                self.left = self.left.delete(key)
        else:
            if self.right is not None:
                self.right = self.right.delete(key)
        return self
            
    def walk(self):
        if self.left is not None:
            yield from self.left.walk()
        yield (self.key, self.value)
        if self.right is not None:
            yield from self.right.walk()
        

class BinaryTree():
    def __init__(self):
        self.root = None
        self.count = 0

    def __len__(self):
        return self.count

    def add(self, key, value):
        node = TreeNode(key, value)
        if self.root is None:
            self.root = node
        else:
            self.root.add(node)
        self.count += 1

    # delete the item matching the key from the tree, and return the
    # value matching the key, or None if no match is found
    def delete(self, key):
        if self.root is None:
            return None
        self.root = self.root.delete(key)
        self.count -= 1


    # return the value matching the key, or None if no match is found
    def get(self, key):
        if self.root is None:
            return None
        node = self.root.find(key)
        if node is None:
            return None
        return node.value

    # create a generator for walking the tree in order
    def walk(self):
        if self.root is None:
            return
        yield from self.root.walk()
                


import random
import pytest

@pytest.fixture
def two_lists():
    items = list(range(100))
    old_items = items.copy()
    random.shuffle(items)
    return (items, old_items)

def test_basics():
    return
    tree = BinaryTree()
    tree.add(2,2)
    tree.add(1,1)
    tree.add(3,3)
    count = 1
    for key, value in tree.walk():
        assert key == count
        assert value == count
        count += 1
    assert(tree.get(1) is not None)
    assert(tree.get(2) is not None)
    assert(tree.get(3) is not None)
    tree.delete(2)
    assert(tree.get(1) is not None)
    assert(tree.get(2) is None)
    assert(tree.get(3) is not None)
    tree.delete(1)
    assert(tree.get(1) is None)
    assert(tree.get(2) is None)
    assert(tree.get(3) is not None)
    tree.delete(1)  # delete something that's no there
    assert(tree.get(1) is None)
    assert(tree.get(2) is None)
    assert(tree.get(3) is not None)
    tree.delete(3)
    assert(tree.get(1) is None)
    assert(tree.get(2) is None)
    assert(tree.get(3) is None)

def test_basics2():
    tree = BinaryTree()
    tree.add(3,3)
    tree.add(2,2)
    tree.add(1,1)
    count = 1
    for key, value in tree.walk():
        assert key == count
        assert value == count
        count += 1
    assert(tree.get(1) is not None)
    assert(tree.get(2) is not None)
    assert(tree.get(3) is not None)
    tree.delete(3)
    assert(tree.get(1) is not None)
    assert(tree.get(2) is not None)
    assert(tree.get(3) is None)
    tree.delete(2)
    assert(tree.get(1) is not None)
    assert(tree.get(2) is None)
    assert(tree.get(3) is None)
    tree.delete(1)  # delete something that's no there
    assert(tree.get(1) is None)
    assert(tree.get(2) is None)
    assert(tree.get(3) is None)

def test_demo():
    tree = BinaryTree()
    tree.add("Karp", ("x30406", "MPEB 6.20"))
    tree.add("Handley", ("x37679", "MPEB 6.21"))
    tree.add("Vissichio", ("x31397", "MPEB 6.19"))
    phone, office = tree.get("Handley")
    assert phone == "x37679"

def test_demo2():
    tree = BinaryTree()
    tree.add("Karp", ("x30406", "MPEB 6.20"))
    tree.add("Handley", ("x37679", "MPEB 6.21"))
    tree.add("Vissichio", ("x31397", "MPEB 6.19"))
    phone, office = tree.get("Handley")
    assert phone == "x37679"

    # your're fired!
    tree.delete("Handley")
    assert tree.get("Handley") == None

def test_add_get(two_lists):
    items, _ = two_lists
    tree = BinaryTree()
    for i in items[:50]:
        tree.add(i, i)

    for i in items[:50]:
        value = tree.get(i)
        assert tree.get(i) is not None

    for i in items[50:]:
        assert tree.get(i) is None

def test_add_delete_len(two_lists):
    items = list(range(100))
    random.shuffle(items)   # randomly shuffled list from 0 to 99
    # Test init and add
    tree = BinaryTree()
    for i in items:
        tree.add(i,i)                    # Test add
    assert tree.root.max() == 99         # Test max

    # Test remove, get, len
    random.shuffle(items)
    count = len(items)
    for i in items:     # Helper iterator
        assert len(tree) == count   # Test len
        assert tree.get(i) is not None  # Test isin
        tree.delete(i)                  # Test remove
        assert tree.get(i) is None      # Test get
        count -= 1


def test_walk(two_lists):
    items = list(range(100))        # [0, ..., 99]
    random.shuffle(items)           # shuffle

    tree = BinaryTree()
    for i in items:
        tree.add(i,str(i))

    assert len(items) == len(tree)    # Test len

    # Check that iterator returns elements in order
    count = 0
    for key,value in tree.walk():
        assert key == count  # Check the order is the same
        assert value == str(count)
        count += 1
