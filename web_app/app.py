import base64
import os
import subprocess
from flask import Flask, render_template, request, flash, redirect, send_file, url_for, session, jsonify
from pymongo import MongoClient
from resume import resume_bp

def create_app():
    # app initialization
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY")
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client["resume_db"]
    users_collection = db["users"] # STORES W/ EMAIL AND PASSWORD
    resumes_collection = db["resumes"] # STORES W/ USER IT WAS MADE BY, NAME OF RESUME, AND THE PDF ITSELF

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

    # get user's dashboard
    # finds resumes made under the email of current session user and returns all of them
    @app.route("/dashboard")
    def dashboard():
        if "email" in session:
            email = session["email"]
            resumes = resumes_collection.find({"email": email})
            return render_template("dashboard.html", email=email, resumes=resumes)
        else:
            flash("You must be logged in to access this.", "danger")
            return redirect(url_for("login"))

    # get generate resume page, use commented out code instead once registration/login is working
    @app.route("/generate-resume")
    def generate_resume():
        if "email" in session:
            email = session["email"]
            resumes = resumes_collection.find({"email": email})
            return render_template("generate-resume.html", email=email, resumes=resumes)
        else:
            flash("You must be logged in to access this.", "danger")
            return redirect(url_for("login"))

    # saves resume to the database
    @app.route("/save_resume", methods=["POST"])
    def save_resume():
        if "email" not in session:
            flash("You must be logged in to save a resume.", "danger")
            return redirect(url_for("login"))
        
        try:
            resume_data = request.json
            print("Received resume data:", resume_data)  # Debugging: print the received data
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            return jsonify({"error": "Invalid JSON in request"}), 400
        
        email = session["email"]
        resume_title = resume_data.get("name")
        pdf_base64 = resume_data.get("pdf")

        if not pdf_base64:
            return jsonify({"error": "PDF data is missing"}), 400
        
        # Check if the base64 string includes the "data:" prefix and split it
        if pdf_base64.startswith('data:application/pdf;base64,'):
            pdf_base64 = pdf_base64.split(",")[1]
        else:
            print("PDF data format is incorrect")
            return jsonify({"error": "Invalid PDF data format"}), 400

        try:
            # Decode the base64 PDF data
            pdf_data = base64.b64decode(pdf_base64)
        except Exception as e:
            print(f"Error decoding PDF: {e}")
            return jsonify({"error": "Error decoding PDF data"}), 500

        # Save the resume to the database
        resume = {
            "email": email,
            "name": resume_title,
            "pdf": pdf_data
        }
        resumes_collection.insert_one(resume)

        # Return a success response
        return jsonify({"message": "Resume saved successfully!"})


    @app.route("/logout")
    def logout():
        session.pop("email", None)
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))

    app.register_blueprint(resume_bp)

    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=8080, debug=True)
