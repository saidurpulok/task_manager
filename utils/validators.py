"""Validation utilities for task data."""
import re
from datetime import datetime
from typing import Optional, Tuple

from config.settings import Settings


class TaskValidator:
    """Validator for task attributes."""
    
    @staticmethod
    def validate_description(description: str) -> Tuple[bool, Optional[str]]:
        """
        Validate task description.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not description or not description.strip():
            return False, "Description cannot be empty"
        
        if len(description) > 500:
            return False, "Description cannot exceed 500 characters"
        
        return True, None
    
    @staticmethod
    def validate_priority(priority: str) -> Tuple[bool, Optional[str]]:
        """
        Validate task priority.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if priority not in Settings.PRIORITY_LEVELS:
            return False, f"Priority must be one of {Settings.PRIORITY_LEVELS}"
        
        return True, None
    
    @staticmethod
    def validate_date(date_string: str) -> Tuple[bool, Optional[str]]:
        """
        Validate date string.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not date_string:
            return True, None  # Empty date is valid
        
        try:
            datetime.strptime(date_string, Settings.DATE_FORMAT)
            return True, None
        except ValueError:
            return False, f"Date must be in format {Settings.DATE_FORMAT}"
    
    @staticmethod
    def validate_category(category: str) -> Tuple[bool, Optional[str]]:
        """
        Validate category name.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not category or not category.strip():
            return False, "Category cannot be empty"
        
        if len(category) > 50:
            return False, "Category name cannot exceed 50 characters"
        
        # Check for valid characters (alphanumeric, spaces, hyphens, underscores)
        if not re.match(r'^[\w\s\-]+$', category):
            return False, "Category can only contain letters, numbers, spaces, hyphens, and underscores"
        
        return True, None
