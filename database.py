"""
Enhanced database module with ORM-like functionality, migrations, and error handling.
"""
import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional, Tuple
from pathlib import Path

from models.task import Task
from models.category import Category
from config.settings import Settings

logger = logging.getLogger("TaskManager.Database")


class DatabaseError(Exception):
    """Custom exception for database operations."""
    pass


class TaskDatabase:
    """
    Enhanced database manager with context manager support, 
    migrations, and comprehensive error handling.
    """
    
    VERSION = 2  # Database schema version
    
    def __init__(self, db_file: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            db_file: Path to database file. If None, uses default from settings.
        """
        self.db_path = Path(db_file) if db_file else Settings.DB_PATH
        self.connection = None
        self._connect()
        self._initialize_database()
        logger.info(f"Database initialized at {self.db_path}")
    
    def _connect(self):
        """Establish database connection."""
        try:
            self.connection = sqlite3.connect(str(self.db_path))
            self.connection.row_factory = sqlite3.Row
            # Enable foreign keys
            self.connection.execute("PRAGMA foreign_keys = ON")
            logger.debug("Database connection established")
        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            raise DatabaseError(f"Database connection failed: {e}")
    
    def _initialize_database(self):
        """Initialize database with schema and migrations."""
        self._create_version_table()
        current_version = self._get_version()
        
        if current_version == 0:
            # New database
            self._create_initial_schema()
            self._set_version(self.VERSION)
        elif current_version < self.VERSION:
            # Run migrations
            self._run_migrations(current_version)
    
    def _create_version_table(self):
        """Create version tracking table."""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL
                )
            ''')
            self.connection.commit()
        except sqlite3.Error as e:
            logger.error(f"Failed to create version table: {e}")
            raise DatabaseError(f"Version table creation failed: {e}")
    
    def _get_version(self) -> int:
        """Get current database schema version."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT MAX(version) as version FROM schema_version")
            row = cursor.fetchone()
            return row[0] if row[0] is not None else 0
        except sqlite3.Error:
            return 0
    
    def _set_version(self, version: int):
        """Set database schema version."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO schema_version (version, applied_at) VALUES (?, ?)",
                (version, datetime.now().isoformat())
            )
            self.connection.commit()
            logger.info(f"Database version set to {version}")
        except sqlite3.Error as e:
            logger.error(f"Failed to set version: {e}")
            raise DatabaseError(f"Version update failed: {e}")
    
    def _create_initial_schema(self):
        """Create initial database schema."""
        try:
            cursor = self.connection.cursor()
            
            # Categories table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT
                )
            ''')
            
            # Tasks table with enhanced fields
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    priority TEXT DEFAULT 'Medium',
                    category TEXT DEFAULT 'General',
                    due_date TEXT,
                    completed INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    completed_at TEXT,
                    FOREIGN KEY (category) REFERENCES categories(name)
                        ON UPDATE CASCADE
                        ON DELETE SET DEFAULT
                )
            ''')
            
            # Insert default category
            cursor.execute(
                "INSERT OR IGNORE INTO categories (name, description) VALUES (?, ?)",
                ("General", "Default category for uncategorized tasks")
            )
            
            # Create indexes for better performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)"
            )
            
            self.connection.commit()
            logger.info("Initial database schema created")
        except sqlite3.Error as e:
            logger.error(f"Failed to create initial schema: {e}")
            raise DatabaseError(f"Schema creation failed: {e}")
    
    def _run_migrations(self, from_version: int):
        """Run database migrations."""
        logger.info(f"Running migrations from version {from_version} to {self.VERSION}")
        
        if from_version < 2:
            self._migrate_v1_to_v2()
        
        self._set_version(self.VERSION)
    
    def _migrate_v1_to_v2(self):
        """Migrate from version 1 to version 2 (add new fields)."""
        try:
            cursor = self.connection.cursor()
            
            # Check if old schema exists and migrate
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'")
            if cursor.fetchone():
                # Get existing columns
                cursor.execute("PRAGMA table_info(tasks)")
                columns = [row[1] for row in cursor.fetchall()]
                
                # Add new columns if they don't exist
                if 'priority' not in columns:
                    cursor.execute("ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'Medium'")
                if 'category' not in columns:
                    cursor.execute("ALTER TABLE tasks ADD COLUMN category TEXT DEFAULT 'General'")
                if 'due_date' not in columns:
                    cursor.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")
                if 'created_at' not in columns:
                    cursor.execute("ALTER TABLE tasks ADD COLUMN created_at TEXT")
                    # Set created_at for existing tasks
                    cursor.execute(
                        "UPDATE tasks SET created_at = ? WHERE created_at IS NULL",
                        (datetime.now().isoformat(),)
                    )
                if 'updated_at' not in columns:
                    cursor.execute("ALTER TABLE tasks ADD COLUMN updated_at TEXT")
                    cursor.execute(
                        "UPDATE tasks SET updated_at = ? WHERE updated_at IS NULL",
                        (datetime.now().isoformat(),)
                    )
                if 'completed_at' not in columns:
                    cursor.execute("ALTER TABLE tasks ADD COLUMN completed_at TEXT")
            
            # Create categories table if it doesn't exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='categories'")
            if not cursor.fetchone():
                cursor.execute('''
                    CREATE TABLE categories (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        description TEXT
                    )
                ''')
                cursor.execute(
                    "INSERT INTO categories (name, description) VALUES (?, ?)",
                    ("General", "Default category for uncategorized tasks")
                )
            
            self.connection.commit()
            logger.info("Migration to v2 completed")
        except sqlite3.Error as e:
            logger.error(f"Migration failed: {e}")
            raise DatabaseError(f"Migration to v2 failed: {e}")
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        try:
            yield self.connection
            self.connection.commit()
            logger.debug("Transaction committed")
        except sqlite3.Error as e:
            self.connection.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise DatabaseError(f"Transaction failed: {e}")
    
    def insert_task(self, task: Task) -> int:
        """
        Insert a new task into the database.
        
        Args:
            task: Task object to insert
            
        Returns:
            ID of the inserted task
        """
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()
                now = datetime.now().isoformat()
                cursor.execute('''
                    INSERT INTO tasks (
                        description, priority, category, due_date, 
                        completed, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    task.description,
                    task.priority,
                    task.category,
                    task.due_date,
                    int(task.completed),
                    now,
                    now
                ))
                task_id = cursor.lastrowid
                logger.info(f"Task created with ID {task_id}")
                return task_id
        except sqlite3.Error as e:
            logger.error(f"Failed to insert task: {e}")
            raise DatabaseError(f"Failed to insert task: {e}")
    
    def update_task(self, task: Task):
        """
        Update an existing task.
        
        Args:
            task: Task object with updated data
        """
        if task.id is None:
            raise ValueError("Cannot update task without ID")
        
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE tasks 
                    SET description = ?, priority = ?, category = ?, 
                        due_date = ?, completed = ?, updated_at = ?
                    WHERE id = ?
                ''', (
                    task.description,
                    task.priority,
                    task.category,
                    task.due_date,
                    int(task.completed),
                    datetime.now().isoformat(),
                    task.id
                ))
                if cursor.rowcount == 0:
                    raise DatabaseError(f"Task with ID {task.id} not found")
                logger.info(f"Task {task.id} updated")
        except sqlite3.Error as e:
            logger.error(f"Failed to update task: {e}")
            raise DatabaseError(f"Failed to update task: {e}")
    
    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        """Get a task by its ID."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE id = ?",
                (task_id,)
            )
            row = cursor.fetchone()
            if row:
                return Task.from_db_row(tuple(row))
            return None
        except sqlite3.Error as e:
            logger.error(f"Failed to get task: {e}")
            raise DatabaseError(f"Failed to get task: {e}")
    
    def get_all_tasks(self, include_completed: bool = False) -> List[Task]:
        """
        Get all tasks, optionally including completed ones.
        
        Args:
            include_completed: Whether to include completed tasks
            
        Returns:
            List of Task objects
        """
        try:
            cursor = self.connection.cursor()
            if include_completed:
                cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
            else:
                cursor.execute(
                    "SELECT * FROM tasks WHERE completed = 0 ORDER BY created_at DESC"
                )
            return [Task.from_db_row(tuple(row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get tasks: {e}")
            raise DatabaseError(f"Failed to get tasks: {e}")
    
    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE completed = 1 ORDER BY completed_at DESC"
            )
            return [Task.from_db_row(tuple(row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get completed tasks: {e}")
            raise DatabaseError(f"Failed to get completed tasks: {e}")
    
    def get_tasks_by_category(self, category: str) -> List[Task]:
        """Get all tasks in a specific category."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE category = ? ORDER BY created_at DESC",
                (category,)
            )
            return [Task.from_db_row(tuple(row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get tasks by category: {e}")
            raise DatabaseError(f"Failed to get tasks by category: {e}")
    
    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        """Get all tasks with a specific priority."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE priority = ? ORDER BY created_at DESC",
                (priority,)
            )
            return [Task.from_db_row(tuple(row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get tasks by priority: {e}")
            raise DatabaseError(f"Failed to get tasks by priority: {e}")
    
    def search_tasks(self, query: str) -> List[Task]:
        """
        Search tasks by description.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching tasks
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT * FROM tasks WHERE description LIKE ? ORDER BY created_at DESC",
                (f"%{query}%",)
            )
            return [Task.from_db_row(tuple(row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to search tasks: {e}")
            raise DatabaseError(f"Failed to search tasks: {e}")
    
    def mark_task_complete(self, task_id: int):
        """Mark a task as completed."""
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE tasks 
                    SET completed = 1, completed_at = ?, updated_at = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), datetime.now().isoformat(), task_id))
                if cursor.rowcount == 0:
                    raise DatabaseError(f"Task with ID {task_id} not found")
                logger.info(f"Task {task_id} marked as complete")
        except sqlite3.Error as e:
            logger.error(f"Failed to mark task complete: {e}")
            raise DatabaseError(f"Failed to mark task complete: {e}")
    
    def mark_task_incomplete(self, task_id: int):
        """Mark a task as incomplete."""
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE tasks 
                    SET completed = 0, completed_at = NULL, updated_at = ?
                    WHERE id = ?
                ''', (datetime.now().isoformat(), task_id))
                if cursor.rowcount == 0:
                    raise DatabaseError(f"Task with ID {task_id} not found")
                logger.info(f"Task {task_id} marked as incomplete")
        except sqlite3.Error as e:
            logger.error(f"Failed to mark task incomplete: {e}")
            raise DatabaseError(f"Failed to mark task incomplete: {e}")
    
    def delete_task(self, task_id: int):
        """Delete a task."""
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                if cursor.rowcount == 0:
                    raise DatabaseError(f"Task with ID {task_id} not found")
                logger.info(f"Task {task_id} deleted")
        except sqlite3.Error as e:
            logger.error(f"Failed to delete task: {e}")
            raise DatabaseError(f"Failed to delete task: {e}")
    
    # Category operations
    
    def insert_category(self, category: Category) -> int:
        """Insert a new category."""
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO categories (name, description) VALUES (?, ?)",
                    (category.name, category.description)
                )
                logger.info(f"Category '{category.name}' created")
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            raise DatabaseError(f"Category '{category.name}' already exists")
        except sqlite3.Error as e:
            logger.error(f"Failed to insert category: {e}")
            raise DatabaseError(f"Failed to insert category: {e}")
    
    def get_all_categories(self) -> List[Category]:
        """Get all categories."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY name")
            return [Category.from_db_row(tuple(row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get categories: {e}")
            raise DatabaseError(f"Failed to get categories: {e}")
    
    def delete_category(self, category_name: str):
        """Delete a category (tasks will be moved to General)."""
        if category_name == "General":
            raise ValueError("Cannot delete the General category")
        
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM categories WHERE name = ?", (category_name,))
                if cursor.rowcount == 0:
                    raise DatabaseError(f"Category '{category_name}' not found")
                logger.info(f"Category '{category_name}' deleted")
        except sqlite3.Error as e:
            logger.error(f"Failed to delete category: {e}")
            raise DatabaseError(f"Failed to delete category: {e}")
    
    def get_task_statistics(self) -> dict:
        """Get statistics about tasks."""
        try:
            cursor = self.connection.cursor()
            
            # Total tasks
            cursor.execute("SELECT COUNT(*) FROM tasks")
            total = cursor.fetchone()[0]
            
            # Completed tasks
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE completed = 1")
            completed = cursor.fetchone()[0]
            
            # Tasks by priority
            cursor.execute("""
                SELECT priority, COUNT(*) 
                FROM tasks 
                WHERE completed = 0 
                GROUP BY priority
            """)
            by_priority = dict(cursor.fetchall())
            
            # Tasks by category
            cursor.execute("""
                SELECT category, COUNT(*) 
                FROM tasks 
                WHERE completed = 0 
                GROUP BY category
            """)
            by_category = dict(cursor.fetchall())
            
            # Overdue tasks
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tasks 
                WHERE completed = 0 
                AND due_date IS NOT NULL 
                AND date(due_date) < date('now')
            """)
            overdue = cursor.fetchone()[0]
            
            return {
                'total': total,
                'completed': completed,
                'active': total - completed,
                'by_priority': by_priority,
                'by_category': by_category,
                'overdue': overdue
            }
        except sqlite3.Error as e:
            logger.error(f"Failed to get statistics: {e}")
            raise DatabaseError(f"Failed to get statistics: {e}")
    
    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")
