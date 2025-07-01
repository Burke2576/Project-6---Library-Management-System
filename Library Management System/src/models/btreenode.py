class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t  # Minimum degree (defines the range for number of keys)
        self.books = []  # List of books
        self.children = []  # List of child nodes
        self.leaf = leaf