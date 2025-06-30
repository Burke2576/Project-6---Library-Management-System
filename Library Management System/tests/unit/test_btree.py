import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from models.btree import BTree
from models.Book import Book
from models.Genre import Genre

class TestBTree(unittest.TestCase):
    def setUp(self):
        """初始化B树和测试书籍 Initialize B-tree and test books"""
        self.btree = BTree(t=2)  # 使用较小的t值便于可视化 Using a smaller t-value facilitates visualization
        self.books = [
            Book(3, "Book C", "Author 3", Genre.SCIENCE, 2002),
            Book(1, "Book A", "Author 1", Genre.FICTION, 2000),
            Book(5, "Book E", "Author 5", Genre.FICTION, 2004),
            Book(2, "Book B", "Author 2", Genre.ROMANCE, 2001),
            Book(4, "Book D", "Author 4", Genre.HISTORY, 2003),
        ]
    
    def print_tree(self, message):
        """打印当前树结构和消息 Print the current tree structure and messages"""
        print(f"\n{'='*30}")
        print(message)
        print(f"{'='*30}")
        print(self.btree)
    
    def test_insert_and_traverse(self):
        """测试插入和遍历功能 Test insertion and traversal functions"""
        for book in self.books:
            self.btree.insert(book)
            self.print_tree(f"插入后 After insertion (ID: {book.book_ID})")
        
        traversed = self.btree.traverse()
        self.assertEqual(len(traversed), len(self.books))
        
        # 检查是否按ID排序
        # Check if sorted by ID
        ids = [book.book_ID for book in traversed]
        self.assertEqual(ids, sorted(ids))
    
    def test_search(self):
        """测试搜索功能 Test the search function"""
        for book in self.books:
            self.btree.insert(book)
        
        self.print_tree("搜索前的B树结构 B-tree structure before search")
        
        # 测试存在的书籍
        # Testing existing books
        found = self.btree.search(3)
        self.assertIsNotNone(found)
        self.assertEqual(found.title, "Book C")
        
        # 测试不存在的书籍
        # Testing non-existent books
        not_found = self.btree.search(99)
        self.assertIsNone(not_found)
    
    def test_delete(self):
        """测试删除功能 Test the deletion function"""
        for book in self.books:
            self.btree.insert(book)
        
        self.print_tree("删除前的B树结构 The B-tree structure before deletion")
        
        initial_count = len(self.btree.traverse())
        
        # 删除存在的书籍
        # Delete existing books
        self.assertTrue(self.btree.delete_book(3))
        self.print_tree("删除ID=3后的B树结构 Delete the B-tree structure with ID=3")
        self.assertEqual(len(self.btree.traverse()), initial_count - 1)
        
        # 删除不存在的书籍
        # Delete non-existent books
        self.assertFalse(self.btree.delete_book(99))
        self.assertEqual(len(self.btree.traverse()), initial_count - 1)

if __name__ == '__main__':
    unittest.main()