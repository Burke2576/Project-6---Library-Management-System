class BTreeNode:
    def __init__(self, t, leaf=False):
        self.t = t          # Minimum degree
        self.books = []     # List of Book objects
        self.children = []  # List of child nodes
        self.leaf = leaf    # Is this a leaf node?

    def __str__(self):
        """用于打印节点时的友好显示 Friendly display for printing nodes"""
        book_ids = [str(book.book_ID) for book in self.books]
        return f"Node(books={book_ids}, leaf={self.leaf})"

    def visualize(self, level=0, output=None):
        """
        生成B树结构的层级可视化文本 Generate hierarchical visualization text with B-tree structure
        :param level: 当前节点层级（用于缩进）
        :param output: 存储输出的列表（递归使用）
        :return: 格式化后的树结构字符串列表
        """
        if output is None:
            output = []
        
        # 当前节点的书籍ID列表
        # List of book IDs for the current node
        prefix = "    " * level
        book_ids = [str(book.book_ID) for book in self.books]
        node_str = f"{prefix}[{'|'.join(book_ids)}]"
        output.append(node_str)
        
        # 递归处理子节点
        # Recursive processing of child nodes
        if not self.leaf:
            for child in self.children:
                child.visualize(level + 1, output)
        
        return output