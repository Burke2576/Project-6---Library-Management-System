# tests/unit/test_user.py
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from models.User import User

class TestUser(unittest.TestCase):
    def setUp(self):
        """Initialize the testing environment"""
        self.default_user = User(user_id="001")
        self.custom_user = User(user_id="002", name="Reader", 
                              borrow_history=["b001", "b002"],
                              preferences={"Fantasy": 3, "Sci-Fi": 1})

    # Test Initialize
    def test_initialization(self):
        self.assertEqual(self.default_user.user_id, "001")
        self.assertEqual(self.default_user.name, "New User")
        self.assertEqual(self.default_user.borrow_history, [])
        self.assertEqual(self.default_user.preferences, {})

        self.assertEqual(self.custom_user.user_id, "002")
        self.assertEqual(self.custom_user.name, "Reader")
        self.assertEqual(self.custom_user.borrow_history, ["b001", "b002"])
        self.assertEqual(self.custom_user.preferences, {"Fantasy": 3, "Sci-Fi": 1})

    # Test the borrowing function
    def test_add_borrowed_book(self):
        self.default_user.add_borrowed_book("b003")
        self.assertIn("b003", self.default_user.borrow_history)
        self.assertEqual(len(self.default_user.borrow_history), 1)

        self.custom_user.add_borrowed_book("b003")
        self.assertEqual(self.custom_user.borrow_history, ["b001", "b002", "b003"])

    # Test preference update
    def test_update_preference(self):
        # new category
        self.default_user.update_preference("Mystery")
        self.assertEqual(self.default_user.preferences["Mystery"], 1)

        # Existing categories
        self.custom_user.update_preference("Fantasy")
        self.assertEqual(self.custom_user.preferences["Fantasy"], 4)

        # Case sensitivity test
        self.default_user.update_preference("mystery")
        self.assertEqual(self.default_user.preferences.get("Mystery"), 1)
        self.assertEqual(self.default_user.preferences.get("mystery"), 1)

    # Test string representation
    def test_string_representation(self):
        self.assertEqual(str(self.default_user), "User(001, New User)")
        self.assertEqual(str(self.custom_user), "User(002, Reader)")

    # Test edge conditions
    def test_edge_cases(self):
        
        empty_user = User(user_id="")
        self.assertEqual(empty_user.user_id, "")
        self.assertEqual(empty_user.name, "New User")

        special_user = User(user_id="003", name="用户@123")
        self.assertEqual(special_user.name, "用户@123")

        for _ in range(5):
            self.default_user.add_borrowed_book("repeat")
        self.assertEqual(self.default_user.borrow_history.count("repeat"), 5)

    def test_invalid_inputs(self):

        user_with_int_id = User(user_id=123)
        self.assertEqual(user_with_int_id.user_id, 123)  
    
        user_with_none_id = User(user_id=None)
        self.assertIsNone(user_with_none_id.user_id)
    
        self.default_user.add_borrowed_book(1001) 
        self.assertIn(1001, self.default_user.borrow_history)
    
        self.default_user.update_preference(42) 
        self.assertEqual(self.default_user.preferences.get(42), 1)

if __name__ == "__main__":
    unittest.main(verbosity=2)