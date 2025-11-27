# Task Manager Pro

A feature-rich, intermediate-level task management application built with Python and Tkinter. This application demonstrates professional software development practices including MVC architecture, database migrations, data export/import, and comprehensive testing.

## 🎯 Project Level: Intermediate

This project has been enhanced from a beginner-level application to an intermediate-level application with professional features and best practices.

## ✨ Features

### Core Functionality
- ✅ **Full CRUD Operations** - Create, Read, Update, and Delete tasks
- 📝 **Task Editing** - Edit any task attribute at any time
- ✓ **Task Completion** - Mark tasks as complete or incomplete
- 🎨 **Color-Coded Priorities** - Visual priority indicators (Low, Medium, High, Urgent)
- 📁 **Categories** - Organize tasks with custom categories
- 📅 **Due Dates** - Set and track task deadlines
- ⚠️ **Overdue Detection** - Automatic highlighting of overdue tasks

### Advanced Features
- 🔍 **Search & Filter** - Search by description, filter by category or priority
- 📊 **Task Statistics** - View comprehensive statistics about your tasks
- 💾 **Data Export** - Export tasks to JSON or CSV formats
- 📥 **Data Import** - Import tasks from JSON or CSV files
- 🔄 **Backup & Restore** - Create database backups and restore when needed
- 🗂️ **Multi-Column View** - Sortable columns with TreeView widget
- 🎯 **Category Management** - Create and manage custom categories

### Technical Features
- 🏗️ **MVC Architecture** - Properly separated concerns with models, views, and database layers
- 🗄️ **Database Migrations** - Automatic schema versioning and migration
- 📝 **Comprehensive Logging** - Application logging with file and console output
- ⚙️ **Configuration Management** - Environment variable support
- 🧪 **Unit Tests** - Extensive test coverage for models and database operations
- 🔒 **Error Handling** - Robust error handling with user-friendly messages
- 🎨 **Modern UI** - Clean, intuitive interface with keyboard shortcuts

## 📁 Project Structure

```
task_manager/
├── config/              # Configuration and settings
│   ├── __init__.py
│   └── settings.py      # Application settings with env variable support
├── models/              # Data models
│   ├── __init__.py
│   ├── task.py          # Task model with validation
│   └── category.py      # Category model
├── utils/               # Utility modules
│   ├── __init__.py
│   ├── data_export.py   # Export/import functionality
│   └── validators.py    # Data validation utilities
├── views/               # UI components
│   ├── __init__.py
│   └── main_window.py   # Main application window
├── tests/               # Unit tests
│   ├── __init__.py
│   ├── test_task.py     # Task model tests
│   └── test_database.py # Database operation tests
├── data/                # Data directory (auto-created)
│   ├── exports/         # Exported files
│   └── backups/         # Database backups
├── logs/                # Log files (auto-created)
├── database.py          # Enhanced database layer with migrations
├── main.py              # Application entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment configuration
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/saidurpulok/task_manager.git
   cd task_manager
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   Note: Tkinter usually comes with Python. If not installed:
   - **Linux**: `sudo apt-get install python3-tk`
   - **macOS**: Included with Python
   - **Windows**: Included with Python

3. **Configure Environment (Optional)**
   ```bash
   cp .env.example .env
   # Edit .env file with your preferences
   ```

4. **Run the Application**
   ```bash
   python main.py
   ```

## 💡 Usage

### Basic Operations

#### Adding a Task
1. Click "Add Task" button or press `Ctrl+N`
2. Enter task description (required)
3. Select priority level (Low, Medium, High, Urgent)
4. Choose or create a category
5. Set a due date (optional, format: YYYY-MM-DD)
6. Click "Save"

#### Editing a Task
1. Select a task from the list
2. Click "Edit Task" button or press `Ctrl+E`
3. Modify any fields
4. Click "Save"

#### Managing Tasks
- **Mark Complete**: Select a task and click "Mark Complete"
- **Mark Incomplete**: Select a completed task and click "Mark Incomplete"
- **Delete Task**: Select a task and press `Delete` key or click "Delete Task"

### Advanced Features

#### Search and Filter
- Use the **Search** box to find tasks by description
- Filter by **Category** using the dropdown
- Filter by **Priority** using the dropdown
- Click **Clear Filters** to reset all filters

#### Data Management
- **Export to JSON/CSV**: File → Export to JSON/CSV
- **Import from JSON/CSV**: File → Import from JSON/CSV
- **Create Backup**: File → Create Backup
- **Restore Backup**: File → Restore Backup

#### Category Management
- Access via **Category → Manage Categories**
- Add new categories
- Delete unused categories (tasks will move to "General")

#### Statistics
- View via **View → Statistics** or `F5` to refresh
- See task counts by priority and category
- Track overdue tasks
- Monitor completion rates

### Keyboard Shortcuts
- `Ctrl+N` - Add new task
- `Ctrl+E` - Edit selected task
- `Delete` - Delete selected task
- `F5` - Refresh view
- Double-click on task - Quick edit

## 🧪 Running Tests

Run the test suite to verify everything works correctly:

```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests.test_task
python -m unittest tests.test_database

# Run with verbose output
python -m unittest discover tests -v
```

## ⚙️ Configuration

The application can be configured using environment variables. Copy `.env.example` to `.env` and modify:

```bash
# Database location
TASK_MANAGER_DB=tasks.db

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# Window dimensions
WINDOW_WIDTH=1000
WINDOW_HEIGHT=700
```

## 📊 Database

The application uses SQLite for data persistence:

- **Automatic Schema Management**: Database schema is versioned and automatically migrated
- **Data Integrity**: Foreign keys and constraints ensure data consistency
- **Performance**: Indexed columns for fast queries
- **Backup-Friendly**: Simple file-based storage for easy backups

### Schema

**Tasks Table:**
- `id` - Unique identifier
- `description` - Task description
- `priority` - Priority level (Low, Medium, High, Urgent)
- `category` - Task category
- `due_date` - Optional due date
- `completed` - Completion status
- `created_at` - Creation timestamp
- `updated_at` - Last update timestamp
- `completed_at` - Completion timestamp

**Categories Table:**
- `id` - Unique identifier
- `name` - Category name (unique)
- `description` - Category description

## 🎓 Learning Highlights

This project demonstrates intermediate Python concepts:

1. **Object-Oriented Programming**: Classes, inheritance, encapsulation
2. **Database Management**: SQLite, migrations, transactions
3. **Error Handling**: Try-except blocks, custom exceptions
4. **Logging**: Structured logging for debugging and monitoring
5. **Testing**: Unit tests with unittest framework
6. **GUI Development**: Tkinter, event handling, custom dialogs
7. **File I/O**: JSON and CSV export/import
8. **Code Organization**: Modular structure, separation of concerns
9. **Data Validation**: Input validation and sanitization
10. **Configuration**: Environment variables and settings management

## 🤝 Contributing

Contributions are welcome! Here are some ideas for enhancements:

- Add recurring tasks functionality
- Implement task reminders/notifications
- Add dark mode theme
- Create task templates
- Add task attachments
- Implement task dependencies
- Add calendar view
- Create reports and charts
- Add user authentication
- Implement cloud sync

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Saidur Rahman Pulok**
- Email: [saidur.pulok@gmail.com](mailto:saidur.pulok@gmail.com)
- GitHub: [@saidurpulok](https://github.com/saidurpulok)

## 🙏 Acknowledgments

- Built as an educational project to demonstrate intermediate Python programming
- Enhanced from a beginner-level project to showcase professional development practices
- Thanks to the Python and Tkinter communities for excellent documentation

## 📸 Screenshots

### Main Window
The main interface shows tasks organized in tabs with color-coded priorities.

### Task Dialog
Add or edit tasks with all attributes including priority, category, and due date.

### Category Management
Create and manage custom categories for better task organization.

### Statistics View
View comprehensive statistics about your tasks and productivity.

---

**Note**: This is an educational project designed to demonstrate intermediate-level Python programming concepts. Feel free to use it as a learning resource or starting point for your own projects!
