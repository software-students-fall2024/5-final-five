import os
import subprocess
from flask import Flask, render_template, request, flash, redirect, send_file, url_for, session
from pymongo import MongoClient
from resume import resume_bp

def create_app():
    # app initialization
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")

    # database initialization
    client = MongoClient("mongodb://mongodb:27017/")
    db = client["resume_db"]
    users_collection = db["users"] # STORED W/ EMAIL AND PASSWORD
    resumes_collection = db["resumes"] # STORED W/ USER IT WAS MADE BY, NAME OF RESUME, AND THE PDF ITSELF

    # get home page
    @app.route("/")
    def home():
        if "email" in session:
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('login'))

    # get login page
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]

            user = users_collection.find_one({"email": email, "password": password})
            if user:
                session["email"] = email
                flash("Login successful.", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid email or password. Please try again.", "danger")
        return render_template("login.html")

    # get register page
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]

            if users_collection.find_one({"email": email}):
                flash("Email already registered. Choose a different one.", "danger")
            else:
                users_collection.insert_one({"email": email, "password": password})
                flash("Registration successful. You can now log in.", "success")
                return redirect(url_for("login"))

        return render_template("register.html")

    @app.route("/dashboard")
    def dashboard():
        if "email" in session:
            email = session["email"]
            resumes = resumes_collection.find({"email": email})
            return render_template("dashboard.html", email=email, resumes=resumes)
        else:
            flash("You must be logged in to access this.", "danger")
            return redirect(url_for("login"))

    @app.route("/generate_resume")
    def generate_resume():
        if "email" in session:
            email = session["email"]
            resumes = resumes_collection.find({"email": email})
            return render_template("generate_resume.html", email=email, resumes=resumes)
        else:
            flash("You must be logged in to access this.", "danger")
            return redirect(url_for("login"))

    @app.route("/logout")
    def logout():
        session.pop("email", None)
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))

    app.register_blueprint(resume_bp)

    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5002, debug=True)
