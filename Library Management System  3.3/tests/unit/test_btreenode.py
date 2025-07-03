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
        """测试节点初始化"""
        self.assertEqual(self.leaf_node.t, 3)
        self.assertTrue(self.leaf_node.leaf)
        self.assertEqual(len(self.leaf_node.books), 0)  # 使用books而不是keys
        self.assertEqual(len(self.leaf_node.children), 0)

    def test_is_full_property(self):
        """测试节点是否满的判断（基于books长度）"""
        # 未满节点
        self.assertFalse(len(self.leaf_node.books) == (2 * self.t) - 1)
        
        # 填充节点到刚好满
        for i in range(5):  # 2t-1=5 when t=3
            self.leaf_node.books.append(self.sample_books[i])  # 添加Book对象而不是整数
        self.assertTrue(len(self.leaf_node.books) == (2 * self.t) - 1)

    def test_node_operations(self):
        """测试基础节点操作"""
        # 测试book插入顺序保持
        book1 = Book(1, "Book1", "Author", Genre.FICTION, 2001)
        book0 = Book(0, "Book0", "Author", Genre.FICTION, 2000)
        
        self.leaf_node.books.append(book1)
        self.leaf_node.books.append(book0)
        self.leaf_node.books.sort(key=lambda x: x.book_ID)  # 根据book_id排序
        
        self.assertEqual(self.leaf_node.books[0].book_ID, 0)
        self.assertEqual(self.leaf_node.books[1].book_ID, 1)

    def test_edge_cases(self):
        """测试边界条件"""
        # 最小度数t=2的节点
        min_t_node = BTreeNode(t=2, leaf=True)
        
        # 填充到最大容量 (2t-1=3)
        for i in range(3):  
            min_t_node.books.append(self.sample_books[i])
        
        self.assertTrue(len(min_t_node.books) == 3)
        self.assertEqual(len(min_t_node.books), 3)

if __name__ == '__main__':
    unittest.main()