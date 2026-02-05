from flask import Flask, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

# -----------------------
# Database Connection
# -----------------------
def get_db():
    return sqlite3.connect("users.db", timeout=30)

# -----------------------
# Create Table
# -----------------------
conn = get_db()
conn.execute("PRAGMA journal_mode=WAL")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT,
 phone TEXT,
 email TEXT UNIQUE,
 address TEXT,
 dob TEXT,
 gender TEXT,
 father_name TEXT,
 father_phone TEXT,
 mother_name TEXT,
 mother_phone TEXT,
 password TEXT,
 role TEXT
)
""")

conn.commit()
conn.close()

# -----------------------
# Create Default Admin
# -----------------------
conn = get_db()
cur = conn.cursor()

cur.execute("SELECT * FROM users WHERE email=?", ("admin@pccoepune.org",))
if cur.fetchone() is None:
    cur.execute("""
    INSERT INTO users
    (name,phone,email,address,dob,gender,
     father_name,father_phone,mother_name,mother_phone,
     password,role)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
    """,(
        "Admin",
        "0000000000",
        "admin@pccoepune.org",
        "India",
        "",
        "Male",
        "",
        "",
        "",
        "",
        "admin123",
        "ADMIN"
    ))

conn.commit()
conn.close()

# -----------------------
# Register
# -----------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE email=?", (data["email"],))
    if cur.fetchone():
        conn.close()
        return {"message": "Email already exists"}

    cur.execute("""
    INSERT INTO users
    (name,phone,email,address,dob,gender,
     father_name,father_phone,mother_name,mother_phone,
     password,role)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
    """,(
        data["name"],
        data["phone"],
        data["email"],
        data["address"],
        data["dob"],
        data["gender"],
        data["father_name"],
        data["father_phone"],
        data["mother_name"],
        data["mother_phone"],
        data["password"],   # 👈 user password
        "USER"
    ))

    conn.commit()
    conn.close()

    return {"message": "Registration Successful"}

# -----------------------
# Login
# -----------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT password, role FROM users WHERE email=?", (data["email"],))
    user = cur.fetchone()
    conn.close()

    if user and user[0] == data["password"]:
        return {"status": "success", "role": user[1]}
    else:
        return {"status": "fail"}

# -----------------------
# Get User
# -----------------------
@app.route("/get-user", methods=["POST"])
def get_user():
    data = request.get_json()

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    SELECT name,phone,email,address,dob,gender,
           father_name,father_phone,
           mother_name,mother_phone
    FROM users WHERE email=?
    """, (data["email"],))

    user = cur.fetchone()
    conn.close()

    if user is None:
        return {"message": "User not found"}

    return {
        "name": user[0],
        "phone": user[1],
        "email": user[2],
        "address": user[3],
        "dob": user[4],
        "gender": user[5],
        "father_name": user[6],
        "father_phone": user[7],
        "mother_name": user[8],
        "mother_phone": user[9]
    }

# -----------------------
# Run Server
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)
