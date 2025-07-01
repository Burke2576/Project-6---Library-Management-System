import sys
import os

# 获取项目根目录（"Library Management System/" 的路径）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 将 src/ 目录加入 Python 路径
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

import unittest
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from enum import Enum
import csv
import chardet

from gui.libraryapp import LibraryApp
from models.Book import Book
from models.Genre import Genre
from models.btree import BTree
from models.btreenode import BTreeNode


class TestBook(unittest.TestCase):
    def test_book_creation(self):
        """Test basic book creation with all attributes"""
        book = Book(1, "Test Book", "Author", Genre.FICTION, 2020)
        self.assertEqual(book.book_ID, 1)
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, "Author")
        self.assertEqual(book.genre, Genre.FICTION)
        self.assertEqual(book.publication_year, 2020)
        self.assertTrue(book.available)
        
    def test_book_equality(self):
        """Test that book equality is based on title only"""
        book1 = Book(1, "Same Title", "Author", Genre.FICTION, 2020)
        book2 = Book(2, "Same Title", "Different Author", Genre.ROMANCE, 2021)
        book3 = Book(3, "Different Title", "Author", Genre.FICTION, 2020)
        
        self.assertEqual(book1, book2)
        self.assertNotEqual(book1, book3)
        
    def test_book_comparison(self):
        """Test book comparison operators (based on title)"""
        book1 = Book(1, "A Title", "Author", Genre.FICTION, 2020)
        book2 = Book(2, "B Title", "Author", Genre.FICTION, 2020)
        
        self.assertLess(book1, book2)
        self.assertGreater(book2, book1)

class TestBTreeNode(unittest.TestCase):
    def test_node_creation(self):
        """Test B-tree node initialization"""
        node = BTreeNode(t=3, leaf=True)
        self.assertEqual(node.t, 3)
        self.assertTrue(node.leaf)
        self.assertEqual(len(node.books), 0)
        self.assertEqual(len(node.children), 0)

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
        ]
        
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
        found = self.btree.search("Book C")
        self.assertIsNotNone(found)
        self.assertEqual(found.title, "Book C")
        
        # Test non-existing book
        not_found = self.btree.search("Nonexistent Book")
        self.assertIsNone(not_found)
    
    def test_update_availability(self):
        """Test updating a book's availability status"""
        for book in self.books:
            self.btree.insert(book)
            
        # Update availability to False
        self.assertTrue(self.btree.update_availability(3, False))
        book = self.btree.search("Book C")
        self.assertFalse(book.available)
        
        # Update non-existent book
        self.assertFalse(self.btree.update_availability(999, True))
        
    def test_delete_book(self):
        """Test deleting existing and non-existing books"""
        for book in self.books:
            self.btree.insert(book)
            
        initial_count = len(self.btree.traverse())
        
        # Delete existing book
        self.assertTrue(self.btree.delete_book(3))
        self.assertEqual(len(self.btree.traverse()), initial_count - 1)
        self.assertIsNone(self.btree.search("Book C"))
        
        # Try to delete non-existent book
        self.assertFalse(self.btree.delete_book(999))
        self.assertEqual(len(self.btree.traverse()), initial_count - 1)

if __name__ == '__main__':
    unittest.main()




