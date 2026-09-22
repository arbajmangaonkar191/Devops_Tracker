from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = "tasks.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


# Get all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():

    conn = get_db()

    tasks = conn.execute(
        "SELECT * FROM tasks"
    ).fetchall()

    conn.close()

    return jsonify([
        {
            "id": task["id"],
            "title": task["title"],
            "completed": bool(task["completed"])
        }
        for task in tasks
    ])


# Create a new task
@app.route("/tasks", methods=["POST"])
def create_task():

    data = request.get_json()

    title = data.get("title")

    if not title:
        return jsonify({"error": "Task title is required"}), 400

    conn = get_db()

    cursor = conn.execute(
        "INSERT INTO tasks (title) VALUES (?)",
        (title,)
    )

    conn.commit()

    task_id = cursor.lastrowid

    conn.close()

    return jsonify({
        "id": task_id,
        "title": title,
        "completed": False
    }), 201


# Mark task as completed
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):

    conn = get_db()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if not task:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    new_status = 0 if task["completed"] else 1

    conn.execute(
        "UPDATE tasks SET completed = ? WHERE id = ?",
        (new_status, task_id)
    )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Task updated successfully"
    })


# Delete task
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):

    conn = get_db()

    cursor = conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    conn.commit()

    deleted = cursor.rowcount

    conn.close()

    if deleted == 0:
        return jsonify({"error": "Task not found"}), 404

    return jsonify({
        "message": "Task deleted successfully"
    })


if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
