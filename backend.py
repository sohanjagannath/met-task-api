from fastapi import FastAPI
import sqlite3

def connect_db():
    return sqlite3.connect("account.db")

app = FastAPI()


@app.post("/signup")
def signup(username: str, password: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users(username, password, is_login) VALUES (?, ?, ?)", (username, password, 0))
    conn.commit()
    conn.close()
    return {"message": "Signup successful", "username": username}

@app.post("/users/login")
def login(username: str, password: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password, is_login FROM users WHERE username = ?", (username,))
    r_password = cursor.fetchone()

    if r_password and r_password[0] == password and r_password[1] != 1:
        cursor.execute("UPDATE users SET is_login = 1 WHERE username = ?", (username,))
        conn.commit()
        conn.close()
        return {"message": "Login successful"}

    conn.close()
    return {"message": "Invalid username or password"}


@app.post("/users/logout")
def logout(username: str, password: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT is_login FROM users WHERE username=? AND password=?", (username, password))
    user = cursor.fetchone()
    if user:
        if user[0] == 1:
            cursor.execute("UPDATE users SET is_login = 0 WHERE username=? AND password=?", (username, password))
            conn.commit()
            conn.close()
            return "User logged out successfully"
        else:
            return "User is not logged in"
    else:
        return "Invalid username or password"

@app.get("/users/tasks")
def users_tasks(username: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return {"error": "User not found"}

    cursor.execute("SELECT * FROM tasks WHERE user_id = ?", (user[0],))
    data = cursor.fetchall()
    conn.close()
    return data

@app.post("/adding/tasks")
def add_tasks(username: str, title: str, description: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username=?", (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return {"error": "User not found"}

    cursor.execute("INSERT INTO tasks(user_id, title, description) VALUES (?, ?, ?)", (user[0], title, description))
    conn.commit()
    conn.close()
    return {"message": "Task added successfully"}

@app.delete("/delete/users/{username}")
def delete_user(username: str):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted:
        return "User deleted successfully"
    else:
        return "Deletion failed"

@app.delete("/delete/tasks/{id}")
def delete_task(id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted:
        return {"message":"Task deleted successfully"}
    else:
        return {"message":"Task deletion failed"}