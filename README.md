# Task Manager Application

This Task Manager Application is a simple task management tool built using Python and Tkinter. The purpose of this application is to introduce beginner programmers to CRUD functionality with a database. (The update part is not implemented yet, I'll do it when I'm free. Feel free to do it if you want to.)
For now this app allows users to manage their tasks by adding, marking as complete, and deleting tasks. The application uses SQLite for storing task data persistently.

## Features

- Add new tasks to the task list.
- Mark tasks as complete and move them to the completed tasks list.
- Delete tasks from both the active and completed tasks lists.
- Persist task data using an SQLite database.

## Installation
This is as easy as it can get!

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/saidurpulok/task_manager.git
   ```

2. **Install Dependencies:**

   Ensure you have Python (3.x) installed on your system. Usually tkinter and sqlite3 is included with Python. 
   However you can install them using pip:

   ```bash
   pip install tkinter
   pip install sqlite3
   ```

3. **Run the Application:**

   Navigate to the project directory and run the `main.py` file:

   ```bash
   cd task-manager
   python main.py
   ```

## Usage

1. **Adding a New Task:**

   Click on the "Add Task" button, enter the task description in the prompt, and press Enter or click OK.

2. **Marking a Task as Complete:**

   Select a task from the "Tasks" list and click on the "Mark Complete" button to move it to the "Completed Tasks" list.

3. **Deleting a Task:**

   Select a task from either the "Tasks" or "Completed Tasks" list and click on the "Delete Task" or "Delete Completed Task" button, respectively.

## Database

The application uses SQLite to store task data persistently. The database file (`tasks.db`) will be created in the project directory upon running the application for the first time.

## Contributing

Contributions are welcome! If you have suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/new-feature`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature/new-feature`).
5. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact
If you have any questions or suggestions, feel free to reach out to us at [saidurr13@gmail.com](mailto:saidurr13@gmail.com).
