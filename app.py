from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_FILE = "tasks.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT DEFAULT 'Personal',
                due_date TEXT DEFAULT '',
                status TEXT DEFAULT 'Pending'
            )
        """)
init_db()

@app.route('/')
def index():
    with sqlite3.connect(DB_FILE) as conn:
        tasks = conn.execute("""
            SELECT id, title, category, due_date, status 
            FROM tasks ORDER BY id DESC
        """).fetchall()
        
        # Calculate stats
        total = len(tasks)
        completed = sum(1 for t in tasks if t[4] == 'Completed')
        pending = total - completed

    return render_template('index.html', tasks=tasks, total=total, pending=pending, completed=completed)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    category = request.form.get('category') or 'Personal'
    due_date = request.form.get('due_date') or ''

    if title:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("""
                INSERT INTO tasks (title, category, due_date, status)
                VALUES (?, ?, ?, 'Pending')
            """, (title, category, due_date))
    return redirect(url_for('index'))

@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            UPDATE tasks 
            SET status = CASE WHEN status = 'Pending' THEN 'Completed' ELSE 'Pending' END 
            WHERE id = ?
        """, (task_id,))
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return redirect(url_for('index'))

@app.route('/clear', methods=['POST'])
def clear_all():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM tasks")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)