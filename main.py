import tkinter as tk
from task_manager import TaskManagerApp

def main():
    db_file = 'tasks.db'
    root = tk.Tk()
    app = TaskManagerApp(root, db_file)
    root.mainloop()
    app.close()  # Close the database connection when the application exits

if __name__ == "__main__":
    main()
