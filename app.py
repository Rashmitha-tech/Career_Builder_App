from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json, os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
app.config["SECRET_KEY"] = "career-builder-secret"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

USERS_FILE = "users.json"
PROGRESS_FILE = "progress.json"

# ----------------- CAREER DATA -----------------
CAREER_ROADMAPS = {
    "web_dev": {
        "title": "Web Developer",
        "skills": ["HTML", "CSS", "JavaScript", "React", "Flask"]
    },
    "data_science": {
        "title": "Data Scientist",
        "skills": ["Python", "Statistics", "Machine Learning", "Pandas"]
    }
}

# ----------------- USER CLASS -----------------
class User(UserMixin):
    def __init__(self, id, email, name):
        self.id = id
        self.email = email
        self.name = name

# ----------------- FILE HELPERS -----------------
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2)

# ---------------- EMAIL FUNCTION ----------------
def send_welcome_email(user_email, user_name):
    try:
        sender_email = "careerbuilder629@gmail.com"
        sender_password = "cmfc qcwj lyrl bpio"   # paste Gmail App Password here

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = user_email
        msg["Subject"] = "Welcome to Career Path Builder 🎉"

        body = f"""
Hi {user_name},

Your Career Path Builder account has been created successfully.

Start exploring careers, skills, and learning roadmaps today!

Best wishes,
Career Path Builder Team
"""
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        print("Email error:", e)
        return False

# ---------------- LOGIN LOADER ----------------
@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    if user_id in users:
        u = users[user_id]
        return User(user_id, u["email"], u["name"])
    return None

# ---------------- ROUTES ----------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"].lower()
        password = request.form["password"]

        users = load_users()

        for u in users.values():
            if u["email"] == email:
                flash("Email already registered", "error")
                return redirect(url_for("register"))

        uid = str(len(users) + 1)
        users[uid] = {
            "name": name,
            "email": email,
            "password": generate_password_hash(password),
            "created_at": datetime.now().isoformat()
        }
        save_users(users)

        send_welcome_email(email, name)

        flash("Registration successful! Check your email 📧", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower()
        password = request.form["password"]

        users = load_users()
        for uid, u in users.items():
            if u["email"] == email and check_password_hash(u["password"], password):
                login_user(User(uid, u["email"], u["name"]))
                return redirect(url_for("dashboard"))

        flash("Invalid login", "error")

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    progress = load_progress().get(current_user.id, {})
    return render_template("dashboard.html", careers=CAREER_ROADMAPS, progress=progress)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
