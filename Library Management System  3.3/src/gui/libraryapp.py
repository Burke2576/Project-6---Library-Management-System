import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict
from datetime import datetime
import csv
import chardet
import logging
from models.Book import Book
from models.Genre import Genre
from models.btree import BTree
from models.User import User
from services.RecommendationService import RecommendationService

class LibraryApp(tk.Tk):
    """Library Management System Main Window"""
    
    def __init__(self):
        super().__init__()
        self.title("Library Management System")
        self.geometry("1200x800")
        
        # Windows DPI scaling fix
        if tk.TkVersion < 8.6:
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass
        
        # Initialize infrastructure
        self._setup_infrastructure()
        
        # Initialize error label FIRST
        self.error_label = ttk.Label(
            self, 
            text="",
            foreground="red",
            font=('Arial', 10)
        )
        self.error_label.grid(row=999, column=0, columnspan=2, sticky="ew")
        self.error_label.grid_remove()
        
        # Create menu bar 
        self._create_menu_bar()
        
        # Initialize UI
        self._initialize_ui()
        self._show_login_screen()

    def _setup_infrastructure(self):
        """Initialize backend services"""
        self.btree = BTree(t=3)
        self.id_index = {}
        self.current_user = None
        self.rec_service = RecommendationService()
        
        # Configure logging
        logging.basicConfig(
            filename='library.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('LibraryApp')

    def _create_menu_bar(self):
        """Create the menu bar with File and User menus"""
        menubar = tk.Menu(self)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Load CSV", command=self.load_csv, accelerator="Ctrl+O")
        file_menu.add_command(label="Export CSV", command=self.export_to_csv, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit, accelerator="Alt+F4")
        
        # Bind keyboard shortcuts
        self.bind('<Control-o>', lambda e: self.load_csv())
        self.bind('<Control-s>', lambda e: self.export_to_csv())
        
        # User menu
        user_menu = tk.Menu(menubar, tearoff=0)
        user_menu.add_command(label="Switch User", command=self._show_login_screen)
        user_menu.add_command(label="My Statistics", command=self.show_user_stats)
        
        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="User", menu=user_menu)
        
        self.config(menu=menubar)
        
        # Special handling for macOS
        if self.tk.call('tk', 'windowingsystem') == 'aqua':
            self.createcommand('tk::mac::Quit', self.quit)

    def _initialize_ui(self):
        """Initialize the UI components"""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def _show_login_screen(self):
        """Show the login screen"""
        self._clear_frame()
        self.current_user = None
        
        frame = ttk.Frame(self)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(frame, text="User ID:").grid(row=0, column=0, padx=5, pady=5)
        self.user_entry = ttk.Entry(frame, width=20)
        self.user_entry.grid(row=0, column=1, padx=5, pady=5)
        
        login_btn = ttk.Button(frame, text="Login", command=self._handle_login)
        login_btn.grid(row=1, columnspan=2, pady=10)
        self.user_entry.bind('<Return>', lambda e: login_btn.invoke())

    def _handle_login(self):
        """Handle user login"""
        user_id = self.user_entry.get().strip()
        if not user_id:
            self._show_error("Please enter User ID")
            return
            
        try:
            self.current_user = self.rec_service.get_or_create_user(user_id)
            messagebox.showinfo("Welcome", f"Welcome back, {user_id}!")
            self._show_main_interface()
        except Exception as e:
            self._show_error(f"Login failed: {str(e)}")

    def _show_main_interface(self):
        """Show the main application interface"""
        self._clear_frame()
        
        # Recreate menu bar to ensure it persists
        self._create_menu_bar()
        
        # Input Panel
        input_frame = ttk.LabelFrame(self, text="Add New Book", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self._create_input_form(input_frame)

        # Operations Panel
        action_frame = ttk.LabelFrame(self, text="Book Operations", padding=10)
        action_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self._create_action_controls(action_frame)

        # Book List
        list_frame = ttk.LabelFrame(self, text="Book Inventory", padding=10)
        list_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self._create_book_list(list_frame)

        # Recommendations
        rec_frame = ttk.LabelFrame(self, text="Recommended For You", padding=10)
        rec_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.recommend_list = tk.Listbox(rec_frame, font=('Arial', 10))
        self.recommend_list.pack(fill=tk.BOTH, expand=True)
        
        self._refresh_display()

    def _create_input_form(self, parent):
        """Create the book input form"""
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
        
        ttk.Label(parent, text="Available:").grid(row=5, column=0, sticky="e", padx=5)
        self.available_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(parent, variable=self.available_var).grid(row=5, column=1, sticky="w", padx=5)
        
        ttk.Button(parent, text="Add Book", command=self.add_book).grid(row=6, column=0, columnspan=2, pady=10)

    def _create_action_controls(self, parent):
        """Create action buttons and search controls"""
        ttk.Label(parent, text="Book ID:").grid(row=0, column=0, sticky="e", padx=5)
        self.action_id_entry = ttk.Entry(parent)
        self.action_id_entry.grid(row=0, column=1, pady=2, sticky="ew", padx=5)
        
        actions = [
            ("Borrow Book", self.borrow_book),
            ("Return Book", self.return_book),
            ("Delete Book", self.delete_book)
        ]
        for i, (text, command) in enumerate(actions, start=1):
            ttk.Button(parent, text=text, command=command).grid(row=i, column=0, columnspan=2, pady=5, sticky="ew")
        
        # Search controls
        ttk.Label(parent, text="Search By:").grid(row=4, column=0, sticky="e", padx=5)
        self.search_by = ttk.Combobox(parent, values=["Title", "Author", "Genre", "ID"])
        self.search_by.grid(row=5, column=0, padx=5, sticky="ew")
        self.search_by.current(0)
        
        self.search_entry = ttk.Entry(parent)
        self.search_entry.grid(row=5, column=1, padx=5, sticky="ew")
        
        ttk.Label(parent, text="Match Type:").grid(row=6, column=0, sticky="e", padx=5)
        self.match_type = ttk.Combobox(parent, values=["Exact", "Starts with", "Contains"])
        self.match_type.grid(row=6, column=1, padx=5, sticky="ew")
        self.match_type.current(0)
        
        ttk.Button(parent, text="Search", command=self.search_books).grid(row=7, column=0, columnspan=2, pady=10)

    def _create_book_list(self, parent):
        """Create the book list treeview"""
        columns = {
            "ID": {"width": 60, "anchor": "center"},
            "Title": {"width": 250},
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

    def _refresh_display(self):
        """Refresh all displays"""
        self.tree.delete(*self.tree.get_children())
        for book in self.btree.traverse():
            self.tree.insert("", "end", values=(
                book.book_ID,
                book.title,
                book.author,
                book.genre.value,
                book.publication_year,
                "Yes" if book.available else "No"
            ))
        
        self._update_recommendations()
        self.error_label.config(text="")

    def _update_recommendations(self):
        """Update recommendation list"""
        self.recommend_list.delete(0, tk.END)
        if self.current_user:
            try:
                recommended = self.rec_service.recommend_books(self.current_user.user_id)
                for book in recommended:
                    self.recommend_list.insert(
                        tk.END,
                        f"{book.title} - {book.author} | Genre: {book.genre.value}"
                    )
            except Exception as e:
                self.logger.error(f"Recommendation failed: {str(e)}")
                self.recommend_list.insert(tk.END, "Unable to load recommendations")

    def add_book(self):
        """Add a new book"""
        try:
            book_data = self._collect_book_inputs()
            if not book_data:
                return
                
            new_book = Book(
                book_ID=book_data['id'],
                title=book_data['title'],
                author=book_data['author'],
                genre=Genre(book_data['genre']),
                publication_year=book_data['year'],
                available=book_data['available']
            )
            
            self._add_book_to_system(new_book)
            self._show_success_message(new_book)  
            self.clear_form()
            self._refresh_display()
            
        except ValueError as ve:
            self._show_error(f"Input error: {str(ve)}")
        except Exception as e:
            self._show_error(f"System error: {str(e)}")

    def _show_success_message(self, book):
        """Show success message"""
        messagebox.showinfo(
            "Success",
            f"✅ Book added successfully!\n\n"
            f"🆔 ID: {book.book_ID}\n"
            f"📖 Title: {book.title}\n"
            f"✍️ Author: {book.author}\n"
            f"📅 Year: {book.publication_year}\n"
            f"📚 Genre: {book.genre.value}"
        )

    def _collect_book_inputs(self) -> Optional[Dict]:
        """Collect and validate book inputs"""
        fields = {
            'id': (self.id_entry, 'Book ID', int),
            'title': (self.title_entry, 'Title', str),
            'author': (self.author_entry, 'Author', str),
            'year': (self.year_entry, 'Year', int),
            'genre': (self.genre_combo, 'Genre', str)
        }
        
        collected = {}
        errors = []
        
        for field, (widget, name, dtype) in fields.items():
            value = widget.get().strip()
            try:
                if not value:
                    errors.append(f"{name} cannot be empty")
                    continue
                    
                collected[field] = dtype(value) if dtype != str else value
                
            except ValueError:
                errors.append(f"Invalid {name} format")
                self._highlight_error(widget)
        
        if 'id' in collected and collected['id'] in self.id_index:
            errors.append("Book ID already exists")
            self._highlight_error(self.id_entry)
            
        if 'year' in collected:
            current_year = datetime.now().year
            if collected['year'] > current_year + 1:
                if not messagebox.askyesno("Confirm", 
                    f"Publication year {collected['year']} is in the future. Continue?"):
                    return None
        
        if errors:
            self._show_error("\n".join(errors))
            return None
            
        collected['available'] = self.available_var.get()
        return collected

    def _add_book_to_system(self, book: Book):
        """Add book to all index structures"""
        self.btree.insert(book)
        self.id_index[book.book_ID] = book
        self.rec_service.add_book(book)
        self.logger.info(f"Added book: {book.title} (ID: {book.book_ID})")

    def load_csv(self):
        """Load books from CSV file"""
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return

        try:
            # Reset data
            self.btree = BTree(t=3)
            self.id_index = {}
            self.rec_service.reset_books()
        
            with open(filepath, 'rb') as f:
                encoding = chardet.detect(f.read())['encoding'] or 'utf-8'
            
            with open(filepath, 'r', encoding=encoding, errors='replace') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        book = self._create_book_from_csv(row)
                        self.btree.insert(book)
                        self.id_index[book.book_ID] = book
                        self.rec_service.add_book(book)
                    except Exception as e:
                        print(f"[WARNING] Skipping invalid row: {str(e)}")
                    
            self._refresh_display()
            messagebox.showinfo("Import Complete", "CSV imported successfully")
        
        except Exception as e:
            print(f"[ERROR] Import failed: {str(e)}")
            self._show_error(f"CSV import error: {str(e)}")

    def _create_book_from_csv(self, row: dict) -> Book:
        """Create Book object from CSV row"""
        required_fields = ['book_ID', 'title', 'author', 'genre', 'publication_year']
        missing = [field for field in required_fields if field not in row or not row[field].strip()]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
    
        try:
            return Book(
                book_ID=int(row['book_ID']),
                title=row['title'].strip(),
                author=row['author'].strip(),
                genre=Genre(row['genre'].strip()),
                publication_year=int(row['publication_year']),
                available=str(row.get('available', 'true')).lower() == 'true'
            )
        except ValueError as e:
            raise ValueError(f"Data format error: {str(e)}")

    def export_to_csv(self):
        """Export books to CSV file"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="library_export.csv"
        )
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
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
                              f"Successfully exported {len(list(self.btree.traverse()))} books")
        except Exception as e:
            self._show_error(f"Export failed: {str(e)}")

    def search_books(self):
        """Search for books"""
        search_by = self.search_by.get().lower()
        search_term = self.search_entry.get().strip()
        match_type = self.match_type.get()

        if not search_term:
            self._refresh_display()
            return

        results = []
        match_func = {
            "exact": lambda x, y: x.lower() == y.lower(),
            "starts with": lambda x, y: x.lower().startswith(y.lower()),
            "contains": lambda x, y: y.lower() in x.lower()
        }.get(match_type.lower(), lambda x, y: y.lower() in x.lower())

        # ID search special case
        if search_by == "id":
            try:
                book_id = int(search_term)
                if book_id in self.id_index:
                    results.append(self.id_index[book_id])
            except ValueError:
                pass
        else:
            # Other search types
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

    def update_display(self, books=None):
        """Update book list display"""
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

    def borrow_book(self):
        """Borrow a book"""
        try:
            book_id = int(self.action_id_entry.get())
            
            if book_id not in self.id_index:
                self._show_error(f"Book ID {book_id} not found")
                return
            
            book = self.id_index[book_id]
            if not book.available:
                messagebox.showerror("Error", f"Book {book_id} is already borrowed!")
                return
        
            if self.current_user:
                self.rec_service.record_borrow(self.current_user.user_id, book_id)
        
            book.available = False
            self._refresh_display()
            messagebox.showinfo("Success", f"Successfully borrowed: {book.title}")
        except ValueError:
            self._show_error("Please enter a valid Book ID")

    def return_book(self):
        """Return a book"""
        try:
            book_id = int(self.action_id_entry.get())
            
            if book_id not in self.id_index:
                self._show_error(f"Book ID {book_id} not found")
                return
                
            book = self.id_index[book_id]
            if book.available:
                messagebox.showerror("Error", f"Book {book_id} is not borrowed!")
                return
            
            if self.current_user:
                self.rec_service.record_return(self.current_user.user_id, book_id)
            
            book.available = True
            self._refresh_display()
            messagebox.showinfo("Success", f"Successfully returned: {book.title}")
        except ValueError:
            self._show_error("Please enter a valid Book ID")

    def delete_book(self):
        """Delete a book"""
        try:
            book_id = int(self.action_id_entry.get())
            
            if book_id not in self.id_index:
                self._show_error(f"Book ID {book_id} not found")
                return
                
            book = self.id_index[book_id]
            
            if not messagebox.askyesno("Confirm Deletion", 
                                     f"Are you sure you want to delete '{book.title}' (ID: {book_id})? This cannot be undone!"):
                return
                
            self.btree.delete(book.title)
            del self.id_index[book_id]
            self.rec_service.remove_book(book_id)
            
            self._refresh_display()
            messagebox.showinfo("Success", f"Deleted book: {book.title}")
        except ValueError:
            self._show_error("Please enter a valid Book ID")

    def show_user_stats(self):
        """Show user statistics"""
        if not self.current_user:
            self._show_error("Please login first")
            return
            
        stats = [
            f"👤 User ID: {self.current_user.user_id}",
            f"📚 Total Borrowed: {len(self.current_user.borrow_history)}",
            f"❤️ Favorite Genre: {max(self.current_user.preferences.items(), key=lambda x: x[1])[0] if self.current_user.preferences else 'None'}"
        ]
        
        messagebox.showinfo("User Statistics", "\n".join(stats))

    def clear_form(self):
        """Clear the input form"""
        for entry in [self.id_entry, self.title_entry, 
                     self.author_entry, self.year_entry]:
            entry.delete(0, tk.END)
        self.genre_combo.set(Genre.FICTION.value)
        self.available_var.set(True)

    def _clear_frame(self):
        """Clear the frame but keep error label"""
        try:
            self._hide_error()
            
            for widget in self.winfo_children():
                if widget != self.error_label:  # Changed to use the instance variable
                    try:
                        widget.destroy()
                    except:
                        pass
        except Exception as e:
            print(f"Failed to clear frame: {str(e)}")

    def _highlight_error(self, widget):
        """Highlight an error field"""
        widget.config(highlightbackground='red', highlightthickness=2)
        self.after(3000, lambda: widget.config(
            highlightbackground='SystemWindowFrame',
            highlightthickness=1
        ))

    def _show_error(self, message, widget=None):
        """Show an error message"""
        try:
            self.error_label.config(text=message)
            self.error_label.grid()
            self.after(5000, self._hide_error)
            
            if widget:
                widget.focus_set()
        except Exception:
            messagebox.showerror("Error", message)

    def _hide_error(self):
        """Hide the error message"""
        try:
            self.error_label.grid_remove()
        except:
            pass

    def run(self):
        """Run the application"""
        self.mainloop()