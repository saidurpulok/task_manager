"""
Data export/import utilities for tasks.
Supports JSON and CSV formats.
"""
import json
import csv
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import List

from models.task import Task
from config.settings import Settings

logger = logging.getLogger("TaskManager.DataExport")


class DataExporter:
    """Handle data export/import operations."""
    
    @staticmethod
    def export_to_json(tasks: List[Task], filename: str = None) -> Path:
        """
        Export tasks to JSON file.
        
        Args:
            tasks: List of tasks to export
            filename: Optional filename, auto-generated if not provided
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tasks_export_{timestamp}.json"
        
        filepath = Settings.EXPORT_DIR / filename
        
        try:
            data = {
                'exported_at': datetime.now().isoformat(),
                'task_count': len(tasks),
                'tasks': [task.to_dict() for task in tasks]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported {len(tasks)} tasks to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to export to JSON: {e}")
            raise
    
    @staticmethod
    def import_from_json(filepath: Path) -> List[Task]:
        """
        Import tasks from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            List of imported tasks
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tasks = []
            for task_data in data.get('tasks', []):
                # Remove id to create new tasks on import
                task_data.pop('id', None)
                tasks.append(Task.from_dict(task_data))
            
            logger.info(f"Imported {len(tasks)} tasks from {filepath}")
            return tasks
        except Exception as e:
            logger.error(f"Failed to import from JSON: {e}")
            raise
    
    @staticmethod
    def export_to_csv(tasks: List[Task], filename: str = None) -> Path:
        """
        Export tasks to CSV file.
        
        Args:
            tasks: List of tasks to export
            filename: Optional filename, auto-generated if not provided
            
        Returns:
            Path to the exported file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tasks_export_{timestamp}.csv"
        
        filepath = Settings.EXPORT_DIR / filename
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if tasks:
                    fieldnames = tasks[0].to_dict().keys()
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for task in tasks:
                        writer.writerow(task.to_dict())
            
            logger.info(f"Exported {len(tasks)} tasks to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            raise
    
    @staticmethod
    def import_from_csv(filepath: Path) -> List[Task]:
        """
        Import tasks from CSV file.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            List of imported tasks
        """
        try:
            tasks = []
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert string values to proper types
                    row['id'] = None  # Don't import IDs
                    row['completed'] = row.get('completed', '0') in ('1', 'True', 'true')
                    # Remove None strings
                    for key in row:
                        if row[key] in ('None', 'null', ''):
                            row[key] = None
                    tasks.append(Task.from_dict(row))
            
            logger.info(f"Imported {len(tasks)} tasks from {filepath}")
            return tasks
        except Exception as e:
            logger.error(f"Failed to import from CSV: {e}")
            raise
    
    @staticmethod
    def create_backup(db_path: Path) -> Path:
        """
        Create a backup of the database file.
        
        Args:
            db_path: Path to database file
            
        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"tasks_backup_{timestamp}.db"
        backup_path = Settings.BACKUP_DIR / backup_filename
        
        try:
            shutil.copy2(db_path, backup_path)
            logger.info(f"Created backup at {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise
    
    @staticmethod
    def restore_backup(backup_path: Path, db_path: Path):
        """
        Restore database from a backup file.
        
        Args:
            backup_path: Path to backup file
            db_path: Path where database should be restored
        """
        try:
            shutil.copy2(backup_path, db_path)
            logger.info(f"Restored database from {backup_path}")
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}")
            raise
