from models.btreenode import BTreeNode

class BTree:
    def __init__(self, t=2):
        """初始化B树 Initialize B-tree"""
        self.root = None
        self.t = t  # 最小度数 Minimum degree
    
    def insert(self, book):
        """插入一本新书到B树中 Insert a new book into the B-tree"""
        if self.root is None:
            self.root = BTreeNode(self.t, True)
            self.root.books.append(book)
        else:
            if len(self.root.books) == 2 * self.t - 1:
                new_root = BTreeNode(self.t, False)
                new_root.children.append(self.root)
                self._split_child(new_root, 0)
                self.root = new_root
            self._insert_non_full(self.root, book)
        
        # 打印插入后的树结构 Print tree structure after insertion
        print(f"\n插入后 After insertion (ID: {book.book_ID})")
        print("="*30)
        print(self.visualize())
        print("="*30)
    
    def _insert_non_full(self, node, book):
        """在非满节点中插入书籍 Insert book into non-full node"""
        i = len(node.books) - 1
        if node.leaf:
            node.books.append(None)
            while i >= 0 and book.book_ID < node.books[i].book_ID:
                node.books[i + 1] = node.books[i]
                i -= 1
            node.books[i + 1] = book
        else:
            while i >= 0 and book.book_ID < node.books[i].book_ID:
                i -= 1
            i += 1
            if len(node.children[i].books) == 2 * self.t - 1:
                self._split_child(node, i)
                if book.book_ID > node.books[i].book_ID:
                    i += 1
            self._insert_non_full(node.children[i], book)
    
    def _split_child(self, parent, index):
        """分裂子节点 Split child node"""
        t = self.t
        child = parent.children[index]
        new_node = BTreeNode(t, child.leaf)
        
        parent.books.insert(index, child.books[t - 1])
        parent.children.insert(index + 1, new_node)
        
        new_node.books = child.books[t:(2 * t) - 1]
        child.books = child.books[0:t - 1]
        
        if not child.leaf:
            new_node.children = child.children[t:2 * t]
            child.children = child.children[0:t]
    
    def visualize(self):
        """生成B树的文本可视化 Generate B-tree visualization"""
        if not self.root:
            return "空B树 Empty B-tree"
        
        # 单节点情况 Single node case
        if self.root.leaf or len(self.root.children) == 0:
            return str([book.book_ID for book in self.root.books])
        
        # 构建根节点行 Build root line
        root_str = str([book.book_ID for book in self.root.books])
        
        # 构建子节点行 Build children lines
        children_str = []
        for child in self.root.children:
            children_str.append(str([book.book_ID for book in child.books]))
        
        # 格式化输出 Format output
        if len(children_str) == 2:
            return f"{root_str}\n / \\ \n{children_str[0]} {children_str[1]}"
        elif len(children_str) == 1:
            return f"{root_str}\n / \n{children_str[0]}"
        else:
            return f"{root_str}\n{' '.join(children_str)}"
    
    def search(self, book_id, node=None):
        """根据ID搜索书籍 Search book by ID"""
        if node is None:
            node = self.root
            if node is None:
                return None
        
        i = 0
        while i < len(node.books) and book_id > node.books[i].book_ID:
            i += 1
        
        if i < len(node.books) and book_id == node.books[i].book_ID:
            return node.books[i]
        elif node.leaf:
            return None
        else:
            return self.search(book_id, node.children[i])
    
    def traverse(self, node=None, result=None):
        """遍历B树返回所有书籍（按ID排序） Traverse B-tree (sorted by ID)"""
        if result is None:
            result = []
        if node is None:
            node = self.root
            if node is None:
                return result
        
        i = 0
        while i < len(node.books):
            if not node.leaf:
                self.traverse(node.children[i], result)
            result.append(node.books[i])
            i += 1
        
        if not node.leaf:
            self.traverse(node.children[i], result)
        
        return result
    
    def delete_book(self, book_id):
        """根据ID删除书籍 Delete book by ID"""
        if not self.root:
            return False
        
        print("\n删除前的B树结构 Before deletion:")
        print("="*30)
        print(self.visualize())
        print("="*30)
        
        if not self.search(book_id):
            return False
        
        self._delete(self.root, book_id)
        
        if len(self.root.books) == 0 and not self.root.leaf:
            self.root = self.root.children[0]
        
        print("\n删除后的B树结构 After deletion:")
        print("="*30)
        print(self.visualize())
        print("="*30)
        return True
    
    def _delete(self, node, book_id):
        """从指定节点删除书籍 Delete from specific node"""
        idx = 0
        while idx < len(node.books) and book_id > node.books[idx].book_ID:
            idx += 1
        
        if idx < len(node.books) and node.books[idx].book_ID == book_id:
            if node.leaf:
                node.books.pop(idx)
                return True
            else:
                return self._delete_from_internal_node(node, idx)
        else:
            if node.leaf:
                return False
            else:
                return self._delete_from_child(node, idx, book_id)
    
    def _delete_from_internal_node(self, node, idx):
        """从内部节点删除键 Delete from internal node"""
        if len(node.children[idx].books) >= self.t:
            predecessor = self._get_predecessor(node, idx)
            node.books[idx] = predecessor
            return self._delete(node.children[idx], predecessor.book_ID)
        elif len(node.children[idx + 1].books) >= self.t:
            successor = self._get_successor(node, idx)
            node.books[idx] = successor
            return self._delete(node.children[idx + 1], successor.book_ID)
        else:
            self._merge_children(node, idx)
            return self._delete(node.children[idx], node.books[idx].book_ID)
    
    def _delete_from_child(self, node, idx, book_id):
        """从子节点删除键 Delete from child node"""
        if len(node.children[idx].books) == self.t - 1:
            self._fill_child(node, idx)
        
        if idx > len(node.books):
            idx -= 1
        
        return self._delete(node.children[idx], book_id)
    
    def _fill_child(self, node, idx):
        """填充键不足的子节点 Fill child node with insufficient keys"""
        if idx != 0 and len(node.children[idx - 1].books) >= self.t:
            self._borrow_from_left(node, idx)
        elif idx != len(node.books) and len(node.children[idx + 1].books) >= self.t:
            self._borrow_from_right(node, idx)
        else:
            if idx != len(node.books):
                self._merge_children(node, idx)
            else:
                self._merge_children(node, idx - 1)
    
    def _borrow_from_left(self, node, idx):
        """从左兄弟借键 Borrow key from left sibling"""
        child = node.children[idx]
        sibling = node.children[idx - 1]
        
        child.books.insert(0, node.books[idx - 1])
        node.books[idx - 1] = sibling.books.pop()
        
        if not sibling.leaf:
            child.children.insert(0, sibling.children.pop())
    
    def _borrow_from_right(self, node, idx):
        """从右兄弟借键 Borrow key from right sibling"""
        child = node.children[idx]
        sibling = node.children[idx + 1]
        
        child.books.append(node.books[idx])
        node.books[idx] = sibling.books.pop(0)
        
        if not sibling.leaf:
            child.children.append(sibling.children.pop(0))
    
    def _merge_children(self, node, idx):
        """合并子节点 Merge child nodes"""
        child = node.children[idx]
        sibling = node.children[idx + 1]
        
        child.books.append(node.books.pop(idx))
        child.books.extend(sibling.books)
        
        if not sibling.leaf:
            child.children.extend(sibling.children)
        
        node.children.pop(idx + 1)
    
    def _get_predecessor(self, node, idx):
        """获取前驱节点 Get predecessor"""
        current = node.children[idx]
        while not current.leaf:
            current = current.children[-1]
        return current.books[-1]
    
    def _get_successor(self, node, idx):
        """获取后继节点 Get successor"""
        current = node.children[idx + 1]
        while not current.leaf:
            current = current.children[0]
        return current.books[0]
    
    def __str__(self):
        return self.visualize()