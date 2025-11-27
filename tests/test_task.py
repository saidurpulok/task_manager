"""Unit tests for Task model."""
import unittest
from datetime import datetime

from models.task import Task


class TestTask(unittest.TestCase):
    """Test cases for Task model."""
    
    def test_task_creation(self):
        """Test basic task creation."""
        task = Task(
            description="Test task",
            priority="Medium",
            category="General"
        )
        
        self.assertEqual(task.description, "Test task")
        self.assertEqual(task.priority, "Medium")
        self.assertEqual(task.category, "General")
        self.assertFalse(task.completed)
    
    def test_task_validation(self):
        """Test task validation."""
        # Empty description should raise error
        with self.assertRaises(ValueError):
            Task(description="")
        
        # Invalid priority should raise error
        with self.assertRaises(ValueError):
            Task(description="Test", priority="Invalid")
    
    def test_task_to_dict(self):
        """Test task serialization to dict."""
        task = Task(
            id=1,
            description="Test task",
            priority="High",
            category="Work",
            due_date="2025-12-31"
        )
        
        data = task.to_dict()
        
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['description'], "Test task")
        self.assertEqual(data['priority'], "High")
        self.assertEqual(data['category'], "Work")
        self.assertEqual(data['due_date'], "2025-12-31")
    
    def test_task_from_dict(self):
        """Test task deserialization from dict."""
        data = {
            'id': 1,
            'description': "Test task",
            'priority': "Low",
            'category': "Personal",
            'due_date': None,
            'completed': False,
            'created_at': None,
            'updated_at': None,
            'completed_at': None
        }
        
        task = Task.from_dict(data)
        
        self.assertEqual(task.id, 1)
        self.assertEqual(task.description, "Test task")
        self.assertEqual(task.priority, "Low")
        self.assertEqual(task.category, "Personal")
    
    def test_task_is_overdue(self):
        """Test overdue task detection."""
        # Task with past due date
        task_overdue = Task(
            description="Overdue task",
            due_date="2020-01-01"
        )
        self.assertTrue(task_overdue.is_overdue())
        
        # Task with future due date
        task_future = Task(
            description="Future task",
            due_date="2030-12-31"
        )
        self.assertFalse(task_future.is_overdue())
        
        # Completed task should not be overdue
        task_completed = Task(
            description="Completed task",
            due_date="2020-01-01",
            completed=True
        )
        self.assertFalse(task_completed.is_overdue())
        
        # Task without due date
        task_no_date = Task(description="No date task")
        self.assertFalse(task_no_date.is_overdue())


if __name__ == '__main__':
    unittest.main()
