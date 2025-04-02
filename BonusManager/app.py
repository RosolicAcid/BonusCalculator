from flask import Flask, render_template, request, redirect, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://flask:admin@localhost/employeedb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"

# File Upload Configuration
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

db = SQLAlchemy(app)


# Employee Model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)  # Employee ID
    name = db.Column(db.String(200), nullable=False)  # Employee Name
    joining_date = db.Column(db.Date, nullable=False)  # Joining Date
    address = db.Column(db.Text, nullable=True)  # Address
    image = db.Column(db.String(300), nullable=True)  # Image Path
    designation = db.Column(db.String(100), nullable=False)  # Designation
    department = db.Column(db.String(100), nullable=False)  # Department
    gross_salary = db.Column(db.Float, nullable=False)  # Gross Salary
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Admin Role

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Home / Login Page
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form["user_id"]
        password = request.form["password"]

        user = Employee.query.filter_by(user_id=user_id).first()

        if user and user.check_password(password):
            session["user_id"] = user.user_id
            session["is_admin"] = user.is_admin
            return redirect("/dashboard")
        else:
            flash("Invalid credentials", "error")
            return redirect("login.html")

    return render_template("login.html")


# Logout Route
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# Admin Dashboard (Add Employees)
@app.route("/admin", methods=["GET", "POST"])
def admin_dashboard():
    # if not session.get("is_admin"):
    #     return "Access Denied", 403

    if request.method == "POST":
        user_id = request.form["user_id"]
        name = request.form["name"]
        joining_date = datetime.strptime(request.form["joining_date"], "%Y-%m-%d")
        address = request.form["address"]
        designation = request.form["designation"]
        department = request.form["department"]
        gross_salary = float(request.form["gross_salary"])
        password = request.form["password"]
        is_admin = request.form.get("is_admin") == "on"

        # Image Upload Handling
        image_file = request.files["image"]
        if image_file and image_file.filename:
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_file.filename)
            image_file.save(image_path)
        else:
            image_path = None

        if Employee.query.filter_by(user_id=user_id).first():
            flash("User ID already exists.", "error")
            return redirect("/admin")

        new_employee = Employee(
            user_id=user_id,
            name=name,
            joining_date=joining_date,
            address=address,
            designation=designation,
            department=department,
            gross_salary=gross_salary,
            image=image_path,
            is_admin=is_admin
        )
        new_employee.set_password(password)

        db.session.add(new_employee)
        db.session.commit()

        flash("Employee created successfully!", "success")
        return redirect("/admin")

    return render_template("dashboard.html")


# Employee Dashboard (View All Employees)
@app.route("/dashboard")
def dashboard():
    # if "user_id" not in session:
    #     return redirect("/")

    employees = Employee.query.all()
    return render_template("dashboard.html", employees=employees, is_admin=session.get("is_admin"))


@app.route("/register-admin", methods=["GET", "POST"])
def register_admin():
    """Allows first-time admin registration"""
    existing_admin = Employee.query.filter_by(is_admin=True).first()

    # If an admin already exists, prevent further admin registrations
    if existing_admin:
        flash("Admin already exists. Contact an existing admin to add more users.", "error")
        return redirect("/")

    if request.method == "POST":
        user_id = request.form["user_id"]
        name = request.form["name"]
        joining_date = datetime.strptime(request.form["joining_date"], "%Y-%m-%d")
        address = request.form["address"]
        designation = request.form["designation"]
        department = request.form["department"]
        gross_salary = float(request.form["gross_salary"])
        password = request.form["password"]

        # Image Upload Handling
        image_file = request.files["image"]
        if image_file and image_file.filename:
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_file.filename)
            image_file.save(image_path)
        else:
            image_path = None

        # Create an Admin User
        new_admin = Employee(
            user_id=user_id,
            name=name,
            joining_date=joining_date,
            address=address,
            designation=designation,
            department=department,
            gross_salary=gross_salary,
            image=image_path,
            is_admin=True  # Set as Admin
        )
        new_admin.set_password(password)

        db.session.add(new_admin)
        db.session.commit()

        flash("Admin account created successfully! You can now log in.", "success")
        return redirect("/")

    return render_template("register_admin.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
