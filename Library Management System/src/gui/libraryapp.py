#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Library Management System with B-tree Backend
Version: 3.0 (Integrated B-tree)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import chardet
from datetime import datetime
from models.Book import Book
from models.Genre import Genre
from models.btree import BTree

class LibraryApp:
    """Main application class with B-tree and secondary index integration"""
    
    def __init__(self, root):
        """Initialize the application with B-tree and secondary index"""
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("1000x800")
        
        # Initialize B-tree organized by book titles
        self.btree = BTree(t=3)
        
        # Secondary index dictionary for fast ID lookups
        self.id_index = {}
        
        self._init_ui()
        self._setup_error_handler()
        self._setup_layout()

    def _init_ui(self):
        """Initialize all UI components"""
        # Menu Bar
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load CSV", command=self.load_csv)
        file_menu.add_command(label="Export CSV", command=self.export_to_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)

        # Input Frame
        input_frame = ttk.LabelFrame(self.root, text="Add New Book", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self._create_input_form(input_frame)

        # Action Frame
        action_frame = ttk.LabelFrame(self.root, text="Book Operations", padding=10)
        action_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self._create_action_controls(action_frame)

        # Book List Display
        list_frame = ttk.LabelFrame(self.root, text="Book Inventory", padding=10)
        list_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self._create_book_list(list_frame)

    def _setup_error_handler(self):
        """Initialize error display system"""
        self.error_label = ttk.Label(self.root, foreground="red")
        self.error_label.grid(row=2, column=0, columnspan=2, sticky="ew")

    def _setup_layout(self):
        """Configure grid layout weights"""
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def _create_input_form(self, parent):
        """Create book input form components"""
        fields = [
            ("Book ID:", "id_entry"),
            ("Title:", "title_entry"), 
            ("Author:", "author_entry"),
            ("Publication Year:", "year_entry"),
            ("Genre:", "genre_combo")
        ]
        
        for i, (label_text, var_name) in enumerate(fields):
            ttk.Label(parent, text=label_text).grid(row=i, column=0, sticky="e", padx=5)
            if "combo" in var_name:
                entry = ttk.Combobox(parent, values=[g.value for g in Genre])
                entry.current(0)
            else:
                entry = ttk.Entry(parent)
            entry.grid(row=i, column=1, pady=2, sticky="ew", padx=5)
            setattr(self, var_name, entry)
        
        # Availability checkbox
        ttk.Label(parent, text="Available:").grid(row=5, column=0, sticky="e", padx=5)
        self.available_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, variable=self.available_var).grid(row=5, column=1, sticky="w", padx=5)
        
        # Add Book button
        ttk.Button(parent, text="Add Book", command=self.add_book).grid(
            row=6, column=0, columnspan=2, pady=10)

    def _create_action_controls(self, parent):
        """Create action buttons and search controls"""
        # Book ID input
        ttk.Label(parent, text="Book ID:").grid(row=0, column=0, sticky="e", padx=5)
        self.action_id_entry = ttk.Entry(parent)
        self.action_id_entry.grid(row=0, column=1, pady=2, sticky="ew", padx=5)
        
        # Action buttons
        actions = [
            ("Borrow Book", self.borrow_book),
            ("Return Book", self.return_book),
            ("Delete Book", self.delete_book)
        ]
        for i, (text, command) in enumerate(actions, start=1):
            ttk.Button(parent, text=text, command=command).grid(
                row=i, column=0, columnspan=2, pady=5, sticky="ew")
        
        # Search controls
        ttk.Label(parent, text="Search by:").grid(row=4, column=0, sticky="e", padx=5)
        self.search_by = ttk.Combobox(parent, values=["Title", "Author", "Genre", "ID"])
        self.search_by.grid(row=5, column=0, padx=5, sticky="ew")
        self.search_by.current(0)
        
        self.search_entry = ttk.Entry(parent)
        self.search_entry.grid(row=5, column=1, padx=5, sticky="ew")
        
        ttk.Label(parent, text="Match type:").grid(row=6, column=0, sticky="e", padx=5)
        self.match_type = ttk.Combobox(parent, values=["exact", "startswith", "contains"])
        self.match_type.grid(row=6, column=1, padx=5, sticky="ew")
        self.match_type.current(0)
        
        ttk.Button(parent, text="Search", command=self.search_books).grid(
            row=7, column=0, columnspan=2, pady=10)

    def _create_book_list(self, parent):
        """Create the book list treeview"""
        columns = {
            "ID": {"width": 50, "anchor": "center"},
            "Title": {"width": 200},
            "Author": {"width": 150},
            "Genre": {"width": 100},
            "Year": {"width": 80, "anchor": "center"},
            "Available": {"width": 80, "anchor": "center"}
        }
        
        self.tree = ttk.Treeview(parent, columns=list(columns.keys()), 
                               show="headings", selectmode="browse")
        
        for col, config in columns.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, **config)
        
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)

    def add_book(self):
        """Add new book with comprehensive validation using B-tree"""
        try:
            # 1. Collect all inputs
            field_map = {
                "Book ID": (self.id_entry, "int"),
                "Title": (self.title_entry, "str"),
                "Author": (self.author_entry, "str"), 
                "Publication Year": (self.year_entry, "int"),
                "Genre": (self.genre_combo, "str")
            }
            
            inputs = {}
            empty_fields = []
            
            # 2. Check for empty fields
            for field, (widget, dtype) in field_map.items():
                value = widget.get().strip()
                if not value:
                    empty_fields.append(field)
                inputs[field] = value
            
            if empty_fields:
                self._show_error(
                    f"Required fields missing: {', '.join(empty_fields)}",
                    self._get_field_widget(empty_fields[0])
                )
                return
                
            # 3. Validate data types
            try:
                book_id = int(inputs["Book ID"])
                year = int(inputs["Publication Year"])
            except ValueError:
                self._show_error("ID and Year must be valid numbers")
                return
                
            # 4. Validate business rules
            current_year = datetime.now().year
            if year > current_year + 1:  # Allow 1 year buffer
                if not messagebox.askyesno(
                    "Confirm Year",
                    f"The year {year} is after current year ({current_year}).\n"
                    "Are you sure this is correct?"
                ):
                    return
            
            # 5. Check for duplicates using both indexes
            title = inputs["Title"]
            if self.btree.search(title):
                self._show_error(f"A book with title '{title}' already exists!", self.title_entry)
                return
                
            if book_id in self.id_index:
                self._show_error(f"Book ID {book_id} already exists!", self.id_entry)
                return
            
            # 6. All validations passed - create and insert book
            book = Book(
                book_ID=book_id,
                title=title,
                author=inputs["Author"],
                genre=Genre(inputs["Genre"]),
                publication_year=year,
                available=self.available_var.get()
            )
            
            # Add to both structures
            self.btree.insert(book)
            self.id_index[book_id] = book
            self.update_display()
            self.clear_form()
            self._show_success_message(book)
            
        except Exception as e:
            self._show_error(f"Error adding book: {str(e)}")

    def _get_field_widget(self, field_name):
        """Helper to get widget by field name"""
        return {
            "Book ID": self.id_entry,
            "Title": self.title_entry,
            "Author": self.author_entry,
            "Publication Year": self.year_entry,
            "Genre": self.genre_combo
        }.get(field_name)

    def _show_error(self, message, widget=None):
        """Show error message with optional focus control"""
        self.error_label.config(text=message)
        if widget:
            widget.focus_set()
            widget.config(highlightbackground='red', highlightcolor='red')
            self.root.after(5000, lambda: widget.config(
                highlightbackground='SystemWindowFrame',
                highlightcolor='SystemWindowFrame'
            ))
        self.root.after(5000, lambda: self.error_label.config(text=""))

    def _show_success_message(self, book):
        """Show book addition success message"""
        messagebox.showinfo(
            "Success",
            f"✅ Book added successfully!\n\n"
            f"🆔 ID: {book.book_ID}\n"
            f"📖 Title: {book.title}\n"
            f"✍️ Author: {book.author}\n"
            f"📅 Year: {book.publication_year}"
        )

    def load_csv(self):
        """Import books from CSV file into B-tree"""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        try:
            # Detect file encoding
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
                encoding = result['encoding'] or 'utf-8'
            
            # Read CSV content
            with open(file_path, 'r', encoding=encoding, errors='replace') as file:
                reader = csv.DictReader(file)
                self.btree = BTree(t=3)  # Reset B-tree
                self.id_index = {}       # Reset secondary index
                
                success_count = 0
                for row in reader:
                    try:
                        book = Book(
                            book_ID=int(row.get('book_ID', 0)),
                            title=row.get('title', '').strip(),
                            author=row.get('author', '').strip(),
                            genre=Genre(row.get('genre', 'FICTION')),
                            publication_year=int(row.get('publication_year', 0)),
                            available=str(row.get('available', 'true')).lower() == 'true'
                        )
                        self.btree.insert(book)
                        self.id_index[book.book_ID] = book
                        success_count += 1
                    except Exception as e:
                        print(f"Skipped invalid row: {e}")

            self.update_display()
            messagebox.showinfo("Import Complete", 
                              f"Successfully loaded {success_count} books")
        
        except Exception as e:
            self._show_error(f"CSV Import Error: {str(e)}")

    def export_to_csv(self):
        """Export books from B-tree to CSV file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="library_export.csv"
        )
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["book_ID", "title", "author", 
                               "genre", "publication_year", "available"])
                
                for book in self.btree.traverse():
                    writer.writerow([
                        book.book_ID,
                        book.title,
                        book.author,
                        book.genre.value,
                        book.publication_year,
                        book.available
                    ])
            
            messagebox.showinfo("Export Complete", 
                              f"Exported {len(list(self.btree.traverse()))} books")
        except Exception as e:
            self._show_error(f"Export Error: {str(e)}")

    def search_books(self):
        """Search books using B-tree operations"""
        search_by = self.search_by.get().lower()
        search_term = self.search_entry.get().strip()
        match_type = self.match_type.get()

        if not search_term:
            self.update_display()
            return

        results = []
        match_func = {
            "exact": lambda x, y: x.lower() == y.lower(),
            "startswith": lambda x, y: x.lower().startswith(y.lower()),
            "contains": lambda x, y: y.lower() in x.lower()
        }.get(match_type, lambda x, y: y.lower() in x.lower())

        # Special case for ID search (use secondary index)
        if search_by == "id":
            try:
                book_id = int(search_term)
                if book_id in self.id_index:
                    results.append(self.id_index[book_id])
            except ValueError:
                pass
        else:
            # Use B-tree traversal for other searches
            for book in self.btree.traverse():
                try:
                    field_value = {
                        "title": book.title,
                        "author": book.author,
                        "genre": book.genre.value
                    }.get(search_by, "")
                    
                    if field_value and match_func(field_value, search_term):
                        results.append(book)
                except Exception:
                    continue

        self.update_display(results or None)

    def borrow_book(self):
        """Mark book as borrowed using ID index"""
        try:
            book_id = int(self.action_id_entry.get())
            
            if book_id in self.id_index:
                book = self.id_index[book_id]
                if not book.available:
                    messagebox.showerror("Error", 
                                      f"Book ID {book_id} is already borrowed!")
                    return
                book.available = False
                self.update_display()
                messagebox.showinfo("Success", 
                                 f"Book ID {book_id} has been borrowed")
            else:
                self._show_error(f"Book ID {book_id} not found")
        except ValueError:
            self._show_error("Please enter a valid numeric Book ID")

    def return_book(self):
        """Mark book as returned using ID index"""
        try:
            book_id = int(self.action_id_entry.get())
            
            if book_id in self.id_index:
                book = self.id_index[book_id]
                if book.available:
                    messagebox.showerror("Error", 
                                      f"Book ID {book_id} is not currently borrowed!")
                    return
                book.available = True
                self.update_display()
                messagebox.showinfo("Success", 
                                  f"Book ID {book_id} has been returned")
            else:
                self._show_error(f"Book ID {book_id} not found")
        except ValueError:
            self._show_error("Please enter a valid numeric Book ID")

    def delete_book(self):
        """Remove book from both structures"""
        try:
            book_id = int(self.action_id_entry.get())
            
            if book_id not in self.id_index:
                self._show_error(f"Book ID {book_id} not found")
                return
                
            book = self.id_index[book_id]
            
            if messagebox.askyesno("Confirm Delete", 
                                 f"Delete '{book.title}' (ID: {book_id})? This cannot be undone."):
                # Remove from both structures
                self.btree.delete(book.title)
                del self.id_index[book_id]
                self.update_display()
                messagebox.showinfo("Success", 
                                  f"Book '{book.title}' has been deleted")
        except ValueError:
            self._show_error("Please enter a valid numeric Book ID")

    def update_display(self, books=None):
        """Refresh the book list display using B-tree traversal"""
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
        """Reset input fields"""
        for entry in [self.id_entry, self.title_entry, 
                     self.author_entry, self.year_entry]:
            entry.delete(0, tk.END)
        self.genre_combo.set(Genre.FICTION.value)
        self.available_var.set(True)