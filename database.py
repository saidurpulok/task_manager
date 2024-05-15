import sqlite3

class TaskDatabase:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.create_tables()

    def create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                description TEXT NOT NULL,
                completed INTEGER DEFAULT 0
            )
        ''')
        self.connection.commit()

    def insert_task(self, description):
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO tasks (description) VALUES (?)
        ''', (description,))
        self.connection.commit()

    def get_all_tasks(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT id, description FROM tasks WHERE completed = 0
        ''')
        return cursor.fetchall()

    def get_completed_tasks(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT id, description FROM tasks WHERE completed = 1
        ''')
        return cursor.fetchall()

    def mark_task_complete(self, task_id):
        cursor = self.connection.cursor()
        cursor.execute('''
            UPDATE tasks SET completed = 1 WHERE id = ?
        ''', (task_id,))
        self.connection.commit()

    def delete_task(self, task_id):
        cursor = self.connection.cursor()
        cursor.execute('''
            DELETE FROM tasks WHERE id = ?
        ''', (task_id,))
        self.connection.commit()

    def close(self):
        self.connection.close()
