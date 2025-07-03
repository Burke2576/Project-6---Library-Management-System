import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from enum import Enum
import csv
import chardet
class Genre(Enum):
    FICTION = "FICTION"
    ROMANCE = "ROMANCE"
    SCIENCE = "SCIENCE"
    HISTORY = "HISTORY"
