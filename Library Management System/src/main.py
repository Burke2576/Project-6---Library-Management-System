import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from enum import Enum
import csv
import chardet
from models.Book import Book
from models.Genre import Genre
from gui.libraryapp import LibraryApp
from models.btree import BTree
from models.btreenode import BTreeNode

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()