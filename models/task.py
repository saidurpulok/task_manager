"""Task model with enhanced attributes."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    """
    Task model representing a task with all its attributes.
    
    Attributes:
        id: Unique identifier for the task
        description: Task description
        priority: Task priority (Low, Medium, High, Urgent)
        category: Task category/tag
        due_date: Optional due date for the task
        completed: Whether the task is completed
        created_at: When the task was created
        updated_at: When the task was last updated
        completed_at: When the task was completed
    """
    description: str
    priority: str = "Medium"
    category: str = "General"
    completed: bool = False
    id: Optional[int] = None
    due_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def __post_init__(self):
        """Validate task data after initialization."""
        if not self.description or not self.description.strip():
            raise ValueError("Task description cannot be empty")
        
        valid_priorities = ["Low", "Medium", "High", "Urgent"]
        if self.priority not in valid_priorities:
            raise ValueError(f"Priority must be one of {valid_priorities}")
    
    def to_dict(self) -> dict:
        """Convert task to dictionary for serialization."""
        return {
            'id': self.id,
            'description': self.description,
            'priority': self.priority,
            'category': self.category,
            'due_date': self.due_date,
            'completed': self.completed,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'completed_at': self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Task':
        """Create a Task instance from a dictionary."""
        return cls(**data)
    
    @classmethod
    def from_db_row(cls, row: tuple) -> 'Task':
        """
        Create a Task instance from a database row.
        Expected row format: (id, description, priority, category, due_date, 
                            completed, created_at, updated_at, completed_at)
        """
        return cls(
            id=row[0],
            description=row[1],
            priority=row[2],
            category=row[3],
            due_date=row[4],
            completed=bool(row[5]),
            created_at=row[6],
            updated_at=row[7],
            completed_at=row[8]
        )
    
    def is_overdue(self) -> bool:
        """Check if task is overdue."""
        if not self.due_date or self.completed:
            return False
        
        try:
            due = datetime.strptime(self.due_date, "%Y-%m-%d")
            return due.date() < datetime.now().date()
        except ValueError:
            return False
    
    def __str__(self) -> str:
        """String representation of the task."""
        status = "✓" if self.completed else "○"
        due = f" (Due: {self.due_date})" if self.due_date else ""
        return f"{status} [{self.priority}] {self.description}{due}"
