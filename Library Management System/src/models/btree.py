from models.btreenode import BTreeNode

class BTree:
    """Complete B-tree implementation organized by book titles"""
    
    def __init__(self, t=3):
        """Initialize B-tree with minimum degree t (default=3)"""
        self.root = BTreeNode(t, True)
        self.t = t  # Minimum degree

    # Core insertion operation
    def insert(self, book):
        """Insert a book (organized by title)"""
        root = self.root
        if len(root.books) == (2 * self.t) - 1:  # Root is full
            new_root = BTreeNode(self.t, False)
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self.root = new_root
            self._insert_non_full(new_root, book)
        else:
            self._insert_non_full(root, book)

    def _insert_non_full(self, node, book):
        """Insert into a non-full node"""
        i = len(node.books) - 1
        if node.leaf:
            # Insert into leaf node
            node.books.append(None)  # Temporary placeholder
            while i >= 0 and book.title < node.books[i].title:
                node.books[i + 1] = node.books[i]
                i -= 1
            node.books[i + 1] = book
        else:
            # Find appropriate child
            while i >= 0 and book.title < node.books[i].title:
                i -= 1
            i += 1
            # Split child if full
            if len(node.children[i].books) == (2 * self.t) - 1:
                self._split_child(node, i)
                if book.title > node.books[i].title:
                    i += 1
            self._insert_non_full(node.children[i], book)

    def _split_child(self, parent, index):
        """Split a full child node"""
        t = self.t
        child = parent.children[index]
        new_child = BTreeNode(t, child.leaf)
        
        # Move median to parent
        parent.books.insert(index, child.books[t - 1])
        
        # Split books and children
        new_child.books = child.books[t:(2 * t - 1)]
        child.books = child.books[0:(t - 1)]
        
        if not child.leaf:
            new_child.children = child.children[t:(2 * t)]
            child.children = child.children[0:t]
        
        parent.children.insert(index + 1, new_child)

    # Optimized search operations
    def search(self, title):
        """Search by title (O(log n) time)"""
        return self._search_node(self.root, title)

    def _search_node(self, node, title):
        """Recursive node search"""
        if not node:
            return None
        i = 0
        while i < len(node.books) and title > node.books[i].title:
            i += 1
        if i < len(node.books) and title == node.books[i].title:
            return node.books[i]
        if node.leaf:
            return None
        return self._search_node(node.children[i], title)

    # Efficient update operation
    def update_availability(self, title, available):
        """Update book availability (O(log n))"""
        book = self.search(title)
        if book:
            book.available = available
            return True
        return False

    # Complete B-tree deletion
    def delete(self, title):
        """Delete book by title"""
        self._delete(self.root, title)
        # Update root if it becomes empty
        if len(self.root.books) == 0 and not self.root.leaf:
            self.root = self.root.children[0]

    def _delete(self, node, title):
        """Delete from node"""
        # Find key position
        idx = 0
        while idx < len(node.books) and title > node.books[idx].title:
            idx += 1
        
        # Case 1: Key in current node
        if idx < len(node.books) and node.books[idx].title == title:
            if node.leaf:
                self._delete_from_leaf(node, idx)
            else:
                self._delete_from_non_leaf(node, idx)
        else:
            # Case 2: Key in subtree
            if node.leaf:
                return  # Key doesn't exist
            
            # Ensure child has enough keys
            if len(node.children[idx].books) < self.t:
                self._fill_child(node, idx)
            
            # Determine which child to continue with
            if idx > len(node.books):
                self._delete(node.children[idx - 1], title)
            else:
                self._delete(node.children[idx], title)

    def _delete_from_leaf(self, node, idx):
        """Delete from leaf node"""
        node.books.pop(idx)

    def _delete_from_non_leaf(self, node, idx):
        """Delete from internal node"""
        title = node.books[idx].title
        
        # Case 3a: Left child has enough keys
        if len(node.children[idx].books) >= self.t:
            predecessor = self._get_predecessor(node, idx)
            node.books[idx] = predecessor
            self._delete(node.children[idx], predecessor.title)
        
        # Case 3b: Right child has enough keys
        elif len(node.children[idx + 1].books) >= self.t:
            successor = self._get_successor(node, idx)
            node.books[idx] = successor
            self._delete(node.children[idx + 1], successor.title)
        
        # Case 3c: Merge children
        else:
            self._merge_children(node, idx)
            self._delete(node.children[idx], title)

    def _get_predecessor(self, node, idx):
        """Get predecessor key"""
        current = node.children[idx]
        while not current.leaf:
            current = current.children[-1]
        return current.books[-1]

    def _get_successor(self, node, idx):
        """Get successor key"""
        current = node.children[idx + 1]
        while not current.leaf:
            current = current.children[0]
        return current.books[0]

    def _fill_child(self, node, idx):
        """Fill underflowing child"""
        if idx != 0 and len(node.children[idx - 1].books) >= self.t:
            self._borrow_from_prev(node, idx)
        elif idx != len(node.children) - 1 and len(node.children[idx + 1].books) >= self.t:
            self._borrow_from_next(node, idx)
        else:
            if idx != len(node.children) - 1:
                self._merge_children(node, idx)
            else:
                self._merge_children(node, idx - 1)

    def _borrow_from_prev(self, node, idx):
        """Borrow from left sibling"""
        child = node.children[idx]
        sibling = node.children[idx - 1]
        
        # Shift keys and children
        child.books.insert(0, node.books[idx - 1])
        if not child.leaf:
            child.children.insert(0, sibling.children.pop())
        
        node.books[idx - 1] = sibling.books.pop()

    def _borrow_from_next(self, node, idx):
        """Borrow from right sibling"""
        child = node.children[idx]
        sibling = node.children[idx + 1]
        
        # Shift keys and children
        child.books.append(node.books[idx])
        if not child.leaf:
            child.children.append(sibling.children.pop(0))
        
        node.books[idx] = sibling.books.pop(0)

    def _merge_children(self, node, idx):
        """Merge two children"""
        child = node.children[idx]
        sibling = node.children[idx + 1]
        
        # Move key from parent to child
        child.books.append(node.books.pop(idx))
        
        # Merge keys
        child.books.extend(sibling.books)
        
        # Merge children if not leaf
        if not child.leaf:
            child.children.extend(sibling.children)
        
        # Remove merged sibling
        node.children.pop(idx + 1)

    # Traversal with callback (memory efficient)
    def traverse(self, callback=None):
        if callback is not None:
          # ģʽ1��ʹ�ûص�����
          self._inorder_traverse(self.root, callback)
          return None
        else:
          # ģʽ2�����������б������ݾɴ��룩
          results = []
          self._inorder_traverse(self.root, lambda book: results.append(book))
          return results    
    def _inorder_traverse(self, node, callback):
           
        if node is None:
            return
        for i in range(len(node.books)):
            if not node.leaf:
                self._inorder_traverse(node.children[i], callback)
            callback(node.books[i])
        if not node.leaf:
            self._inorder_traverse(node.children[-1], callback)



    def print_tree(self, node=None, level=0):
        """Print the B-tree structure with titles"""
        if node is None:
            node = self.root

        print("  " * level + "|-- " + str([book.title for book in node.books]))
        if not node.leaf:
            for child in node.children:
                self.print_tree(child, level + 1)
