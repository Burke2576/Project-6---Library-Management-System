import sys
import os
import unittest

# 调试信息 - 打印当前文件路径
# Debugging Information - Print Current File Path
current_file = os.path.abspath(__file__)
print(f"\n当前测试文件路径/ Current test file path: {current_file}")

# 计算项目根目录（三级目录结构）
# Calculate the root directory of the project (three-level directory structure)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
src_path = os.path.join(project_root, "src")

# 备用方案：二级目录结构
# Alternative solution: Secondary directory structure
if not os.path.exists(src_path):
    project_root = os.path.dirname(os.path.dirname(current_file))
    src_path = os.path.join(project_root, "src")

print(f"计算项目根目录/ Calculated project root directory: {project_root}")
print(f"计算的src路径/ Calculated src path: {src_path}")

# 检查并添加路径
# Check and add path
if os.path.exists(src_path):
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    print(f"src目录存在,内容/ The src directory exists with the following content: {os.listdir(src_path)}")
else:
    print(f"错误: src目录不存在于/ Error: The src directory does not exist in {src_path}")
    print("当前工作目录内容/ Current working directory content:", os.listdir(project_root))
    raise ImportError("无法找到src目录/ Unable to find src directory")

# 打印最终Python路径
# Print the final Python path
print("\n最终Python路径/ Final Python path:")
for i, path in enumerate(sys.path, 1):
    print(f"{i}. {path}")

# 导入核心模块
# Import core module
try:
    from models.Book import Book
    from models.Genre import Genre
    from models.btree import BTree
    from models.btreenode import BTreeNode
    print("\n✅ 核心模块导入成功/ Core module imported successfully")
except ImportError as e:
    print(f"\n❌ 核心模块导入失败/ Core module import failed: {e}")
    if os.path.exists(src_path):
        print("\n尝试手动检查模块路径/ Attempt to manually check the module path:")
        models_path = os.path.join(src_path, "models")
        if os.path.exists(models_path):
            print(f"models 目录内容/ Models directory content: {os.listdir(models_path)}")
    raise

class TestBook(unittest.TestCase):
    def test_book_creation(self):
        """测试图书创建(所有属性)/ Test book creation (all attributes)"""
        book = Book(1, "Test Book", "Author", Genre.FICTION, 2020)
        self.assertEqual(book.book_ID, 1)
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, "Author")
        self.assertEqual(book.genre, Genre.FICTION)
        self.assertEqual(book.publication_year, 2020)
        self.assertTrue(book.available)
        
    def test_book_equality(self):
        """测试图书相等性(基于ID而非标题)/ Test book equality (based on ID rather than title)"""
        book1 = Book(1, "Same Title", "Author", Genre.FICTION, 2020)
        book2 = Book(1, "Different Title", "Other Author", Genre.ROMANCE, 2021)  # 相同/ID Same ID
        book3 = Book(2, "Same Title", "Author", Genre.FICTION, 2020)  # 不同/ID Different ID
        
        self.assertEqual(book1, book2)  # ID相同应相等 Same ID should be equal
        self.assertNotEqual(book1, book3)  # ID不同应不等 Different IDs should not be the same
        
    def test_book_comparison(self):
        """测试图书比较(基于标题)/ Comparison of Test Books (Based on Titles)"""
        book1 = Book(1, "A Title", "Author", Genre.FICTION, 2020)
        book2 = Book(2, "B Title", "Author", Genre.FICTION, 2020)
        
        self.assertLess(book1, book2)
        self.assertGreater(book2, book1)

class TestBTreeNode(unittest.TestCase):
    def test_node_creation(self):
        """测试B树节点初始化/ Test the initialization of B-tree nodes"""
        node = BTreeNode(t=3, leaf=True)
        self.assertEqual(node.t, 3)
        self.assertTrue(node.leaf)
        self.assertEqual(len(node.books), 0)
        self.assertEqual(len(node.children), 0)

class TestBTree(unittest.TestCase):
    def setUp(self):
        """初始化B树和测试数据/ Initialize B-tree and test data"""
        self.btree = BTree(t=3)
        self.books = [
            Book(1, "Book A", "Author 1", Genre.FICTION, 2000),
            Book(2, "Book B", "Author 2", Genre.ROMANCE, 2001),
            Book(3, "Book C", "Author 3", Genre.SCIENCE, 2002),
            Book(4, "Book D", "Author 4", Genre.HISTORY, 2003),
            Book(5, "Book E", "Author 5", Genre.FICTION, 2004),
        ]
        
    def test_insert_and_traverse(self):
        """测试插入和遍历(排序顺序)/ Test insertion and traversal (sorting order)"""
        for book in self.books:
            self.btree.insert(book)
            
        traversed = self.btree.traverse()
        self.assertEqual(len(traversed), len(self.books))
        titles = [book.title for book in traversed]
        self.assertEqual(titles, sorted(titles))
        
    def test_search(self):
        """测试搜索功能/ Test the search function"""
        for book in self.books:
            self.btree.insert(book)
            
        # 测试存在的书籍
        # Testing existing books
        found = self.btree.search("Book C")
        self.assertIsNotNone(found)
        self.assertEqual(found.title, "Book C")
        
        # 测试不存在的书籍
        # Testing non-existent books
        not_found = self.btree.search("Nonexistent Book")
        self.assertIsNone(not_found)
    
    def test_update_availability(self):
        """测试更新可用性状态/ Test update availability status"""
        for book in self.books:
            self.btree.insert(book)
            
        # 更新为不可用
        # Update to unavailable
        self.assertTrue(self.btree.update_availability(3, False))
        book = self.btree.search("Book C")
        self.assertFalse(book.available)
        
        # 更新不存在的书籍
        # Update non-existent books
        self.assertFalse(self.btree.update_availability(999, True))
        
    def test_delete_book(self):
        """测试删除书籍/ Test deleting books"""
        for book in self.books:
            self.btree.insert(book)
            
        initial_count = len(self.btree.traverse())
        
        # 删除存在的书籍
        # Delete existing books
        self.assertTrue(self.btree.delete_book(3))
        self.assertEqual(len(self.btree.traverse()), initial_count - 1)
        self.assertIsNone(self.btree.search("Book C"))
        
        # 尝试删除不存在的书籍
        # Attempt to delete non-existent books
        self.assertFalse(self.btree.delete_book(999))
        self.assertEqual(len(self.btree.traverse()), initial_count - 1)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("启动测试... Start testing ..")
    unittest.main(verbosity=2)