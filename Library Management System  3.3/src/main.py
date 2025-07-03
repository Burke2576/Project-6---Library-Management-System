#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Library Management System - Main Entry Point
"""

import sys
import os
from importlib import reload
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='library_debug.log'
)
logger = logging.getLogger(__name__)

def debug_environment():
    """Print environment debugging information"""
    logger.info("="*50)
    logger.info("Start environment debugging information:")
    logger.info(f"current working directory: {os.getcwd()}")
    logger.info(f"Python Path: {sys.path}")
    
    try:
        import services.RecommendationService
        reload(services.RecommendationService)
        from services.RecommendationService import RecommendationService
        logger.info("RecommendationService Loading successful")
        logger.info(f"reset_books exist: {hasattr(RecommendationService, 'reset_books')}")
    except Exception as e:
        logger.error(f"Module loading failed: {str(e)}")
    
    logger.info("="*50)

def main():
    """Application Entry Point"""
    
    debug_environment()
    
    try:
        from gui.libraryapp import LibraryApp
        logger.info("Successfully imported LibraryApp")
        
        app = LibraryApp()
        logger.info("LibraryApp Instance created successfully")
        
        # Ensure that the login interface is displayed
        if hasattr(app, '_show_login_screen'):
            app._show_login_screen()
            logger.info("The method to display the login interface has been called")
        else:
            logger.error("LibraryApp lack _show_login_screen method")
        
        app.mainloop()
    except Exception as e:
        logger.critical(f"Application startup failed: {str(e)}")
        messagebox.showerror("Error", f"Application startup failed:\n{str(e)}")

if __name__ == "__main__":
    main()

