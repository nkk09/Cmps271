import sqlite3

DB_PATH = "aub_reviews.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create courses table
cursor.execute("""
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_code TEXT,
    course_name TEXT,
    department TEXT,
    credits INTEGER,
    professor TEXT
)
""")

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    role TEXT
)
""")

# Create professors table
cursor.execute("""
CREATE TABLE IF NOT EXISTS professors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    department TEXT
)
""")

# Create reviews table
cursor.execute("""
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    course_id INTEGER,
    rating INTEGER,
    comment TEXT,
    created_at TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(course_id) REFERENCES courses(id)
)
""")

conn.commit()
conn.close()

print("All tables created successfully!")
