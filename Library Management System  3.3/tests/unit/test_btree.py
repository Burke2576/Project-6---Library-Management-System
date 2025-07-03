import unittest
import time
from src.models.btree import BTree
from src.models.Book import Book
from src.models.Genre import Genre

def format_time(delta):
    """Format time delta to a human-readable string with appropriate units"""
    if delta < 1e-6:
        return f"{delta * 1e9:.3f} ns"
    elif delta < 1e-3:
        return f"{delta * 1e6:.3f} μs"
    elif delta < 1:
        return f"{delta * 1e3:.3f} ms"
    else:
        return f"{delta:.6f} s"

class TestBTree(unittest.TestCase):
    def setUp(self):
        """Initialize a B-tree and sample books for testing"""
        self.btree = BTree(t=3)
        self.books = [
            Book(1, "Book A", "Author 1", Genre.FICTION, 2000),
            Book(2, "Book B", "Author 2", Genre.ROMANCE, 2001),
            Book(3, "Book C", "Author 3", Genre.SCIENCE, 2002),
            Book(4, "Book D", "Author 4", Genre.HISTORY, 2003),
            Book(5, "Book E", "Author 5", Genre.FICTION, 2004),
            Book(6, "Book F", "Author 6", Genre.FICTION, 2005),
            Book(7, "Book G", "Author 7", Genre.ROMANCE, 2006),
            Book(8, "Book H", "Author 8", Genre.SCIENCE, 2007),
            Book(9, "Book I", "Author 9", Genre.HISTORY, 2008),
            Book(10, "Book J", "Author 10", Genre.FICTION, 2009),
        ]

    def test_empty_tree(self):
        """Test operations on an empty tree"""
        self.assertEqual(len(self.btree.traverse()), 0)
        self.assertIsNone(self.btree.search("Any Book"))
        self.assertFalse(self.btree.update_availability("Any Book", True))
        self.btree.delete("Any Book")  # Should not raise an exception
        self.assertEqual(len(self.btree.traverse()), 0)

    def test_single_node_tree(self):
        """Test operations on a tree with only one node"""
        self.btree.insert(self.books[0])
        self.assertEqual(len(self.btree.traverse()), 1)
        self.assertIsNotNone(self.btree.search("Book A"))
        self.assertTrue(self.btree.update_availability("Book A", False))
        self.btree.delete("Book A")
        self.assertEqual(len(self.btree.traverse()), 0)

    def test_insert_and_traverse(self):
        """Test that inserted books can be traversed in sorted order"""
        for book in self.books:
            self.btree.insert(book)
        
        traversed = self.btree.traverse()
        self.assertEqual(len(traversed), len(self.books))
        titles = [book.title for book in traversed]
        self.assertEqual(titles, sorted(titles))

    def test_search(self):
        """Test searching for existing and non-existing books"""
        for book in self.books:
            self.btree.insert(book)
        
        # Test existing book
        start_time = time.perf_counter()
        found = self.btree.search("Book C")
        end_time = time.perf_counter()
        search_time = end_time - start_time
        print(f"Search time for 'Book C': {format_time(search_time)}")
        self.assertIsNotNone(found)
        self.assertEqual(found.title, "Book C")
        
        # Test non-existing book
        start_time = time.perf_counter()
        not_found = self.btree.search("Nonexistent Book")
        end_time = time.perf_counter()
        search_time = end_time - start_time
        print(f"Search time for 'Nonexistent Book': {format_time(search_time)}")
        self.assertIsNone(not_found)

    def test_update_availability(self):
        """Test updating a book's availability status"""
        for book in self.books:
            self.btree.insert(book)
        
        # Update availability to False
        self.assertTrue(self.btree.update_availability("Book C", False))
        book = self.btree.search("Book C")
        self.assertFalse(book.available)
        
        # Update non-existent book
        self.assertFalse(self.btree.update_availability("Nonexistent Book", True))

    def test_delete_book(self):
        """Test deleting existing and non-existing books"""
        for book in self.books:
            self.btree.insert(book)
        
        initial_count = len(self.btree.traverse())
        
        # Delete existing book
        self.btree.delete("Book C")
        self.assertEqual(len(self.btree.traverse()), initial_count - 1)
        self.assertIsNone(self.btree.search("Book C"))
        
        # Try to delete non-existent book
        self.btree.delete("Nonexistent Book")
        self.assertEqual(len(self.btree.traverse()), initial_count - 1)

    def test_delete_all_books(self):
        """Test deleting all books from the tree"""
        for book in self.books:
            self.btree.insert(book)
        
        for book in self.books:
            self.btree.delete(book.title)
        
        self.assertEqual(len(self.btree.traverse()), 0)
        self.assertIsNone(self.btree.search("Book A"))

    def test_edge_cases(self):
        """Test edge cases such as inserting duplicate books, deleting root node, etc."""
        # Insert duplicate books
        self.btree.insert(self.books[0])
        self.btree.insert(self.books[0])
        self.assertEqual(len(self.btree.traverse()), 2)  # Allow duplicate books

        # Delete a non-root node
        self.btree.delete("Book C")
        self.assertIsNone(self.btree.search("Book C"))

        # Insert and delete in a large dataset
        for i in range(100):
            book = Book(i + 100, f"Book {i + 100}", f"Author {i + 100}", Genre.FICTION, 2000 + i)
            self.btree.insert(book)
    
        self.assertEqual(len(self.btree.traverse()), 102)  # Include duplicates
    
        for i in range(100):
            self.btree.delete(f"Book {i + 100}")
    
        self.assertEqual(len(self.btree.traverse()), 2)  # Only the duplicates remain

    def test_large_dataset(self):
        """Test B-tree with a large dataset to verify its structure and performance"""
        for i in range(1000):
            book = Book(i + 1000, f"Book {i + 1000}", f"Author {i + 1000}", Genre.FICTION, 2000 + i)
            self.btree.insert(book)
    
        self.assertEqual(len(self.btree.traverse()), 1000)  # No duplicates

        # Test search performance
        start_time = time.perf_counter()
        for i in range(1000, 1100):
            self.btree.search(f"Book {i}")
        end_time = time.perf_counter()
        avg_search_time = (end_time - start_time) / 100
        print(f"Average search time in large tree: {format_time(avg_search_time)}")

    def test_tree_structure(self):
        """Test that the tree maintains proper structure after operations"""
        # Insert books to force node splits
        for i in range(1, 10):
            book = Book(i, f"Book {i}", f"Author {i}", Genre.FICTION, 2000 + i)
            self.btree.insert(book)
        
        # Verify tree structure by checking traversal order
        titles = [book.title for book in self.btree.traverse()]
        self.assertEqual(titles, sorted(titles))

        # Delete books to force node merges
        for i in range(1, 5):
            self.btree.delete(f"Book {i}")
        
        titles = [book.title for book in self.btree.traverse()]
        self.assertEqual(titles, sorted(titles))

    def test_different_min_degree(self):
        """Test B-tree with different minimum degrees"""
        for t in [2, 3, 4, 5]:
            btree = BTree(t=t)
            for book in self.books:
                btree.insert(book)
            
            self.assertEqual(len(btree.traverse()), len(self.books))
            titles = [book.title for book in btree.traverse()]
            self.assertEqual(titles, sorted(titles))

    def test_concurrent_operations(self):
        """Test mixed insert, delete, and search operations"""
        for i in range(1, 100):
            book = Book(i, f"Book {i}", f"Author {i}", Genre.FICTION, 2000 + i)
            self.btree.insert(book)
            
            if i % 10 == 0:
                # Search for existing books (using i instead of i//2 to ensure existence)
                self.assertIsNotNone(self.btree.search(f"Book {i}"))
                self.assertIsNone(self.btree.search(f"Nonexistent {i}"))
                
                # Delete some books (but not the ones we're searching for)
                if i > 20:
                    # Delete a book that's not the current one
                    delete_target = i - 10 if i - 10 != i else i - 5
                    self.btree.delete(f"Book {delete_target}")
        
        # Final verification
        remaining_books = self.btree.traverse()
        self.assertTrue(len(remaining_books) > 0)
        titles = [book.title for book in remaining_books]
        self.assertEqual(titles, sorted(titles))

    def test_print_tree(self):
        """Test printing the B-tree structure"""
        # Insert more books to ensure the tree has more than two levels
        for i in range(1, 100):
            book = Book(i, f"Book {i}", f"Author {i}", Genre.FICTION, 2000 + i)
            self.btree.insert(book)
        
        print("\nB-tree structure after insertions:")
        self.btree.print_tree()

    def test_insert_and_print_tree(self):
        """Test inserting books and printing the B-tree structure at specified intervals"""
        print("\nInserting books and printing B-tree structure at specified intervals:")
        print_every = 20
        for i in range(1, 100):
            book = Book(i, f"Book {i}", f"Author {i}", Genre.FICTION, 2000 + i)
            self.btree.insert(book)
            if i % print_every == 0:
                print(f"\nAfter inserting {i} books:")
                self.btree.print_tree()

if __name__ == '__main__':
    unittest.main()