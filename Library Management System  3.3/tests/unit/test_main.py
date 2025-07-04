import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import importlib


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

class TestMain(unittest.TestCase):
    @patch('tkinter.messagebox.showerror')  
    @patch('gui.libraryapp.LibraryApp')
    def test_main_success(self, mock_app, mock_error):
        """测试正常执行流程"""
       
        if 'main' in sys.modules:
            importlib.reload(sys.modules['main'])
        else:
            sys.modules['main'] = importlib.import_module('main')
        
        from main import main
        
        mock_instance = mock_app.return_value
        mock_instance._show_login_screen = MagicMock()
        
        main()
        
        mock_app.assert_called_once()
        mock_instance.mainloop.assert_called_once()
        mock_error.assert_not_called()

if __name__ == '__main__':
    unittest.main()