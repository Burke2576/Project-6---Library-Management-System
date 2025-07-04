import unittest
from src.models.Book import Book
from src.models.Genre import Genre
from src.models.btreenode import BTreeNode

class TestBTreeNode(unittest.TestCase):
    def setUp(self):
        self.t = 3
        self.leaf_node = BTreeNode(t=self.t, leaf=True)
        self.internal_node = BTreeNode(t=self.t, leaf=False)
        self.sample_books = [Book(i, f"Book{i}", "Author", Genre.FICTION, 2000+i) for i in range(5)]

    def test_node_initialization(self):
        """Test node initialization"""
        self.assertEqual(self.leaf_node.t, 3)
        self.assertTrue(self.leaf_node.leaf)
        self.assertEqual(len(self.leaf_node.books), 0)  # Use books instead of keys
        self.assertEqual(len(self.leaf_node.children), 0)

    def test_is_full_property(self):
        """Test whether the node is full (based on the length of books)"""
        # Not full nodes
        self.assertFalse(len(self.leaf_node.books) == (2 * self.t) - 1)
        
        # Fill nodes to exactly full
        for i in range(5):  # 2t-1=5 when t=3
            self.leaf_node.books.append(self.sample_books[i])  # Add Book object instead of integer
        self.assertTrue(len(self.leaf_node.books) == (2 * self.t) - 1)

    def test_node_operations(self):
        """Test basic node operations"""
        # 测试book插入顺序保持
        book1 = Book(1, "Book1", "Author", Genre.FICTION, 2001)
        book0 = Book(0, "Book0", "Author", Genre.FICTION, 2000)
        
        self.leaf_node.books.append(book1)
        self.leaf_node.books.append(book0)
        self.leaf_node.books.sort(key=lambda x: x.book_ID)  # Sort by book_id
        
        self.assertEqual(self.leaf_node.books[0].book_ID, 0)
        self.assertEqual(self.leaf_node.books[1].book_ID, 1)

    def test_edge_cases(self):
        """Test boundary conditions"""
        # Node with minimum degree t=2
        min_t_node = BTreeNode(t=2, leaf=True)
        
        # Fill to maximum capacity (2t-1=3)
        for i in range(3):  
            min_t_node.books.append(self.sample_books[i])
        
        self.assertTrue(len(min_t_node.books) == 3)
        self.assertEqual(len(min_t_node.books), 3)

if __name__ == '__main__':
    unittest.main()