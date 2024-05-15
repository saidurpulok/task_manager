import tkinter as tk
from tkinter import simpledialog, ttk
import functions as func

class TaskManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Task Manager")
        
        # Initialize tasks list (you can replace this with data from a database later)
        self.tasks = ["Task 1", "Task 2", "Task 3"]
        self.completed_tasks = []  # Initialize completed tasks list
        
        # Create notebook widget to hold multiple tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=20)
        
        # Create task listbox in the "Tasks" tab
        self.task_tab = tk.Frame(self.notebook)
        self.notebook.add(self.task_tab, text="Tasks")
        
        self.task_listbox = tk.Listbox(self.task_tab, width=50, height=15)
        self.task_listbox.pack()
        
        # Create completed task listbox in the "Completed Tasks" tab
        self.completed_task_tab = tk.Frame(self.notebook)
        self.notebook.add(self.completed_task_tab, text="Completed Tasks")
        
        self.completed_task_listbox = tk.Listbox(self.completed_task_tab, width=50, height=15)
        self.completed_task_listbox.pack()
        
        # Populate task listbox with existing tasks
        func.populate_listbox(self.task_listbox, self.tasks)
        func.populate_listbox(self.completed_task_listbox, self.completed_tasks)
        
        # Create buttons for task operations
        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack(pady=20)
        
        func.create_button(self.buttons_frame, "Add Task", self.add_task)
        func.create_button(self.buttons_frame, "Mark Complete", self.mark_complete)
        func.create_button(self.buttons_frame, "Delete Task", self.delete_task)
        func.create_button(self.buttons_frame, "Delete Completed Task", self.delete_completed_task)

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        # Handle tab change
        selected_tab = func.get_selected_tab(self.notebook)
        func.handle_tab_change(selected_tab, self.buttons_frame)

    def add_task(self):
        new_task = func.get_user_input(self.root, "Add Task", "Enter new task:")
        if new_task:
            func.add_task_to_listbox(self.task_listbox, self.tasks, new_task)

    def mark_complete(self):
        selected_task = func.get_selected_task(self.task_listbox)
        if selected_task:
            func.move_task(self.task_listbox, self.tasks, selected_task, self.completed_task_listbox, self.completed_tasks)

    def delete_task(self):
        selected_task = func.get_selected_task(self.task_listbox)
        if selected_task:
            func.delete_task_from_listbox(self.task_listbox, self.tasks, selected_task)

    def delete_completed_task(self):
        selected_task = func.get_selected_task(self.completed_task_listbox)
        if selected_task:
            func.delete_task_from_listbox(self.completed_task_listbox, self.completed_tasks, selected_task)
