from flask import Flask, render_template, request, redirect, url_for, flash
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import psycopg2
import psycopg2.extras

app = Flask(__name__)
app.secret_key = "your_secret_key"
CORS(app)
bcrypt = Bcrypt(app)

# Database connection
def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="tution_db",
        user="postgres",
        password="123456789"
    )
    return conn

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
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and bcrypt.check_password_hash(user["password_hash"], password):
            flash(f"Welcome, {username}!", "success")
            return redirect(url_for("index"))
        else:
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
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", 
                    (username, hashed_password))
        conn.commit()
        cur.close()
        conn.close()

        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# Courses page
@app.route("/courses")
def courses():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM courses")
    courses = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("courses.html", courses=courses)

if __name__ == "__main__":
    app.run(debug=True)

