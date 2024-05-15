import tkinter as tk
from tkinter import simpledialog, ttk
from task_manager import TaskManagerApp

def main():
    root = tk.Tk()
    app = TaskManagerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
