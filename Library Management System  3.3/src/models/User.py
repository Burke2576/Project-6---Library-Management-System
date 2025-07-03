from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class User:
    """Library user with borrowing history and preferences"""
    user_id: str
    name: str = "New User"
    borrow_history: List[str] = field(default_factory=list)
    preferences: Dict[str, int] = field(default_factory=dict)  # {genre: preference_score}

    def add_borrowed_book(self, book_id: str) -> None:
        """Record a book borrowing"""
        self.borrow_history.append(book_id)

    def update_preference(self, genre: str) -> None:
        """Increment preference for a genre"""
        self.preferences[genre] = self.preferences.get(genre, 0) + 1

    def __str__(self):
        return f"User({self.user_id}, {self.name})"