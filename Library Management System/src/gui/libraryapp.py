import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from enum import Enum
import csv
import chardet

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from enum import Enum
import csv
import chardet
from models.Book import Book
from models.Genre import Genre
from models.btree import BTree
from models.btreenode import BTreeNode

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1000x800")
       
        self.btree = BTree()
        self.create_widgets()

    def create_widgets(self):
        # Menu
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load CSV", command=self.load_csv)
        file_menu.add_command(label="Export CSV", command=self.export_to_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

        # Main frames
        input_frame = ttk.LabelFrame(self.root, text="Add Book", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
       
        action_frame = ttk.LabelFrame(self.root, text="Book Actions", padding=10)
        action_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
       
        list_frame = ttk.LabelFrame(self.root, text="Book List", padding=10)
        list_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
       
        # Input form
        ttk.Label(input_frame, text="book_ID:").grid(row=0, column=0, sticky="e")
        self.id_entry = ttk.Entry(input_frame)
        self.id_entry.grid(row=0, column=1, pady=2, sticky="ew")
       
        ttk.Label(input_frame, text="Title:").grid(row=1, column=0, sticky="e")
        self.title_entry = ttk.Entry(input_frame)
        self.title_entry.grid(row=1, column=1, pady=2, sticky="ew")
       
        ttk.Label(input_frame, text="Author:").grid(row=2, column=0, sticky="e")
        self.author_entry = ttk.Entry(input_frame)
        self.author_entry.grid(row=2, column=1, pady=2, sticky="ew")
       
        ttk.Label(input_frame, text="Genre:").grid(row=3, column=0, sticky="e")
        self.genre_combo = ttk.Combobox(input_frame, values=[g.value for g in Genre])
        self.genre_combo.grid(row=3, column=1, pady=2, sticky="ew")
       
        ttk.Label(input_frame, text="Year:").grid(row=4, column=0, sticky="e")
        self.year_entry = ttk.Entry(input_frame)
        self.year_entry.grid(row=4, column=1, pady=2, sticky="ew")
       
        ttk.Label(input_frame, text="Available:").grid(row=5, column=0, sticky="e")
        self.available_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(input_frame, variable=self.available_var).grid(row=5, column=1, sticky="w")
       
        ttk.Button(input_frame, text="Add Book", command=self.add_book).grid(row=6, column=0, columnspan=2, pady=5)
       
        # Action form (Borrow/Return/Delete)
        ttk.Label(action_frame, text="Book ID:").grid(row=0, column=0, sticky="e")
        self.action_id_entry = ttk.Entry(action_frame)
        self.action_id_entry.grid(row=0, column=1, pady=2, sticky="ew")
       
        ttk.Button(action_frame, text="Borrow Book", command=self.borrow_book).grid(row=1, column=0, pady=5, sticky="ew")
        ttk.Button(action_frame, text="Return Book", command=self.return_book).grid(row=1, column=1, pady=5, sticky="ew")
        ttk.Button(action_frame, text="Delete Book", command=self.delete_book).grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
       
        # Search form
        ttk.Label(action_frame, text="Search by:").grid(row=3, column=0, sticky="e")
        self.search_by = ttk.Combobox(action_frame, values=["Title", "Author", "Genre", "book_ID"])
        self.search_by.grid(row=4, column=0, padx=2, sticky="ew")
        self.search_by.current(0)
       
        self.search_entry = ttk.Entry(action_frame)
        self.search_entry.grid(row=4, column=1, padx=2, sticky="ew")
       
        ttk.Button(action_frame, text="Search", command=self.search_books).grid(row=5, column=0, columnspan=2, pady=5)
       
        # Book list
        self.tree = ttk.Treeview(list_frame, columns=("ID", "Title", "Author", "Genre", "Year", "Available"),
                                show="headings", selectmode="browse")
       
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Author", text="Author")
        self.tree.heading("Genre", text="Genre")
        self.tree.heading("Year", text="Year")
        self.tree.heading("Available", text="Available")
       
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Title", width=200)
        self.tree.column("Author", width=150)
        self.tree.column("Genre", width=100)
        self.tree.column("Year", width=80, anchor="center")
        self.tree.column("Available", width=80, anchor="center")
       
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
       
        # Configure grid weights
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        try:
            with open(file_path, 'rb') as file:
                result = chardet.detect(file.read())
                encoding = result['encoding']
                print(f"Detected encoding: {encoding}")

            with open(file_path, mode="r", encoding=encoding) as file:
                reader = csv.DictReader(file)

                # Clear existing data
                self.btree = BTree()

                for row in reader:
                    print(f"Row book_ID: {row.get('book_ID')}")
                    try:
                        book_id = int(row.get('book_ID', 0))
                    except ValueError:
                        book_id = 0  # Default value if parsing fails
                    book = Book(
                        book_ID=book_id,
                        title=row.get('title', 'Unknown'),
                        author=row.get('author', 'Unknown'),
                        genre=Genre(row.get('genre', 'FICTION')),
                        publication_year=int(row.get('publication_year', 1900)),
                        available=row.get('available', 'True').lower() == 'true'
                    )
                    self.btree.insert(book)

            self.update_display()
            messagebox.showinfo("Success", f"Loaded {len(self.btree.traverse())} books from CSV")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV:\n{str(e)}")

    def export_to_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="library_export.csv"
        )
        if not file_path:
            return
           
        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["book_ID", "title", "author", "genre", "publication_year", "available"])
               
                for book in self.btree.traverse():
                    writer.writerow([
                        book.book_ID,
                        book.title,
                        book.author,
                        book.genre.value,
                        book.publication_year,
                        book.available
                    ])
                   
            messagebox.showinfo("Success", f"Exported {len(self.btree.traverse())} books to CSV")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV:\n{str(e)}")

    def add_book(self):
        try:
            book = Book(
                book_ID=int(self.id_entry.get()),
                title=self.title_entry.get(),
                author=self.author_entry.get(),
                genre=Genre(self.genre_combo.get()),
                publication_year=int(self.year_entry.get()),
                available=self.available_var.get()
            )
            self.btree.insert(book)
            self.update_display()
            self.clear_form()
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input:\n{str(e)}")

    def search_books(self):
        search_term = self.search_entry.get().strip().lower()
        search_by = self.search_by.get().lower()
       
        if not search_term:
            self.update_display()
            messagebox.showinfo("Info", "Please enter search term")
            return
           
        results = []
        for book in self.btree.traverse():
            if search_by == "title" and search_term in book.title.lower():
                results.append(book)
            elif search_by == "author" and search_term in book.author.lower():
                results.append(book)
            elif search_by == "genre" and search_term in book.genre.value.lower():
                results.append(book)
            elif search_by == "book_id":
                try:
                    if str(book.book_ID).startswith(search_term):
                        results.append(book)
                except ValueError:
                    pass
               
        self.update_display(results)
       
        if not results:
            messagebox.showinfo("Search", "No matching books found")

    def borrow_book(self):
        """Borrow a book (set availability to False)"""
        try:
            book_id = int(self.action_id_entry.get())
            if self.btree.update_availability(book_id, False):
                self.update_display()
                messagebox.showinfo("Success", f"Book ID {book_id} has been borrowed")
            else:
                messagebox.showerror("Error", f"Book ID {book_id} not found")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid book ID")

    def return_book(self):
        """Return a book (set availability to True)"""
        try:
            book_id = int(self.action_id_entry.get())
            if self.btree.update_availability(book_id, True):
                self.update_display()
                messagebox.showinfo("Success", f"Book ID {book_id} has been returned")
            else:
                messagebox.showerror("Error", f"Book ID {book_id} not found")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid book ID")
           
    def delete_book(self):
        """Delete a book from the library"""
        try:
            book_id = int(self.action_id_entry.get())
           
            # Check if book exists
            book_exists = False
            for book in self.btree.traverse():
                if book.book_ID == book_id:
                    book_exists = True
                    break
           
            if not book_exists:
                messagebox.showerror("Error", f"Book ID {book_id} not found")
                return
           
            # Confirm deletion
            confirm = messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete book ID {book_id}? This action cannot be undone."
            )
           
            if confirm:
                if self.btree.delete_book(book_id):
                    self.update_display()
                    messagebox.showinfo("Success", f"Book ID {book_id} has been deleted")
                else:
                    messagebox.showerror("Error", f"Failed to delete book ID {book_id}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid book ID")

    def update_display(self, books=None):
        self.tree.delete(*self.tree.get_children())
        display_books = books if books is not None else self.btree.traverse()
       
        for book in display_books:
            self.tree.insert("", "end", values=(
                book.book_ID,
                book.title,
                book.author,
                book.genre.value,
                book.publication_year,
                "Yes" if book.available else "No"
            ))

    def clear_form(self):
        self.id_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_combo.set("")
        self.year_entry.delete(0, tk.END)
        self.available_var.set(True)
