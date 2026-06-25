import os
import psycopg2
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ['DB_HOST'],
        database=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD']
    )
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN DEFAULT FALSE
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route('/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, title, done FROM tasks ORDER BY id;')
    rows = cur.fetchall()
    cur.close()
    conn.close()
    tasks = [{'id': r[0], 'title': r[1], 'done': r[2]} for r in rows]
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    title = data['title']
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO tasks (title) VALUES (%s) RETURNING id;', (title,))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'id': new_id, 'title': title, 'done': False}), 201

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id FROM tasks WHERE id = %s;', (task_id,))
    if cur.fetchone() is None:
        cur.close()
        conn.close()
        return jsonify({'error': 'Task not found'}), 404
    title = data.get('title')
    done = data.get('done')
    if title is not None:
        cur.execute('UPDATE tasks SET title = %s WHERE id = %s;', (title, task_id))
    if done is not None:
        cur.execute('UPDATE tasks SET done = %s WHERE id = %s;', (done, task_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Task updated'}), 200

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM tasks WHERE id = %s;', (task_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({'message': 'Task deleted'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)