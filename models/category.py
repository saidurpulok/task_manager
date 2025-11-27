"""Category model for task organization."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Category:
    """
    Category model for organizing tasks.
    
    Attributes:
        name: Category name
        description: Optional category description
        id: Unique identifier for the category
    """
    name: str
    description: Optional[str] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        """Validate category data."""
        if not self.name or not self.name.strip():
            raise ValueError("Category name cannot be empty")
    
    def to_dict(self) -> dict:
        """Convert category to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }
    
    @classmethod
    def from_db_row(cls, row: tuple) -> 'Category':
        """Create a Category instance from a database row."""
        return cls(
            id=row[0],
            name=row[1],
            description=row[2] if len(row) > 2 else None
        )
    
    def __str__(self) -> str:
        """String representation of the category."""
        return self.name
