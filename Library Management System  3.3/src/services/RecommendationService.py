from collections import defaultdict
from typing import Dict, List, Set
from models.Book import Book
from models.User import User
from models.btree import BTree
import random

class RecommendationService:
    def __init__(self):
        """Initialize recommendation service"""
        self.reset_books()
        self.user_data: Dict[str, User] = {}
    
    def reset_books(self):
        """Reset all book data"""
        self.book_data: Dict[int, Book] = {}
        self.title_index = BTree(t=3)
        self.genre_stats = defaultdict(int)
    
    def add_user(self, user: User):
        """Add users to the system"""
        if not isinstance(user, User):
            raise ValueError("Only User type objects can be added")
        self.user_data[user.user_id] = user
    
    def add_book(self, book: Book):
        """Add books to the system"""
        if not isinstance(book, Book):
            raise ValueError("Only Book type objects can be added")
        self.book_data[book.book_ID] = book
        self.title_index.insert(book)
        self.genre_stats[book.genre.value] += 1
    
    def remove_book(self, book_id: int):
        """Remove books from the system"""
        if book_id in self.book_data:
            book = self.book_data[book_id]
            self.title_index.delete(book.title)
            self.genre_stats[book.genre.value] -= 1
            del self.book_data[book_id]
    
    def record_borrow(self, user_id: str, book_id: int):
        """Record borrowing behavior and update user preferences"""
        if user_id in self.user_data and book_id in self.book_data:
            user = self.user_data[user_id]
            book = self.book_data[book_id]
            
            user.add_borrowed_book(book_id)
            book.available = False
            
            # Update type preference
            genre = book.genre.value
            user.preferences[genre] = user.preferences.get(genre, 0) + 2
    
    def record_return(self, user_id: str, book_id: int):
        """Record the act of returning books"""
        if user_id in self.user_data and book_id in self.book_data:
            self.book_data[book_id].available = True
    
    def recommend_books(self, user_id: str, top_n: int = 5) -> List[Book]:
        """Pure preference recommendation based on author and type"""
        if user_id not in self.user_data:
            return []
        
        user = self.user_data[user_id]
        borrowed_books = set(user.borrow_history)
        
        # Get recommended books
        available_books = [
            book for book in self.book_data.values()
            if book.book_ID not in borrowed_books and book.available
        ]
        
        if not available_books:
            return []
        
        # Calculate author preferences
        author_prefs = defaultdict(int)
        for book_id in user.borrow_history:
            if book_id in self.book_data:
                author_prefs[self.book_data[book_id].author] += 1
        
        # Recommendation when there is no historical record
        if not author_prefs:
            return self._recommend_by_genre_diversity(available_books, top_n)
        
        # Recommendations when there are historical records
        return self._recommend_by_preferences(user, available_books, author_prefs, top_n)
    
    def _recommend_by_genre_diversity(self, books: List[Book], top_n: int) -> List[Book]:
        """Recommended by Type Diversity"""
        genre_groups = defaultdict(list)
        for book in books:
            genre_groups[book.genre.value].append(book)
        
        recommended = []
        for genre in genre_groups:
            if len(recommended) >= top_n:
                break
            recommended.append(random.choice(genre_groups[genre]))
        
        return recommended
    
    def _recommend_by_preferences(
        self,
        user: User,
        books: List[Book],
        author_prefs: Dict[str, int],
        top_n: int
    ) -> List[Book]:
        """Preference based recommendation core algorithm"""
        def calculate_score(book: Book) -> float:
            """Rating function: Author 60%+Type 40%"""
            author_score = author_prefs.get(book.author, 0) * 0.6
            genre_score = user.preferences.get(book.genre.value, 0) * 0.4
            return author_score + genre_score
        
        # Sort by rating
        sorted_books = sorted(books, key=calculate_score, reverse=True)
        final_recommendations = []
        added_authors: Set[str] = set()
        added_genres: Set[str] = set()
        
        for book in sorted_books:
            if len(final_recommendations) >= top_n:
                break
            if book.author not in added_authors or book.genre.value not in added_genres:
                final_recommendations.append(book)
                added_authors.add(book.author)
                added_genres.add(book.genre.value)
        
        return final_recommendations
    
    def get_or_create_user(self, user_id: str) -> User:
        """Obtain or create users"""
        if user_id not in self.user_data:
            self.add_user(User(user_id=user_id))
        return self.user_data[user_id]

