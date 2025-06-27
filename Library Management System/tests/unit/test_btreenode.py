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

from src.gui.libraryapp import LibraryApp
from src.models.Book import Book
from src.models.Genre import Genre
from src.models.btree import BTree
from src.models.btreenode import BTreeNode

class TestBTreeNode(unittest.TestCase):
    def test_node_creation(self):
        """测试B树节点初始化/ Test B-tree node initialization"""
        node = BTreeNode(t=3, leaf=True)
        self.assertEqual(node.t, 3)
        self.assertEqual(len(node.books), 0)
        self.assertEqual(len(node.children), 0)