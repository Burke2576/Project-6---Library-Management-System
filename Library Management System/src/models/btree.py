from .btreenode import BTreeNode

class BTree:
    def __init__(self, t=2):
        """
        B树实现 / B-tree Implementation
        
        Args参数:
            t: 最小度数 (默认值2) / Minimum degree (default 2)
        """
        self.root = None  # 根节点 / Root node
        self.t = t        # 最小度数 / Minimum degree

    def insert(self, book):
        """
        插入书籍 / Insert a book
        Args参数:
            book: 要插入的书籍对象 / Book object to insert
        """
        if self.root is None:
            self.root = BTreeNode(self.t)
            self.root.books.append(book)
        else:
            if len(self.root.books) == 2 * self.t - 1:
                new_root = BTreeNode(self.t)
                new_root.children.append(self.root)
                self._split_child(new_root, 0)
                self.root = new_root
            self._insert_non_full(self.root, book)

    def _insert_non_full(self, node, book):
        """
        在非满节点中插入 / Insert into a non-full node
        Args参数:
            node: 当前节点 / Current node
            book: 要插入的书籍 / Book to insert
        """
        i = len(node.books) - 1
        
        if node.is_leaf():
            # 叶子节点直接插入 / Directly insert into leaf node
            node.books.append(None)  # 临时占位 / Temporary placeholder
            while i >= 0 and book.book_ID < node.books[i].book_ID:
                node.books[i + 1] = node.books[i]
                i -= 1
            node.books[i + 1] = book
        else:
            # 找到合适的子节点 / Find appropriate child node
            while i >= 0 and book.book_ID < node.books[i].book_ID:
                i -= 1
            i += 1
            
            # 检查子节点是否需要分裂 / Check if child needs splitting
            if len(node.children[i].books) == 2 * self.t - 1:
                self._split_child(node, i)
                if book.book_ID > node.books[i].book_ID:
                    i += 1
            self._insert_non_full(node.children[i], book)

    def _split_child(self, parent, index):
        """
        分裂子节点 / Split a child node
        Args参数:
            parent: 父节点 / Parent node
            index: 子节点索引 / Child index
        """
        t = self.t
        child = parent.children[index]
        new_node = BTreeNode(t)

        # 将中间键提升到父节点 / Promote middle key to parent
        parent.books.insert(index, child.books[t - 1])
        # 新节点获取右半部分键 / New node gets right half keys
        new_node.books = child.books[t:(2 * t - 1)]
        # 原节点保留左半部分键 / Original node keeps left half keys
        child.books = child.books[0:t - 1]

        # 如果不是叶子节点，还需要处理子节点 / If not leaf, handle children
        if not child.is_leaf():
            new_node.children = child.children[t:(2 * t)]
            child.children = child.children[0:t]

        # 将新节点添加到父节点 / Add new node to parent
        parent.children.insert(index + 1, new_node)

    def search(self, book_id, node=None):
        """
        搜索书籍 / Search for a book
        Args参数:
            book_id: 书籍ID / Book ID to search
            node: 起始节点(默认为根) / Starting node (default root)
        Returns返回:
            Book对象或None / Book object or None if not found
        """
        if node is None:
            node = self.root
            if node is None:
                return None
        
        i = 0
        while i < len(node.books) and book_id > node.books[i].book_ID:
            i += 1
        
        if i < len(node.books) and book_id == node.books[i].book_ID:
            return node.books[i]
        elif node.is_leaf():
            return None
        else:
            return self.search(book_id, node.children[i])

    def traverse(self, node=None, result=None):
        """
        中序遍历返回排序后的书籍 / In-order traversal returns sorted books
        Args参数:
            node: 起始节点 / Starting node
            result: 结果列表 / Result list
        Returns返回:
            排序后的书籍列表 / Sorted list of books
        """
        if result is None:
            result = []
        if node is None:
            node = self.root
            if node is None:
                return result
        
        i = 0
        while i < len(node.books):
            if not node.is_leaf():
                self.traverse(node.children[i], result)
            result.append(node.books[i])
            i += 1
        
        if not node.is_leaf():
            self.traverse(node.children[i], result)
        
        return result

    def delete_book(self, book_id):
        """
        删除书籍 / Delete a book
        Args参数:
            book_id: 要删除的书籍ID / Book ID to delete
        Returns返回:
            bool: 是否删除成功 / Whether deletion succeeded
        """
        if not self.root:
            return False
        
        if not self.search(book_id):
            return False
        
        self._delete(self.root, book_id)
        
        # 如果根节点没有键且不是叶子节点，降低树高
        # If root has no keys and is not leaf, reduce tree height
        if len(self.root.books) == 0 and not self.root.is_leaf():
            self.root = self.root.children[0]
        
        return True

    def _delete(self, node, book_id):
        """从节点删除 / Delete from a node"""
        idx = 0
        while idx < len(node.books) and book_id > node.books[idx].book_ID:
            idx += 1

        # 找到要删除的键 / Found key to delete
        if idx < len(node.books) and node.books[idx].book_ID == book_id:
            if node.is_leaf():
                node.books.pop(idx)
            else:
                self._delete_from_internal_node(node, idx)
        elif not node.is_leaf():
            self._delete_from_child(node, idx, book_id)

    def _delete_from_internal_node(self, node, idx):
        """从内部节点删除 / Delete from internal node"""
        # 前驱节点有足够键 / Predecessor has enough keys
        if len(node.children[idx].books) >= self.t:
            predecessor = self._get_predecessor(node, idx)
            node.books[idx] = predecessor
            self._delete(node.children[idx], predecessor.book_ID)
        # 后继节点有足够键 / Successor has enough keys
        elif len(node.children[idx + 1].books) >= self.t:
            successor = self._get_successor(node, idx)
            node.books[idx] = successor
            self._delete(node.children[idx + 1], successor.book_ID)
        # 需要合并子节点 / Need to merge children
        else:
            self._merge_children(node, idx)
            self._delete(node.children[idx], node.books[idx].book_ID)

    def _delete_from_child(self, node, idx, book_id):
        """从子节点删除 / Delete from child node"""
        # 子节点键不足时需要填充 / Fill child if it has insufficient keys
        if len(node.children[idx].books) == self.t - 1:
            self._fill_child(node, idx)
        
        # 填充后可能需要调整索引 / May need to adjust index after filling
        if idx > len(node.books):
            idx -= 1
        
        self._delete(node.children[idx], book_id)

    def _fill_child(self, node, idx):
        """填充键不足的子节点 / Fill child with insufficient keys"""
        # 尝试从左兄弟借键 / Try borrowing from left sibling
        if idx != 0 and len(node.children[idx - 1].books) >= self.t:
            self._borrow_from_left(node, idx)
        # 尝试从右兄弟借键 / Try borrowing from right sibling
        elif idx != len(node.books) and len(node.children[idx + 1].books) >= self.t:
            self._borrow_from_right(node, idx)
        # 需要合并子节点 / Need to merge children
        else:
            if idx != len(node.books):
                self._merge_children(node, idx)
            else:
                self._merge_children(node, idx - 1)

    def _borrow_from_left(self, node, idx):
        """从左兄弟借键 / Borrow from left sibling"""
        child = node.children[idx]
        sibling = node.children[idx - 1]
        
        # 父节点键下移 / Move parent key down
        child.books.insert(0, node.books[idx - 1])
        # 左兄弟最大键上移 / Move sibling's max key up
        node.books[idx - 1] = sibling.books.pop()
        
        # 如果不是叶子节点，还需要移动子节点 / If not leaf, move child
        if not sibling.is_leaf():
            child.children.insert(0, sibling.children.pop())

    def _borrow_from_right(self, node, idx):
        """从右兄弟借键 / Borrow from right sibling"""
        child = node.children[idx]
        sibling = node.children[idx + 1]
        
        # 父节点键下移 / Move parent key down
        child.books.append(node.books[idx])
        # 右兄弟最小键上移 / Move sibling's min key up
        node.books[idx] = sibling.books.pop(0)
        
        # 如果不是叶子节点，还需要移动子节点 / If not leaf, move child
        if not sibling.is_leaf():
            child.children.append(sibling.children.pop(0))

    def _merge_children(self, node, idx):
        """合并子节点 / Merge children"""
        child = node.children[idx]
        sibling = node.children[idx + 1]
        
        # 父节点键下移 / Move parent key down
        child.books.append(node.books.pop(idx))
        # 合并键 / Merge keys
        child.books.extend(sibling.books)
        
        # 如果不是叶子节点，还需要合并子节点 / If not leaf, merge children
        if not sibling.is_leaf():
            child.children.extend(sibling.children)
        
        # 移除被合并的兄弟节点 / Remove merged sibling
        node.children.pop(idx + 1)

    def _get_predecessor(self, node, idx):
        """获取前驱节点 / Get predecessor"""
        current = node.children[idx]
        while not current.is_leaf():
            current = current.children[-1]
        return current.books[-1]

    def _get_successor(self, node, idx):
        """获取后继节点 / Get successor"""
        current = node.children[idx + 1]
        while not current.is_leaf():
            current = current.children[0]
        return current.books[0]

    def visualize(self):
        """
        生成数学表达式风格的树形展示
        Generate mathematical expression style tree visualization
        Returns返回:
            可视化字符串 / Visualization string
        """
        if not self.root:
            return "空B树 / Empty B-tree"
        
        lines = []
        self._build_compact_tree(self.root, lines)
        return "\n".join(lines)

    def _build_compact_tree(self, node, lines):
        """递归构建紧凑型树形结构 / Recursively build compact tree structure"""
        book_ids = [str(book.book_ID) for book in node.books]
        node_str = f"[{'|'.join(book_ids)}]"
        
        if node.is_leaf() or not lines:
            lines.append(node_str)
        else:
            lines[-1] = node_str
        
        if not node.is_leaf():
            # 构建分支线 / Build branch lines
            branch_line = "  /" + " "*(len(node_str)-2) + "\\"
            lines.append(branch_line)
            
            # 构建子节点 / Build children
            children_line = ""
            for i, child in enumerate(node.children):
                child_book_ids = [str(b.book_ID) for b in child.books]
                if i == 0:  # 左子节点 / Left child
                    children_line += f"[{'|'.join(child_book_ids)}]"
                else:       # 右子节点 / Right child
                    children_line += " "*(len(node_str)-len(children_line)+1)
                    children_line += f"[{'|'.join(child_book_ids)}]"
            
            lines.append(children_line)

    def __str__(self):
        return self.visualize()
    
    def search(self, book_id, node=None, _is_outer_call=True):
        
        import time
        start = time.perf_counter()  # Windows和Unix通用高精度计时器 / Cross-platform high-resolution timer
        
        # 实际搜索逻辑 / Actual search logic
        if node is None:
            node = self.root
            if node is None:
                self._print_time(time.perf_counter() - start)
                return None
        
        i = 0
        while i < len(node.books) and book_id > node.books[i].book_ID:
            i += 1
        
        if i < len(node.books) and book_id == node.books[i].book_ID:
            if _is_outer_call:
                self._print_time(time.perf_counter() - start)
            return node.books[i]
        elif node.is_leaf():
            if _is_outer_call:
                self._print_time(time.perf_counter() - start)
            return None
        else:
            result = self.search(book_id, node.children[i], _is_outer_call=False)
            if _is_outer_call:
                self._print_time(time.perf_counter() - start)
            return result

    def _print_time(self, seconds):
    
        if seconds < 1e-6:  # 纳秒级（适用于极快操作）/ Nanosecond range (for very fast operations)
            value = seconds * 1e9
            unit = ("ns", "纳秒/nanoseconds")
        elif seconds < 1e-3:  # 微秒级 / Microsecond range
            value = seconds * 1e6
            unit = ("μs", "微秒/microseconds")
        elif seconds < 1:  # 毫秒级 / Millisecond range
            value = seconds * 1e3
            unit = ("ms", "毫秒/milliseconds")
        else:  # 秒级 / Second range
            value = seconds
            unit = ("s", "秒/seconds")
        
        # 统一打印格式 / Unified print format
        print(f"搜索耗时/Search time: {value:.3f}{unit[0]} ({unit[1]})")    