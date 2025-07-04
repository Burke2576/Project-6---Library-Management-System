import unittest
from unittest.mock import Mock, patch
from models import Book, User, Genre
from collections import defaultdict
from models.Genre import Genre
from services.RecommendationService import RecommendationService
import threading

class TestRecommendationService(unittest.TestCase):
    def setUp(self):
        """Initialize test environment with mock BTree"""
        self.service = RecommendationService()
        
        # Mock the BTree to avoid dependency on actual implementation
        self.service.title_index = Mock()
        
        # Create test users
        self.user1 = User(user_id="u1", preferences={"FICTION": 3})
        self.user2 = User(user_id="u2")
        
        # Create test books
        self.book1 = Book(1, "FictionBook", "AuthorA", Genre.FICTION, 2020)
        self.book2 = Book(2, "SciFiBook", "AuthorB", Genre.SCIENCE, 2021)
        self.book3 = Book(3, "RomanceBook", "AuthorA", Genre.ROMANCE, 2022)
        
        # Add to service (without triggering BTree operations)
        self.service.user_data = {"u1": self.user1, "u2": self.user2}
        self.service.book_data = {
            1: self.book1,
            2: self.book2, 
            3: self.book3
        }
        self.service.genre_stats = defaultdict(int)
        self.service.genre_stats.update({
            "FICTION": 1,
            "SCIENCE": 1,
            "ROMANCE": 1
        })

    def test_add_book(self):
        """Test book addition"""
        self.assertIn(1, self.service.book_data)
        with self.assertRaises(ValueError):
            self.service.add_book("invalid_book_object")

    def test_add_user(self):
        """Test user addition"""
        self.assertIn("u1", self.service.user_data)
        with self.assertRaises(ValueError):
            self.service.add_user("invalid_user_object")

    def test_diversity_fallback(self):

        recommendations = self.service.recommend_books("u2")
        

        authors = {b.author for b in recommendations}
        genres = {b.genre.value for b in recommendations}
        self.assertTrue(len(authors) > 1)
        self.assertTrue(len(genres) > 1)

    def test_empty_recommendations(self):
        """Test when no books are available"""
        for book in self.service.book_data.values():
            book.available = False
        self.assertEqual(len(self.service.recommend_books("u1")), 0)

    def test_get_or_create_user(self):
        """Test user get-or-create functionality"""
        existing_user = self.service.get_or_create_user("u1")
        self.assertEqual(existing_user.user_id, "u1")
        
        new_user = self.service.get_or_create_user("new_user")
        self.assertEqual(new_user.user_id, "new_user")
        self.assertIn("new_user", self.service.user_data)

    def test_invalid_operations(self):
        """测试无效操作处理"""
        with self.assertRaises(ValueError):
            self.service.add_user("not_a_user_object")
        

        self.service.remove_book(999)
        self.service.record_return("u1", 999)

    def test_recommend_books_existing_user(self):
        """Test recommendations for user with preferences"""
        self.service.record_borrow("u1", 1)
        recommendations = self.service.recommend_books("u1")
        self.assertEqual(len(recommendations), 2)
        recommended_ids = {book.book_ID for book in recommendations}
        self.assertEqual(recommended_ids, {2, 3})

    def test_recommend_books_new_user(self):
        """Test recommendations for new user"""
        recommendations = self.service.recommend_books("u2")
        self.assertEqual(len(recommendations), 3)
        recommended_ids = {book.book_ID for book in recommendations}
        self.assertEqual(recommended_ids, {1, 2, 3})

    def test_recommendation_algorithm(self):
        """Test recommendation algorithm with mocked data"""
        # Properly mock the search method
        self.service.title_index.search = Mock()
        self.service.title_index.search.side_effect = lambda title: next(
            (b for b in [self.book1, self.book2, self.book3] if b.title == title), None)
        
        # User borrowed AuthorA's book
        self.service.record_borrow("u1", 1)
        
        recommendations = self.service.recommend_books("u1")
        self.assertGreaterEqual(len(recommendations), 2)
        
        # Verify recommendation contains expected books
        titles = [b.title for b in recommendations]
        self.assertIn("RomanceBook", titles)  # Same author
        self.assertIn("SciFiBook", titles)    # Different genre

    def test_recommendation_diversity(self):
        """Test recommendation diversity"""
        # Initialize all possible genre types
        for i in range(4):
            self.service.genre_stats[f"Type{i}"] = 1
        
        for i in range(5, 15):
            book = Mock(spec=Book)
            book.book_ID = i
            book.title = f"Book {i}"
            book.author = f"Author{i}"
            book.genre = Mock()
            book.genre.value = f"Type{i%4}"
            book.available = True
            self.service.book_data[i] = book
            self.service.genre_stats[book.genre.value] += 1
        
        recommendations = self.service.recommend_books("u1", top_n=5)
        authors = {book.author for book in recommendations}
        genres = {book.genre.value for book in recommendations}
        self.assertTrue(len(authors) >= 3)
        self.assertTrue(len(genres) >= 2)

    def test_remove_book(self):
        """Test book removal"""
        self.service.remove_book(1)
        self.assertNotIn(1, self.service.book_data)
        self.assertEqual(len(self.service.book_data), 2)

    def test_thread_safety(self):
        # Reset to initial state (3 points)
        self.user1.preferences = {"FICTION": 3}
        
        def borrow_books():
            for _ in range(100):
                self.service.record_borrow("u1", 1)
        
        from threading import Thread
        threads = [Thread(target=borrow_books) for _ in range(2)]
        for t in threads: t.start()
        for t in threads: t.join()
        
        self.assertEqual(self.user1.preferences["FICTION"], 403)

if __name__ == "__main__":
    unittest.main(verbosity=2)