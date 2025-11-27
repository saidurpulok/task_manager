"""Unit tests for database operations."""
import unittest
import tempfile
import os
from pathlib import Path

from database import TaskDatabase, DatabaseError
from models.task import Task
from models.category import Category


class TestDatabase(unittest.TestCase):
    """Test cases for database operations."""
    
    def setUp(self):
        """Set up test database."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        self.db = TaskDatabase(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database."""
        self.db.close()
        os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test database initialization and schema creation."""
        # Check that tables were created
        cursor = self.db.connection.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name IN ('tasks', 'categories')"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        self.assertIn('tasks', tables)
        self.assertIn('categories', tables)
        
        # Check default category exists
        categories = self.db.get_all_categories()
        self.assertTrue(any(cat.name == "General" for cat in categories))
    
    def test_insert_and_get_task(self):
        """Test inserting and retrieving a task."""
        task = Task(
            description="Test task",
            priority="High",
            category="General"
        )
        
        # Insert task
        task_id = self.db.insert_task(task)
        self.assertIsNotNone(task_id)
        
        # Retrieve task
        retrieved_task = self.db.get_task_by_id(task_id)
        self.assertIsNotNone(retrieved_task)
        self.assertEqual(retrieved_task.description, "Test task")
        self.assertEqual(retrieved_task.priority, "High")
    
    def test_update_task(self):
        """Test updating a task."""
        # Create and insert task
        task = Task(description="Original", priority="Low", category="General")
        task_id = self.db.insert_task(task)
        
        # Get and update task
        task = self.db.get_task_by_id(task_id)
        task.description = "Updated"
        task.priority = "Urgent"
        self.db.update_task(task)
        
        # Verify update
        updated_task = self.db.get_task_by_id(task_id)
        self.assertEqual(updated_task.description, "Updated")
        self.assertEqual(updated_task.priority, "Urgent")
    
    def test_mark_task_complete(self):
        """Test marking a task as complete."""
        # Create task
        task = Task(description="Test", category="General")
        task_id = self.db.insert_task(task)
        
        # Mark complete
        self.db.mark_task_complete(task_id)
        
        # Verify
        completed_task = self.db.get_task_by_id(task_id)
        self.assertTrue(completed_task.completed)
        self.assertIsNotNone(completed_task.completed_at)
    
    def test_mark_task_incomplete(self):
        """Test marking a completed task as incomplete."""
        # Create and complete task
        task = Task(description="Test", category="General")
        task_id = self.db.insert_task(task)
        self.db.mark_task_complete(task_id)
        
        # Mark incomplete
        self.db.mark_task_incomplete(task_id)
        
        # Verify
        task = self.db.get_task_by_id(task_id)
        self.assertFalse(task.completed)
        self.assertIsNone(task.completed_at)
    
    def test_delete_task(self):
        """Test deleting a task."""
        # Create task
        task = Task(description="Test", category="General")
        task_id = self.db.insert_task(task)
        
        # Delete task
        self.db.delete_task(task_id)
        
        # Verify deletion
        deleted_task = self.db.get_task_by_id(task_id)
        self.assertIsNone(deleted_task)
    
    def test_get_all_tasks(self):
        """Test retrieving all tasks."""
        # Create multiple tasks
        for i in range(3):
            task = Task(description=f"Task {i}", category="General")
            self.db.insert_task(task)
        
        # Get all tasks
        tasks = self.db.get_all_tasks()
        self.assertEqual(len(tasks), 3)
    
    def test_get_completed_tasks(self):
        """Test retrieving completed tasks."""
        # Create tasks, some completed
        task1 = Task(description="Task 1", category="General")
        task2 = Task(description="Task 2", category="General")
        
        id1 = self.db.insert_task(task1)
        id2 = self.db.insert_task(task2)
        
        self.db.mark_task_complete(id1)
        
        # Get completed tasks
        completed = self.db.get_completed_tasks()
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0].id, id1)
    
    def test_search_tasks(self):
        """Test task search functionality."""
        # Create tasks with different descriptions
        self.db.insert_task(Task(description="Python programming", category="General"))
        self.db.insert_task(Task(description="Java development", category="General"))
        self.db.insert_task(Task(description="Python testing", category="General"))
        
        # Search for Python
        results = self.db.search_tasks("Python")
        self.assertEqual(len(results), 2)
    
    def test_get_tasks_by_category(self):
        """Test filtering tasks by category."""
        # Create Work category
        self.db.insert_category(Category(name="Work"))
        
        # Create tasks in different categories
        self.db.insert_task(Task(description="Task 1", category="General"))
        self.db.insert_task(Task(description="Task 2", category="Work"))
        self.db.insert_task(Task(description="Task 3", category="Work"))
        
        # Get tasks by category
        work_tasks = self.db.get_tasks_by_category("Work")
        self.assertEqual(len(work_tasks), 2)
    
    def test_get_tasks_by_priority(self):
        """Test filtering tasks by priority."""
        # Create tasks with different priorities
        self.db.insert_task(Task(description="Task 1", priority="Low", category="General"))
        self.db.insert_task(Task(description="Task 2", priority="High", category="General"))
        self.db.insert_task(Task(description="Task 3", priority="High", category="General"))
        
        # Get tasks by priority
        high_tasks = self.db.get_tasks_by_priority("High")
        self.assertEqual(len(high_tasks), 2)
    
    def test_category_operations(self):
        """Test category CRUD operations."""
        # Create category
        category = Category(name="Personal", description="Personal tasks")
        cat_id = self.db.insert_category(category)
        self.assertIsNotNone(cat_id)
        
        # Get all categories
        categories = self.db.get_all_categories()
        self.assertTrue(any(cat.name == "Personal" for cat in categories))
        
        # Delete category
        self.db.delete_category("Personal")
        categories = self.db.get_all_categories()
        self.assertFalse(any(cat.name == "Personal" for cat in categories))
    
    def test_statistics(self):
        """Test task statistics."""
        # Create various tasks
        self.db.insert_task(Task(description="Task 1", priority="High", category="General"))
        task2_id = self.db.insert_task(Task(description="Task 2", priority="Low", category="General"))
        self.db.mark_task_complete(task2_id)
        
        # Get statistics
        stats = self.db.get_task_statistics()
        
        self.assertEqual(stats['total'], 2)
        self.assertEqual(stats['completed'], 1)
        self.assertEqual(stats['active'], 1)


if __name__ == '__main__':
    unittest.main()
