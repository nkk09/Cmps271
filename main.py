from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import sqlite3
from datetime import datetime
import secrets
import string
import bcrypt

DB_PATH = "aub_reviews.db"
app = FastAPI(title="AUB Course Reviews")

# -----------------------
# Password generator & hashing
# -----------------------
def generate_password(length=10):
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for i in range(length))

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# -----------------------
# Database connection
# -----------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# -----------------------
# Models
# -----------------------
class User(BaseModel):
    name: str
    email: EmailStr
    role: str  # "student" or "professor"

class Review(BaseModel):
    user_id: int
    course_id: int
    rating: int
    comment: str

# -----------------------
# Bad word filter
# -----------------------
BAD_WORDS = ["badword1", "badword2", "badword3"]

def contains_bad_word(text: str):
    text_lower = text.lower()
    for word in BAD_WORDS:
        if word in text_lower:
            return True
    return False

# -----------------------
# Seed test data if empty
# -----------------------
def seed_data():
    conn = get_db_connection()

    # Professors
    if not conn.execute("SELECT * FROM professors").fetchone():
        conn.execute("INSERT INTO professors (name, email, department) VALUES (?, ?, ?)", 
                     ("Dr. Alice", "alice@aub.edu.lb", "CS"))
        conn.execute("INSERT INTO professors (name, email, department) VALUES (?, ?, ?)", 
                     ("Dr. Bob", "bob@aub.edu.lb", "Math"))

    # Users
    if not conn.execute("SELECT * FROM users").fetchone():
        for name, email, role in [("Jad Zein", "jad@mail.aub.edu", "student"),
                                  ("Lara Abi", "lara@mail.aub.edu", "student")]:
            raw_password = generate_password()
            hashed_password = hash_password(raw_password)
            conn.execute("INSERT INTO users (name, email, role, password) VALUES (?, ?, ?, ?)",
                         (name, email, role, hashed_password))
            print(f"{role.capitalize()} {name} password: {raw_password}")

    # Courses
    if not conn.execute("SELECT * FROM courses").fetchone():
        conn.execute("INSERT INTO courses (course_code, course_name, department, credits, professor) VALUES (?, ?, ?, ?, ?)",
                     ("CS101", "Intro to CS", "CS", 3, "Dr. Alice"))
        conn.execute("INSERT INTO courses (course_code, course_name, department, credits, professor) VALUES (?, ?, ?, ?, ?)",
                     ("MATH201", "Calculus II", "Math", 3, "Dr. Bob"))

    conn.commit()
    conn.close()

seed_data()

# -----------------------
# Endpoints
# -----------------------

# Users endpoint with password generation
@app.post("/users")
def create_user(user: User):
    # Email validation
    if user.role == "student" and not user.email.endswith("@mail.aub.edu"):
        raise HTTPException(status_code=400, detail="Student email must end with @mail.aub.edu")
    if user.role == "professor" and not user.email.endswith("@aub.edu.lb"):
        raise HTTPException(status_code=400, detail="Professor email must end with @aub.edu.lb")
    
    # Generate password
    raw_password = generate_password()
    hashed_password = hash_password(raw_password)
    
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO users (name, email, role, password) VALUES (?, ?, ?, ?)",
        (user.name, user.email, user.role, hashed_password)
    )
    conn.commit()
    conn.close()

    return {"message": "User created successfully", "password": raw_password}

# List courses
@app.get("/courses")
def list_courses():
    conn = get_db_connection()
    courses = conn.execute("SELECT * FROM courses").fetchall()
    conn.close()
    return [dict(c) for c in courses]

# -----------------------
# Endpoints for reviews (anonymous)
# -----------------------
@app.get("/reviews")
def list_reviews():
    conn = get_db_connection()
    # Only return course_id, rating, comment, created_at
    reviews = conn.execute("""
        SELECT course_id, rating, comment, created_at 
        FROM reviews
        ORDER BY created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in reviews]

@app.post("/reviews")
def submit_review(review: Review):
    if review.rating < 1 or review.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    if contains_bad_word(review.comment):
        raise HTTPException(status_code=400, detail="Comment contains inappropriate language")

    conn = get_db_connection()
    # Check if user exists (still needed for backend spam checks)
    user = conn.execute("SELECT * FROM users WHERE id = ?", (review.user_id,)).fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    # Check if course exists
    course = conn.execute("SELECT * FROM courses WHERE id = ?", (review.course_id,)).fetchone()
    if not course:
        conn.close()
        raise HTTPException(status_code=404, detail="Course not found")

    # Insert review but don't expose user_id
    conn.execute(
        "INSERT INTO reviews (user_id, course_id, rating, comment, created_at) VALUES (?, ?, ?, ?, ?)",
        (review.user_id, review.course_id, review.rating, review.comment, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return {"message": "Review submitted successfully"}


# Professors’ courses
@app.get("/professors/{professor_id}/courses")
def professor_courses(professor_id: int):
    conn = get_db_connection()
    professor = conn.execute("SELECT * FROM professors WHERE id = ?", (professor_id,)).fetchone()
    if not professor:
        conn.close()
        raise HTTPException(status_code=404, detail="Professor not found")

    courses = conn.execute("SELECT * FROM courses WHERE professor = ?", (professor["name"],)).fetchall()
    conn.close()
    return [dict(c) for c in courses]
