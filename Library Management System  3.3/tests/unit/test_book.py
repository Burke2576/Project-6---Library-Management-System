import sys
import os


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.path.append(os.path.join(PROJECT_ROOT, "src"))

import unittest
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from enum import Enum
import csv
import chardet

from src.gui.libraryapp import LibraryApp
from src.models.Book import Book
from src.models.Genre import Genre
from src.models.btree import BTree
from src.models.btreenode import BTreeNode


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
        
        self.assertEqual(book1.title, book2.title)
        self.assertNotEqual(book1, book3)
        
    def test_book_comparison(self):
        """Test book comparison operators (based on title)"""
        book1 = Book(1, "A Title", "Author", Genre.FICTION, 2020)
        book2 = Book(2, "B Title", "Author", Genre.FICTION, 2020)
        
        self.assertLess(book1, book2)
        self.assertGreater(book2, book1)