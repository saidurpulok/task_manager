"""
Configuration settings for Task Manager application.
Supports environment variables and provides centralized configuration.
"""
import os
import logging
from pathlib import Path
from typing import Optional


class Settings:
    """Application settings with environment variable support."""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Database settings
    DB_NAME = os.getenv("TASK_MANAGER_DB", "tasks.db")
    DB_PATH = DATA_DIR / DB_NAME
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = LOGS_DIR / "task_manager.log"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # UI settings
    WINDOW_WIDTH = int(os.getenv("WINDOW_WIDTH", "1000"))
    WINDOW_HEIGHT = int(os.getenv("WINDOW_HEIGHT", "700"))
    THEME = os.getenv("THEME", "default")
    
    # Task settings
    DEFAULT_CATEGORY = "General"
    PRIORITY_LEVELS = ["Low", "Medium", "High", "Urgent"]
    PRIORITY_COLORS = {
        "Low": "#90EE90",      # Light green
        "Medium": "#FFD700",    # Gold
        "High": "#FFA500",      # Orange
        "Urgent": "#FF6B6B"     # Red
    }
    
    # Export settings
    EXPORT_DIR = DATA_DIR / "exports"
    BACKUP_DIR = DATA_DIR / "backups"
    
    # Date format
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    @classmethod
    def setup_directories(cls):
        """Create necessary directories if they don't exist."""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
        cls.EXPORT_DIR.mkdir(exist_ok=True)
        cls.BACKUP_DIR.mkdir(exist_ok=True)
    
    @classmethod
    def setup_logging(cls):
        """Configure application logging."""
        cls.setup_directories()
        
        # Create logger
        logger = logging.getLogger("TaskManager")
        logger.setLevel(getattr(logging, cls.LOG_LEVEL.upper()))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(cls.LOG_FORMAT, cls.LOG_DATE_FORMAT)
        console_handler.setFormatter(console_formatter)
        
        # File handler
        file_handler = logging.FileHandler(cls.LOG_FILE)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(cls.LOG_FORMAT, cls.LOG_DATE_FORMAT)
        file_handler.setFormatter(file_formatter)
        
        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger


# Initialize settings on import
Settings.setup_directories()
logger = Settings.setup_logging()
