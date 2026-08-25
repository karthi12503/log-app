from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_FILE = "tasks.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT DEFAULT 'Pending'
            )
        """)
init_db()

@app.route('/')
def index():
    with sqlite3.connect(DB_FILE) as conn:
        tasks = conn.execute("SELECT id, title, status FROM tasks").fetchall()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form.get('title')
    if title:
        with sqlite3.connect(DB_FILE) as conn:
            conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
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

@app.route('/clear', methods=['POST'])
def clear_all():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM tasks")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)