import tkinter as tk
from tkinter import ttk
import functions as func
from database import TaskDatabase

class TaskManagerApp:
    def __init__(self, root, db_file):
        self.root = root
        self.root.title("Task Manager")
        self.db = TaskDatabase(db_file)
        
        # Create notebook widget to hold multiple tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=20)
        
        # Create task listbox in the "Tasks" tab
        self.task_tab = tk.Frame(self.notebook)
        self.notebook.add(self.task_tab, text="Tasks")
        
        self.task_listbox = tk.Listbox(self.task_tab, width=70, height=20)
        self.task_listbox.pack()
        
        # Create completed task listbox in the "Completed Tasks" tab
        self.completed_task_tab = tk.Frame(self.notebook)
        self.notebook.add(self.completed_task_tab, text="Completed Tasks")
        
        self.completed_task_listbox = tk.Listbox(self.completed_task_tab, width=70, height=20)
        self.completed_task_listbox.pack()
        
        # Populate task listbox with existing tasks from database
        self.refresh_task_listbox()
        self.refresh_completed_task_listbox()
        
        # Create buttons for task operations
        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack(pady=20)
        
        func.create_button(self.buttons_frame, "Add Task", self.add_task)
        func.create_button(self.buttons_frame, "Mark Complete", self.mark_complete)
        func.create_button(self.buttons_frame, "Delete Task", self.delete_task)
        func.create_button(self.buttons_frame, "Delete Completed Task", self.delete_completed_task)

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        selected_tab = func.get_selected_tab(self.notebook)
        func.handle_tab_change(selected_tab, self.buttons_frame)

    def refresh_task_listbox(self):
        self.task_listbox.delete(0, tk.END)
        tasks = self.db.get_all_tasks()
        for task_id, description in tasks:
            self.task_listbox.insert(tk.END, description)

    def refresh_completed_task_listbox(self):
        self.completed_task_listbox.delete(0, tk.END)
        tasks = self.db.get_completed_tasks()
        for task_id, description in tasks:
            self.completed_task_listbox.insert(tk.END, description)

    def add_task(self):
        new_task = func.get_user_input(self.root, "Add Task", "Enter new task:")
        if new_task:
            self.db.insert_task(new_task)
            self.refresh_task_listbox()

    def mark_complete(self):
        selected_task = func.get_selected_task(self.task_listbox)
        if selected_task:
            task_id = self.get_task_id(selected_task, self.task_listbox)
            if task_id:
                self.db.mark_task_complete(task_id)
                self.refresh_task_listbox()
                self.refresh_completed_task_listbox()

    def delete_task(self):
        selected_task = func.get_selected_task(self.task_listbox)
        if selected_task:
            task_id = self.get_task_id(selected_task, self.task_listbox)
            if task_id:
                self.db.delete_task(task_id)
                self.refresh_task_listbox()

    def delete_completed_task(self):
        selected_task = func.get_selected_task(self.completed_task_listbox)
        if selected_task:
            task_id = self.get_task_id(selected_task, self.completed_task_listbox)
            if task_id:
                self.db.delete_task(task_id)
                self.refresh_completed_task_listbox()

    def get_task_id(self, task_description, listbox):
        tasks = listbox.get(0, tk.END)
        for index, description in enumerate(tasks):
            if description == task_description:
                return index + 1  # SQLite uses 1-based index for IDs

    def close(self):
        self.db.close()
