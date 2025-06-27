class BTreeNode:
    def __init__(self, t, *args, **kwargs):
        """
        B树节点类 / B-tree Node Class
        Args参数:
            t: 最小度数 / Minimum degree
            *args, **kwargs: 用于兼容接收leaf参数但不使用 / For backward compatibility (ignored)
        """
        self.t = t          # 最小度数 / Minimum degree
        self.books = []     # 存储书籍对象列表 / List of Book objects
        self.children = []  # 子节点列表 / List of child nodes

    def is_leaf(self):
        """
        判断是否为叶子节点 / Check if the node is a leaf
        Returns返回:
            bool: True如果是叶子节点 / if leaf node
        """
        return len(self.children) == 0

    def __str__(self):
        """
        节点字符串表示 / Node string representation
        Returns返回:
            str: 格式化后的节点信息 / Formatted node info
        """
        book_ids = [str(book.book_ID) for book in self.books]
        return f"Node(keys={book_ids}, leaf={self.is_leaf()})"

    def visualize(self, level=0, output=None):
        """
        生成B树结构的层级可视化文本 / Generate hierarchical visualization
        Args参数:
            level: 当前节点层级（用于缩进） / Current level (for indentation)
            output: 存储输出的列表（递归使用）/ Output list (recursive use)
        Returns返回:
            list: 格式化后的树结构字符串列表 / Formatted tree structure strings
        """
        if output is None:
            output = []
        
        prefix = "  " * level
        book_ids = [str(book.book_ID) for book in self.books]
        output.append(f"{prefix}[{'|'.join(book_ids)}]")
        
        if not self.is_leaf():
            for child in self.children:
                child.visualize(level + 1, output)
        
        return output