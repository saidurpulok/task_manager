"""
Task Manager Pro - Main Entry Point
An intermediate-level task management application with advanced features.
"""
import tkinter as tk
import logging
import sys

from views.main_window import TaskManagerApp
from config.settings import Settings

# Setup logging
logger = logging.getLogger("TaskManager")


def main():
    """Main entry point for the application."""
    try:
        # Create root window
        root = tk.Tk()
        
        # Create application
        app = TaskManagerApp(root)
        
        # Start main loop
        logger.info("Starting application main loop")
        root.mainloop()
        
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
