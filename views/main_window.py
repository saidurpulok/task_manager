"""
Enhanced Task Manager UI with modern design and advanced features.
Includes task editing, filtering, search, and data export/import.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import logging
from typing import Optional

from database import TaskDatabase, DatabaseError
from models.task import Task
from models.category import Category
from config.settings import Settings
from utils.data_export import DataExporter
from utils.validators import TaskValidator

logger = logging.getLogger("TaskManager.UI")


class TaskManagerApp:
    """Enhanced Task Manager application with modern UI."""
    
    def __init__(self, root: tk.Tk, db_file: Optional[str] = None):
        """Initialize the Task Manager application."""
        self.root = root
        self.root.title("Task Manager Pro")
        self.root.geometry(f"{Settings.WINDOW_WIDTH}x{Settings.WINDOW_HEIGHT}")
        
        # Initialize database
        try:
            self.db = TaskDatabase(db_file)
            logger.info("Application started successfully")
        except DatabaseError as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")
            self.root.destroy()
            return
        
        # Current filter state
        self.current_filter = {"category": None, "priority": None, "search": None}
        
        # Setup UI
        self._setup_menu()
        self._setup_toolbar()
        self._setup_main_content()
        self._setup_status_bar()
        
        # Load initial data
        self.refresh_all()
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _setup_menu(self):
        """Setup application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export to JSON", command=self.export_to_json)
        file_menu.add_command(label="Export to CSV", command=self.export_to_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Import from JSON", command=self.import_from_json)
        file_menu.add_command(label="Import from CSV", command=self.import_from_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Create Backup", command=self.create_backup)
        file_menu.add_command(label="Restore Backup", command=self.restore_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Task menu
        task_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Task", menu=task_menu)
        task_menu.add_command(label="Add Task", command=self.add_task, accelerator="Ctrl+N")
        task_menu.add_command(label="Edit Task", command=self.edit_task, accelerator="Ctrl+E")
        task_menu.add_command(label="Delete Task", command=self.delete_task, accelerator="Delete")
        task_menu.add_separator()
        task_menu.add_command(label="Mark Complete", command=self.mark_complete)
        task_menu.add_command(label="Mark Incomplete", command=self.mark_incomplete)
        
        # Category menu
        category_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Category", menu=category_menu)
        category_menu.add_command(label="Manage Categories", command=self.manage_categories)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Refresh", command=self.refresh_all, accelerator="F5")
        view_menu.add_command(label="Statistics", command=self.show_statistics)
        
        # Keyboard shortcuts
        self.root.bind("<Control-n>", lambda e: self.add_task())
        self.root.bind("<Control-e>", lambda e: self.edit_task())
        self.root.bind("<Delete>", lambda e: self.delete_task())
        self.root.bind("<F5>", lambda e: self.refresh_all())
    
    def _setup_toolbar(self):
        """Setup toolbar with search and filter options."""
        toolbar = ttk.Frame(self.root, padding="5")
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Search
        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.apply_filters())
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # Category filter
        ttk.Label(toolbar, text="Category:").pack(side=tk.LEFT, padx=(0, 5))
        self.category_filter_var = tk.StringVar(value="All")
        self.category_filter = ttk.Combobox(
            toolbar, 
            textvariable=self.category_filter_var, 
            state="readonly",
            width=15
        )
        self.category_filter.pack(side=tk.LEFT, padx=(0, 20))
        self.category_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())
        
        # Priority filter
        ttk.Label(toolbar, text="Priority:").pack(side=tk.LEFT, padx=(0, 5))
        self.priority_filter_var = tk.StringVar(value="All")
        priority_filter = ttk.Combobox(
            toolbar,
            textvariable=self.priority_filter_var,
            values=["All"] + Settings.PRIORITY_LEVELS,
            state="readonly",
            width=15
        )
        priority_filter.pack(side=tk.LEFT, padx=(0, 20))
        priority_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())
        
        # Clear filters button
        ttk.Button(
            toolbar, 
            text="Clear Filters", 
            command=self.clear_filters
        ).pack(side=tk.LEFT)
    
    def _setup_main_content(self):
        """Setup main content area with notebook tabs."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Active tasks tab
        self.active_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.active_frame, text="Active Tasks")
        self._setup_task_tree(self.active_frame, "active")
        
        # Completed tasks tab
        self.completed_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.completed_frame, text="Completed Tasks")
        self._setup_task_tree(self.completed_frame, "completed")
        
        # Button frame
        button_frame = ttk.Frame(self.root, padding="5")
        button_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Action buttons
        ttk.Button(
            button_frame, 
            text="Add Task", 
            command=self.add_task
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Edit Task", 
            command=self.edit_task
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Delete Task", 
            command=self.delete_task
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Mark Complete", 
            command=self.mark_complete
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Mark Incomplete", 
            command=self.mark_incomplete
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Refresh", 
            command=self.refresh_all
        ).pack(side=tk.RIGHT, padx=5)
    
    def _setup_task_tree(self, parent: ttk.Frame, tree_type: str):
        """Setup treeview for displaying tasks."""
        # Create frame with scrollbar
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Treeview
        columns = ("ID", "Description", "Priority", "Category", "Due Date", "Created")
        tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show="tree headings",
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=tree.yview)
        hsb.config(command=tree.xview)
        
        # Configure columns
        tree.column("#0", width=30, stretch=False)
        tree.column("ID", width=50, stretch=False)
        tree.column("Description", width=300, stretch=True)
        tree.column("Priority", width=80, stretch=False)
        tree.column("Category", width=100, stretch=False)
        tree.column("Due Date", width=100, stretch=False)
        tree.column("Created", width=150, stretch=False)
        
        # Configure headings
        tree.heading("#0", text="")
        tree.heading("ID", text="ID", command=lambda: self.sort_column(tree, "ID", False))
        tree.heading("Description", text="Description", command=lambda: self.sort_column(tree, "Description", False))
        tree.heading("Priority", text="Priority", command=lambda: self.sort_column(tree, "Priority", False))
        tree.heading("Category", text="Category", command=lambda: self.sort_column(tree, "Category", False))
        tree.heading("Due Date", text="Due Date", command=lambda: self.sort_column(tree, "Due Date", False))
        tree.heading("Created", text="Created", command=lambda: self.sort_column(tree, "Created", False))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Double-click to edit
        tree.bind("<Double-1>", lambda e: self.edit_task())
        
        # Store reference
        if tree_type == "active":
            self.active_tree = tree
        else:
            self.completed_tree = tree
    
    def _setup_status_bar(self):
        """Setup status bar."""
        self.status_bar = ttk.Label(
            self.root, 
            text="Ready", 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_status(self, message: str):
        """Update status bar message."""
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def refresh_categories(self):
        """Refresh category filter dropdown."""
        try:
            categories = self.db.get_all_categories()
            category_names = ["All"] + [cat.name for cat in categories]
            self.category_filter['values'] = category_names
        except DatabaseError as e:
            logger.error(f"Failed to refresh categories: {e}")
    
    def refresh_active_tasks(self):
        """Refresh active tasks treeview."""
        # Clear existing items
        for item in self.active_tree.get_children():
            self.active_tree.delete(item)
        
        try:
            tasks = self.db.get_all_tasks(include_completed=False)
            self._populate_tree(self.active_tree, tasks)
        except DatabaseError as e:
            messagebox.showerror("Error", f"Failed to load tasks: {e}")
            logger.error(f"Failed to refresh active tasks: {e}")
    
    def refresh_completed_tasks(self):
        """Refresh completed tasks treeview."""
        # Clear existing items
        for item in self.completed_tree.get_children():
            self.completed_tree.delete(item)
        
        try:
            tasks = self.db.get_completed_tasks()
            self._populate_tree(self.completed_tree, tasks)
        except DatabaseError as e:
            messagebox.showerror("Error", f"Failed to load completed tasks: {e}")
            logger.error(f"Failed to refresh completed tasks: {e}")
    
    def refresh_all(self):
        """Refresh all UI components."""
        self.refresh_categories()
        self.refresh_active_tasks()
        self.refresh_completed_tasks()
        self.update_status_statistics()
    
    def _populate_tree(self, tree: ttk.Treeview, tasks: list):
        """Populate treeview with tasks."""
        for task in tasks:
            # Determine row color based on priority
            tags = (task.priority.lower(),)
            if task.is_overdue():
                tags += ("overdue",)
            
            # Format dates
            created = task.created_at.split('T')[0] if task.created_at else ""
            due_date = task.due_date if task.due_date else ""
            
            tree.insert(
                "",
                tk.END,
                values=(
                    task.id,
                    task.description,
                    task.priority,
                    task.category,
                    due_date,
                    created
                ),
                tags=tags
            )
        
        # Configure tags for color coding
        tree.tag_configure("low", background=Settings.PRIORITY_COLORS["Low"])
        tree.tag_configure("medium", background=Settings.PRIORITY_COLORS["Medium"])
        tree.tag_configure("high", background=Settings.PRIORITY_COLORS["High"])
        tree.tag_configure("urgent", background=Settings.PRIORITY_COLORS["Urgent"])
        tree.tag_configure("overdue", foreground="#FF0000", font=("TkDefaultFont", 9, "bold"))
    
    def get_selected_task_id(self) -> Optional[int]:
        """Get ID of currently selected task."""
        current_tab = self.notebook.index(self.notebook.select())
        tree = self.active_tree if current_tab == 0 else self.completed_tree
        
        selection = tree.selection()
        if not selection:
            return None
        
        item = tree.item(selection[0])
        return int(item['values'][0])
    
    def add_task(self):
        """Open dialog to add a new task."""
        dialog = TaskDialog(self.root, self.db, "Add Task")
        if dialog.result:
            try:
                task_id = self.db.insert_task(dialog.result)
                self.refresh_all()
                self.update_status(f"Task added successfully (ID: {task_id})")
                logger.info(f"Task added: {task_id}")
            except DatabaseError as e:
                messagebox.showerror("Error", f"Failed to add task: {e}")
    
    def edit_task(self):
        """Open dialog to edit selected task."""
        task_id = self.get_selected_task_id()
        if not task_id:
            messagebox.showwarning("No Selection", "Please select a task to edit")
            return
        
        try:
            task = self.db.get_task_by_id(task_id)
            if not task:
                messagebox.showerror("Error", "Task not found")
                return
            
            dialog = TaskDialog(self.root, self.db, "Edit Task", task)
            if dialog.result:
                self.db.update_task(dialog.result)
                self.refresh_all()
                self.update_status(f"Task updated successfully (ID: {task_id})")
                logger.info(f"Task updated: {task_id}")
        except DatabaseError as e:
            messagebox.showerror("Error", f"Failed to edit task: {e}")
    
    def delete_task(self):
        """Delete selected task."""
        task_id = self.get_selected_task_id()
        if not task_id:
            messagebox.showwarning("No Selection", "Please select a task to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?"):
            try:
                self.db.delete_task(task_id)
                self.refresh_all()
                self.update_status(f"Task deleted (ID: {task_id})")
                logger.info(f"Task deleted: {task_id}")
            except DatabaseError as e:
                messagebox.showerror("Error", f"Failed to delete task: {e}")
    
    def mark_complete(self):
        """Mark selected task as complete."""
        task_id = self.get_selected_task_id()
        if not task_id:
            messagebox.showwarning("No Selection", "Please select a task to mark complete")
            return
        
        try:
            self.db.mark_task_complete(task_id)
            self.refresh_all()
            self.update_status(f"Task marked as complete (ID: {task_id})")
            logger.info(f"Task marked complete: {task_id}")
        except DatabaseError as e:
            messagebox.showerror("Error", f"Failed to mark task complete: {e}")
    
    def mark_incomplete(self):
        """Mark selected task as incomplete."""
        task_id = self.get_selected_task_id()
        if not task_id:
            messagebox.showwarning("No Selection", "Please select a task to mark incomplete")
            return
        
        try:
            self.db.mark_task_incomplete(task_id)
            self.refresh_all()
            self.update_status(f"Task marked as incomplete (ID: {task_id})")
            logger.info(f"Task marked incomplete: {task_id}")
        except DatabaseError as e:
            messagebox.showerror("Error", f"Failed to mark task incomplete: {e}")
    
    def apply_filters(self):
        """Apply search and filter criteria."""
        # Store filter state
        self.current_filter["search"] = self.search_var.get()
        self.current_filter["category"] = self.category_filter_var.get()
        self.current_filter["priority"] = self.priority_filter_var.get()
        
        # Get all tasks
        try:
            all_tasks = self.db.get_all_tasks(include_completed=False)
            
            # Apply filters
            filtered_tasks = all_tasks
            
            if self.current_filter["search"]:
                search_lower = self.current_filter["search"].lower()
                filtered_tasks = [
                    t for t in filtered_tasks 
                    if search_lower in t.description.lower()
                ]
            
            if self.current_filter["category"] and self.current_filter["category"] != "All":
                filtered_tasks = [
                    t for t in filtered_tasks 
                    if t.category == self.current_filter["category"]
                ]
            
            if self.current_filter["priority"] and self.current_filter["priority"] != "All":
                filtered_tasks = [
                    t for t in filtered_tasks 
                    if t.priority == self.current_filter["priority"]
                ]
            
            # Update tree
            for item in self.active_tree.get_children():
                self.active_tree.delete(item)
            self._populate_tree(self.active_tree, filtered_tasks)
            
            self.update_status(f"Showing {len(filtered_tasks)} of {len(all_tasks)} tasks")
        except DatabaseError as e:
            messagebox.showerror("Error", f"Failed to apply filters: {e}")
    
    def clear_filters(self):
        """Clear all filters and search."""
        self.search_var.set("")
        self.category_filter_var.set("All")
        self.priority_filter_var.set("All")
        self.refresh_active_tasks()
        self.update_status("Filters cleared")
    
    def sort_column(self, tree: ttk.Treeview, col: str, reverse: bool):
        """Sort treeview by column."""
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        l.sort(reverse=reverse)
        
        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)
        
        tree.heading(col, command=lambda: self.sort_column(tree, col, not reverse))
    
    def manage_categories(self):
        """Open category management dialog."""
        CategoryDialog(self.root, self.db)
        self.refresh_all()
    
    def show_statistics(self):
        """Show task statistics dialog."""
        try:
            stats = self.db.get_task_statistics()
            
            message = f"""Task Statistics:
            
Total Tasks: {stats['total']}
Active Tasks: {stats['active']}
Completed Tasks: {stats['completed']}
Overdue Tasks: {stats['overdue']}

Tasks by Priority:
"""
            for priority in Settings.PRIORITY_LEVELS:
                count = stats['by_priority'].get(priority, 0)
                message += f"  {priority}: {count}\n"
            
            message += "\nTasks by Category:\n"
            for category, count in stats['by_category'].items():
                message += f"  {category}: {count}\n"
            
            messagebox.showinfo("Task Statistics", message)
        except DatabaseError as e:
            messagebox.showerror("Error", f"Failed to get statistics: {e}")
    
    def update_status_statistics(self):
        """Update status bar with quick statistics."""
        try:
            stats = self.db.get_task_statistics()
            status_text = f"Active: {stats['active']} | Completed: {stats['completed']}"
            if stats['overdue'] > 0:
                status_text += f" | Overdue: {stats['overdue']}"
            self.update_status(status_text)
        except DatabaseError:
            pass
    
    def export_to_json(self):
        """Export tasks to JSON file."""
        try:
            tasks = self.db.get_all_tasks(include_completed=True)
            filepath = DataExporter.export_to_json(tasks)
            messagebox.showinfo("Export Successful", f"Tasks exported to:\n{filepath}")
            self.update_status(f"Exported {len(tasks)} tasks to JSON")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export tasks: {e}")
    
    def export_to_csv(self):
        """Export tasks to CSV file."""
        try:
            tasks = self.db.get_all_tasks(include_completed=True)
            filepath = DataExporter.export_to_csv(tasks)
            messagebox.showinfo("Export Successful", f"Tasks exported to:\n{filepath}")
            self.update_status(f"Exported {len(tasks)} tasks to CSV")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Failed to export tasks: {e}")
    
    def import_from_json(self):
        """Import tasks from JSON file."""
        filepath = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            tasks = DataExporter.import_from_json(filepath)
            for task in tasks:
                self.db.insert_task(task)
            self.refresh_all()
            messagebox.showinfo("Import Successful", f"Imported {len(tasks)} tasks")
            self.update_status(f"Imported {len(tasks)} tasks from JSON")
        except Exception as e:
            messagebox.showerror("Import Failed", f"Failed to import tasks: {e}")
    
    def import_from_csv(self):
        """Import tasks from CSV file."""
        filepath = filedialog.askopenfilename(
            title="Select CSV file",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            tasks = DataExporter.import_from_csv(filepath)
            for task in tasks:
                self.db.insert_task(task)
            self.refresh_all()
            messagebox.showinfo("Import Successful", f"Imported {len(tasks)} tasks")
            self.update_status(f"Imported {len(tasks)} tasks from CSV")
        except Exception as e:
            messagebox.showerror("Import Failed", f"Failed to import tasks: {e}")
    
    def create_backup(self):
        """Create a backup of the database."""
        try:
            backup_path = DataExporter.create_backup(Settings.DB_PATH)
            messagebox.showinfo("Backup Successful", f"Backup created at:\n{backup_path}")
            self.update_status("Database backup created")
        except Exception as e:
            messagebox.showerror("Backup Failed", f"Failed to create backup: {e}")
    
    def restore_backup(self):
        """Restore database from a backup."""
        filepath = filedialog.askopenfilename(
            title="Select backup file",
            filetypes=[("Database files", "*.db"), ("All files", "*.*")],
            initialdir=Settings.BACKUP_DIR
        )
        
        if not filepath:
            return
        
        if messagebox.askyesno(
            "Confirm Restore",
            "Restoring from backup will overwrite the current database.\nAre you sure?"
        ):
            try:
                self.db.close()
                DataExporter.restore_backup(filepath, Settings.DB_PATH)
                self.db = TaskDatabase()
                self.refresh_all()
                messagebox.showinfo("Restore Successful", "Database restored from backup")
                self.update_status("Database restored from backup")
            except Exception as e:
                messagebox.showerror("Restore Failed", f"Failed to restore backup: {e}")
    
    def on_closing(self):
        """Handle application closing."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.db.close()
            logger.info("Application closed")
            self.root.destroy()
    
    def close(self):
        """Close the application."""
        self.db.close()


class TaskDialog:
    """Dialog for adding/editing tasks."""
    
    def __init__(self, parent: tk.Tk, db: TaskDatabase, title: str, task: Optional[Task] = None):
        """Initialize task dialog."""
        self.db = db
        self.result = None
        self.task = task
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("500x400")
        
        # Setup form
        self._setup_form()
        
        # Wait for dialog
        self.dialog.wait_window()
    
    def _setup_form(self):
        """Setup form fields."""
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Description
        ttk.Label(frame, text="Description:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.description_var = tk.StringVar(value=self.task.description if self.task else "")
        description_entry = ttk.Entry(frame, textvariable=self.description_var, width=50)
        description_entry.grid(row=0, column=1, pady=5, sticky=tk.EW)
        description_entry.focus()
        
        # Priority
        ttk.Label(frame, text="Priority:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.priority_var = tk.StringVar(
            value=self.task.priority if self.task else Settings.PRIORITY_LEVELS[1]
        )
        priority_combo = ttk.Combobox(
            frame,
            textvariable=self.priority_var,
            values=Settings.PRIORITY_LEVELS,
            state="readonly",
            width=47
        )
        priority_combo.grid(row=1, column=1, pady=5, sticky=tk.EW)
        
        # Category
        ttk.Label(frame, text="Category:").grid(row=2, column=0, sticky=tk.W, pady=5)
        categories = self.db.get_all_categories()
        category_names = [cat.name for cat in categories]
        self.category_var = tk.StringVar(
            value=self.task.category if self.task else Settings.DEFAULT_CATEGORY
        )
        category_combo = ttk.Combobox(
            frame,
            textvariable=self.category_var,
            values=category_names,
            width=47
        )
        category_combo.grid(row=2, column=1, pady=5, sticky=tk.EW)
        
        # Due Date
        ttk.Label(frame, text="Due Date (YYYY-MM-DD):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.due_date_var = tk.StringVar(value=self.task.due_date if self.task and self.task.due_date else "")
        due_date_entry = ttk.Entry(frame, textvariable=self.due_date_var, width=50)
        due_date_entry.grid(row=3, column=1, pady=5, sticky=tk.EW)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
        
        # Configure grid
        frame.columnconfigure(1, weight=1)
    
    def save(self):
        """Validate and save task."""
        # Validate description
        is_valid, error = TaskValidator.validate_description(self.description_var.get())
        if not is_valid:
            messagebox.showerror("Validation Error", error)
            return
        
        # Validate due date
        is_valid, error = TaskValidator.validate_date(self.due_date_var.get())
        if not is_valid:
            messagebox.showerror("Validation Error", error)
            return
        
        # Create or update task
        try:
            if self.task:
                # Update existing task
                self.task.description = self.description_var.get()
                self.task.priority = self.priority_var.get()
                self.task.category = self.category_var.get()
                self.task.due_date = self.due_date_var.get() if self.due_date_var.get() else None
                self.result = self.task
            else:
                # Create new task
                self.result = Task(
                    description=self.description_var.get(),
                    priority=self.priority_var.get(),
                    category=self.category_var.get(),
                    due_date=self.due_date_var.get() if self.due_date_var.get() else None
                )
            
            self.dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))


class CategoryDialog:
    """Dialog for managing categories."""
    
    def __init__(self, parent: tk.Tk, db: TaskDatabase):
        """Initialize category dialog."""
        self.db = db
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Manage Categories")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.geometry("400x300")
        
        # Setup UI
        self._setup_ui()
        self.refresh_list()
        
        # Wait for dialog
        self.dialog.wait_window()
    
    def _setup_ui(self):
        """Setup dialog UI."""
        frame = ttk.Frame(self.dialog, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.category_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.category_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.category_listbox.yview)
        
        # Add category frame
        add_frame = ttk.Frame(frame)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(add_frame, text="New Category:").pack(side=tk.LEFT, padx=(0, 5))
        self.category_name_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.category_name_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(add_frame, text="Add", command=self.add_category).pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_category).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Close", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def refresh_list(self):
        """Refresh category list."""
        self.category_listbox.delete(0, tk.END)
        categories = self.db.get_all_categories()
        for category in categories:
            self.category_listbox.insert(tk.END, category.name)
    
    def add_category(self):
        """Add a new category."""
        name = self.category_name_var.get().strip()
        if not name:
            return
        
        is_valid, error = TaskValidator.validate_category(name)
        if not is_valid:
            messagebox.showerror("Validation Error", error)
            return
        
        try:
            category = Category(name=name)
            self.db.insert_category(category)
            self.category_name_var.set("")
            self.refresh_list()
        except DatabaseError as e:
            messagebox.showerror("Error", str(e))
    
    def delete_category(self):
        """Delete selected category."""
        selection = self.category_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a category to delete")
            return
        
        category_name = self.category_listbox.get(selection[0])
        
        if category_name == "General":
            messagebox.showerror("Error", "Cannot delete the General category")
            return
        
        if messagebox.askyesno(
            "Confirm Delete",
            f"Delete category '{category_name}'?\nTasks in this category will be moved to General."
        ):
            try:
                self.db.delete_category(category_name)
                self.refresh_list()
            except (DatabaseError, ValueError) as e:
                messagebox.showerror("Error", str(e))
