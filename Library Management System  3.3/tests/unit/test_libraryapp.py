import unittest
import os
import tempfile
import shutil
import tkinter as tk
from unittest.mock import patch, MagicMock, call
from models.Book import Book
from models.Genre import Genre
from models.User import User

class TestLibraryApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the Tk root window once for all tests"""
        cls.root = tk.Tk()
        cls.root.withdraw()

    @classmethod
    def tearDownClass(cls):
        """Clean up the Tk root window after all tests"""
        cls.root.destroy()
        del cls.root

    def setUp(self):
        """Set up test environment before each test"""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create mock objects
        self.mock_btree = MagicMock()
        self.mock_rec_service = MagicMock()
        self.mock_messagebox = MagicMock()
        self.mock_filedialog = MagicMock()
        
        # Create mock widgets
        self.mock_tree = MagicMock()
        self.mock_error_label = MagicMock()
        self.mock_recommend_list = MagicMock()
        self.mock_entry = MagicMock()
        self.mock_combobox = MagicMock()
        
        # Set up patchers
        self.patchers = [
            patch('gui.libraryapp.BTree', return_value=self.mock_btree),
            patch('gui.libraryapp.RecommendationService', return_value=self.mock_rec_service),
            patch('gui.libraryapp.messagebox', self.mock_messagebox),
            patch('gui.libraryapp.filedialog', self.mock_filedialog),
        ]
        
        # Start all patchers
        for patcher in self.patchers:
            patcher.start()
        
        from gui.libraryapp import LibraryApp
        self.app = LibraryApp()
        self.app.withdraw()
        
        # Set up mock widgets
        self.app.tree = self.mock_tree
        self.app.error_label = self.mock_error_label
        self.app.recommend_list = self.mock_recommend_list
        self.app.user_entry = self.mock_entry
        
        # Configure mock behaviors
        self.mock_error_label.winfo_ismapped.return_value = True
        self.mock_error_label.cget.return_value = ""
        self.mock_error_label.grid = MagicMock()
        self.mock_error_label.grid_remove = MagicMock()
        self.mock_error_label.config = MagicMock()
        
        # Mock form widgets
        self.app.id_entry = self.mock_entry
        self.app.title_entry = self.mock_entry
        self.app.author_entry = self.mock_entry
        self.app.year_entry = self.mock_entry
        self.app.genre_combo = self.mock_combobox
        self.app.available_var = MagicMock(value=True)
        self.app.action_id_entry = self.mock_entry
        self.app.search_by = self.mock_combobox
        self.app.search_entry = self.mock_entry
        self.app.match_type = self.mock_combobox

        # Configure default mock behaviors
        self.mock_entry.get.return_value = ""
        self.mock_combobox.get.return_value = ""
        self.mock_recommend_list.size.return_value = 0
        self.mock_tree.get_children.return_value = []

    def tearDown(self):
        """Clean up after each test"""
        for patcher in self.patchers:
            patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.app.destroy()

    def test_initialization(self):
        """Test that the application initializes correctly"""
        self.assertEqual(self.app.title(), "Library Management System")
        self.assertEqual(self.app.btree, self.mock_btree)
        self.assertEqual(self.app.rec_service, self.mock_rec_service)
        self.assertIsNone(self.app.current_user)
        
    def test_setup_infrastructure(self):
        """Test infrastructure setup"""
        self.assertEqual(self.app.btree, self.mock_btree)
        self.assertEqual(self.app.rec_service, self.mock_rec_service)
        self.assertEqual(self.app.id_index, {})

    def test_login_success(self):
        """Test successful user login"""
        test_user = User("test123")
        self.mock_rec_service.get_or_create_user.return_value = test_user
        
        self.mock_entry.get.return_value = "test123"
        self.app._handle_login()
        
        self.mock_rec_service.get_or_create_user.assert_called_once_with("test123")
        self.assertEqual(self.app.current_user, test_user)
        
    def test_login_failure(self):
        """Test failed login scenario"""
        self.mock_rec_service.get_or_create_user.side_effect = Exception("Login failed")
        
        self.mock_entry.get.return_value = "invalid"
        self.app._handle_login()
        
        self.assertIsNone(self.app.current_user)

    def test_add_book_success(self):
        """Test successful addition of a new book"""
        test_book = MagicMock(spec=Book)
        test_book.book_ID = 123
        test_book.title = "Test Book"
        test_book.author = "Test Author"
        test_book.genre = Genre.FICTION
        test_book.publication_year = 2023
        test_book.available = True
        
        # Mock form inputs
        self.mock_entry.get.side_effect = ["123", "Test Book", "Test Author", "2023"]
        self.mock_combobox.get.return_value = Genre.FICTION.value
        
        with patch.object(self.app, '_add_book_to_system'):
            self.app.add_book()
            self.app._add_book_to_system.assert_called_once()

    def test_borrow_book(self):
        """Test book borrowing functionality"""
        self.app.current_user = User("test123")
        
        test_book = MagicMock()
        test_book.available = True
        self.app.id_index = {123: test_book}
        
        self.mock_entry.get.return_value = "123"
        self.app.borrow_book()
        
        self.assertFalse(test_book.available)
        self.mock_rec_service.record_borrow.assert_called_once_with("test123", 123)

    def test_return_book(self):
        """Test book return functionality"""
        self.app.current_user = User("test123")
        
        test_book = MagicMock()
        test_book.available = False
        self.app.id_index = {123: test_book}
        
        self.mock_entry.get.return_value = "123"
        self.app.return_book()
        
        self.assertTrue(test_book.available)
        self.mock_rec_service.record_return.assert_called_once_with("test123", 123)

    def test_search_books(self):
        """Test book search functionality"""
        test_books = [
            MagicMock(book_ID=1, title="Python Programming", author="John Doe", 
                     genre=Genre.FICTION, available=True),
            MagicMock(book_ID=2, title="Advanced Python", author="Jane Smith", 
                     genre=Genre.SCIENCE, available=False)
        ]
        self.mock_btree.traverse.return_value = test_books
        
        # Mock search inputs
        self.mock_combobox.get.side_effect = ["Title", "Exact"]
        self.mock_entry.get.return_value = "Python"
        
        self.app.search_books()
        self.mock_tree.insert.assert_called()

    def test_csv_import_export(self):
        """Test CSV import and export functionality"""
        # Create temporary CSV file
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'w', newline='') as f:
            f.write("book_ID,title,author,genre,publication_year,available\n")
            f.write("1,Test Book,Test Author,FICTION,2023,True\n")
        
        # Configure mock file dialogs
        self.mock_filedialog.askopenfilename.return_value = csv_path
        self.mock_filedialog.asksaveasfilename.return_value = os.path.join(self.temp_dir, "export.csv")
        
        # Test import with mock book creation
        with patch.object(self.app, '_create_book_from_csv', return_value=MagicMock()):
            self.app.load_csv()
            self.app._create_book_from_csv.assert_called_once()
        
        # Test export
        self.app.export_to_csv()
        self.mock_filedialog.asksaveasfilename.assert_called_once()

    def test_recommendations(self):
        """Test book recommendation functionality"""
        self.app.current_user = User("test123")
        
        test_books = [
            MagicMock(title="Book 1", author="Author 1", genre=Genre.FICTION),
            MagicMock(title="Book 2", author="Author 2", genre=Genre.SCIENCE)
        ]
        self.mock_rec_service.recommend_books.return_value = test_books
        
        # Configure mock recommend_list
        self.mock_recommend_list.delete = MagicMock()
        self.mock_recommend_list.insert = MagicMock()
        
        self.app._update_recommendations()
        
        # Verify recommendations were updated
        self.mock_rec_service.recommend_books.assert_called_with("test123")
        self.assertEqual(self.mock_recommend_list.insert.call_count, 2)

    def test_show_user_stats_with_login(self):
        """Test showing user stats when logged in"""
        test_user = User("test123")
        test_user.borrow_history = [1, 2, 3]
        test_user.preferences = {Genre.FICTION: 5, Genre.SCIENCE: 3}
        self.app.current_user = test_user
        
        self.app.show_user_stats()
        self.mock_messagebox.showinfo.assert_called_once()

    def test_delete_book_success(self):
        """Test successful book deletion"""
        test_book = MagicMock()
        test_book.book_ID = 123
        test_book.title = "Test Book"
        self.app.id_index = {123: test_book}
        
        # Mock user confirmation
        self.mock_messagebox.askyesno.return_value = True
        self.mock_entry.get.return_value = "123"
        
        self.app.delete_book()
        
        self.mock_btree.delete.assert_called_once()
        self.mock_rec_service.remove_book.assert_called_once_with(123)
        self.mock_messagebox.showinfo.assert_called_once()

    def test_delete_book_cancel(self):
        """Test canceled book deletion"""
        test_book = MagicMock()
        test_book.book_ID = 123
        self.app.id_index = {123: test_book}
        
        # Mock user cancellation
        self.mock_messagebox.askyesno.return_value = False
        self.mock_entry.get.return_value = "123"
        
        self.app.delete_book()
        
        self.mock_btree.delete.assert_not_called()
        self.mock_rec_service.remove_book.assert_not_called()

    def test_clear_form(self):
        """Test form clearing functionality"""
        self.app.clear_form()
        self.mock_entry.delete.assert_called_with(0, tk.END)
        self.mock_combobox.set.assert_called_with(Genre.FICTION.value)
        self.app.available_var.set.assert_called_with(True)

    def test_error_handling(self):
        """Test error message display and hiding"""
        self.app._show_error("Test error")
        self.mock_error_label.config.assert_called_with(text="Test error")
        self.mock_error_label.grid.assert_called_once()
        
        self.app._hide_error()
        self.mock_error_label.grid_remove.assert_called_once()

    def test_highlight_error(self):
        """Test error field highlighting"""
        mock_widget = MagicMock()
        self.app._highlight_error(mock_widget)
        mock_widget.config.assert_called_with(highlightbackground='red', highlightthickness=2)

    def test_csv_import_encoding_detection(self):
        """Test CSV import with encoding detection"""
        # Create test CSV with non-UTF-8 encoding
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'wb') as f:
            f.write("book_ID,title,author,genre,publication_year,available\n".encode('utf-16'))
            f.write("1,Test Book,Test Author,FICTION,2023,True\n".encode('utf-16'))
        
        self.mock_filedialog.askopenfilename.return_value = csv_path
        
        # Mock chardet and book creation
        with patch('chardet.detect', return_value={'encoding': 'utf-16'}), \
             patch.object(self.app, '_create_book_from_csv', return_value=MagicMock()):
            self.app.load_csv()
            self.app._create_book_from_csv.assert_called_once()

    def test_csv_import_invalid_row(self):
        """Test CSV import with invalid rows"""
        csv_path = os.path.join(self.temp_dir, "test.csv")
        with open(csv_path, 'w', newline='') as f:
            f.write("book_ID,title,author,genre,publication_year,available\n")
            f.write("invalid,,,,,\n")  # Invalid row
            f.write("1,Valid Book,Test Author,FICTION,2023,True\n")  # Valid row
        
        self.mock_filedialog.askopenfilename.return_value = csv_path
        
        # Mock book creation for valid row
        with patch.object(self.app, '_create_book_from_csv', side_effect=[None, MagicMock()]):
            self.app.load_csv()
            self.assertEqual(self.app._create_book_from_csv.call_count, 2)

    def test_search_books_empty_results(self):
        """Test book search with no results"""
        self.mock_combobox.get.return_value = "Title"
        self.mock_entry.get.return_value = "Nonexistent"
        self.mock_btree.traverse.return_value = []
        
        self.app.search_books()
        self.mock_tree.insert.assert_not_called()

    def test_search_books_invalid_criteria(self):
        """Test book search with invalid search criteria"""
        self.mock_combobox.get.return_value = "Invalid"
        self.mock_entry.get.return_value = "test"
        
        self.app.search_books()
        # Should not raise exceptions
        self.assertTrue(True)

    def test_book_creation_from_csv(self):
        """Test creating Book objects from CSV data"""
        test_row = {
            'book_ID': '123',
            'title': 'Test Book',
            'author': 'Test Author',
            'genre': 'FICTION',
            'publication_year': '2023',
            'available': 'True'
        }
        
        book = self.app._create_book_from_csv(test_row)
        self.assertEqual(book.book_ID, 123)
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.genre, Genre.FICTION)

    def test_book_creation_from_csv_missing_fields(self):
        """Test creating Book objects with missing fields"""
        test_row = {
            'book_ID': '123',
            'title': '',  # Missing title
            'author': 'Test Author',
            'genre': 'FICTION',
            'publication_year': '2023'
        }
        
        with self.assertRaises(ValueError):
            self.app._create_book_from_csv(test_row)

    def test_collect_book_inputs_validation(self):
        """Test book input collection and validation"""
        # Mock form inputs
        self.mock_entry.get.side_effect = ["invalid", "", "Test Author", "2023"]
        self.mock_combobox.get.return_value = "FICTION"
        
        with patch.object(self.app, '_highlight_error'):
            result = self.app._collect_book_inputs()
            self.assertIsNone(result)
            self.app._highlight_error.assert_called()

if __name__ == '__main__':
    unittest.main()
