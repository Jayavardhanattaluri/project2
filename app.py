from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
app.secret_key = "your_secret_key"
CORS(app)
bcrypt = Bcrypt(app)


# Database connection
# Returns None if the database is unavailable so routes can gracefully fallback.
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="tution_db",
            user="postgres",
            password="ABCD!@#$",
        )
        return conn
    except psycopg2.Error:
        return None


DEFAULT_COURSES = [
    {
        "title": "Python for Everybody",
        "description": "Start from scratch and build a strong Python programming foundation.",
        "image_url": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=1200&q=80",
        "instructor": "Dr. Angela Kim",
        "rating": "4.8",
        "students": "102,341",
        "duration": "24 hours",
        "level": "Beginner",
        "category": "Programming",
    },
    {
        "title": "Data Structures in C++",
        "description": "Master arrays, linked lists, trees, and graph fundamentals for interviews.",
        "image_url": "https://images.unsplash.com/photo-1517180102446-f3ece451e9d8?auto=format&fit=crop&w=1200&q=80",
        "instructor": "Prof. Martin Lee",
        "rating": "4.7",
        "students": "71,230",
        "duration": "31 hours",
        "level": "Intermediate",
        "category": "Computer Science",
    },
    {
        "title": "Computer Networks Essentials",
        "description": "Understand networking layers, routing, TCP/IP, and modern cloud networking.",
        "image_url": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=1200&q=80",
        "instructor": "Nadia Alvi",
        "rating": "4.6",
        "students": "43,902",
        "duration": "18 hours",
        "level": "Intermediate",
        "category": "Computer Science",
    },
    {
        "title": "CS50-Style Intro to Computer Science",
        "description": "A broad intro to algorithms, abstraction, memory, and software engineering.",
        "image_url": "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?auto=format&fit=crop&w=1200&q=80",
        "instructor": "Sarah Donovan",
        "rating": "4.9",
        "students": "190,445",
        "duration": "40 hours",
        "level": "Beginner",
        "category": "Computer Science",
    },
    {
        "title": "Operating Systems Fundamentals",
        "description": "Processes, threads, scheduling, virtual memory, and file systems made practical.",
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
        "instructor": "David Cho",
        "rating": "4.7",
        "students": "56,084",
        "duration": "26 hours",
        "level": "Advanced",
        "category": "Computer Science",
    },
    {
        "title": "Algorithms for Coding Interviews",
        "description": "Practice sorting, searching, dynamic programming, and graph techniques.",
        "image_url": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=1200&q=80",
        "instructor": "Neha Arora",
        "rating": "4.8",
        "students": "88,902",
        "duration": "29 hours",
        "level": "Intermediate",
        "category": "Computer Science",
    },
    {
        "title": "Algorithms for Coding Interviews",
        "description": "A second learning track with fresh practice sets and timed mock assessments.",
        "image_url": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=1200&q=80",
        "instructor": "Neha Arora",
        "rating": "4.8",
        "students": "41,335",
        "duration": "22 hours",
        "level": "Intermediate",
        "category": "Computer Science",
    },
    {
        "title": "Machine Learning Foundations",
        "description": "Learn supervised learning, model evaluation, and practical ML workflows.",
        "image_url": "https://images.unsplash.com/photo-1527474305487-b87b222841cc?auto=format&fit=crop&w=1200&q=80",
        "instructor": "Dr. Hina Patel",
        "rating": "4.7",
        "students": "79,112",
        "duration": "34 hours",
        "level": "Intermediate",
        "category": "Data Science",
    },
]


# Home page
@app.route("/")
def index():
    return render_template("index.html")


# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("login"))

        conn = get_db_connection()
        if conn is None:
            flash("Login service is temporarily unavailable. Please try again later.", "danger")
            return redirect(url_for("login"))

        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and bcrypt.check_password_hash(user["password_hash"], password):
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("index"))

        flash("Invalid username or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


# Registration route
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        conn = get_db_connection()
        if conn is None:
            flash("Registration service is temporarily unavailable. Please try again later.", "danger")
            return redirect(url_for("register"))

        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, hashed_password),
            )
            conn.commit()
        except psycopg2.Error:
            conn.rollback()
            flash("Could not create account. The username may already exist.", "danger")
            return redirect(url_for("register"))
        finally:
            cur.close()
            conn.close()

        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


# Courses page
@app.route("/courses")
def courses():
    courses_data = []
    conn = get_db_connection()

    if conn is not None:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute(
                """
                SELECT title, description, image_url, instructor, rating, students, duration, level, category
                FROM courses
                ORDER BY id
                """
            )
            courses_data = [dict(row) for row in cur.fetchall()]
        except psycopg2.Error:
            courses_data = []
        finally:
            cur.close()
            conn.close()

    if not courses_data:
        courses_data = DEFAULT_COURSES

    return render_template("courses.html", courses=courses_data)


if __name__ == "__main__":
    app.run(debug=True)
