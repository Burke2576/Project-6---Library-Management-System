import sys
import os

# 获取项目根目录（"Library Management System/" 的路径）
# Retrieve the root directory of the project (path to 'Library Management System/')
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 将 src/ 目录加入 Python 路径
# Add src/directory to Python path
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
        """测试所有属性的基本书籍创建/ Test basic book creation with all attributes"""
        book = Book(1, "Test Book", "Author", Genre.FICTION, 2020)
        self.assertEqual(book.book_ID, 1)
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, "Author")
        self.assertEqual(book.genre, Genre.FICTION)
        self.assertEqual(book.publication_year, 2020)
        self.assertTrue(book.available)
        
    def test_book_equality(self):
        """测试书籍的平等性仅基于标题/ Test that book equality is based on title only"""
        book1 = Book(1, "Same Title", "Author", Genre.FICTION, 2020)
        book2 = Book(2, "Same Title", "Different Author", Genre.ROMANCE, 2021)
        book3 = Book(3, "Different Title", "Author", Genre.FICTION, 2020)
        
        self.assertEqual(book1.title, book2.title)
        self.assertNotEqual(book1, book3)
        
    def test_book_comparison(self):
        """测试比较运算符(基于标题)/ Test book comparison operators (based on title)"""
        book1 = Book(1, "A Title", "Author", Genre.FICTION, 2020)
        book2 = Book(2, "B Title", "Author", Genre.FICTION, 2020)
        
        self.assertLess(book1, book2)
        self.assertGreater(book2, book1)