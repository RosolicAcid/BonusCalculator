from flask import Flask, render_template, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://myuser:mypassword@localhost/employeedb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "your_secret_key"

db = SQLAlchemy(app)


# Employee Model
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Route to Show Login Page
@app.route("/")
def login_page():
    return render_template("login.html")


# Route to Handle Login
@app.route("/login", methods=["POST"])
def login():
    user_id = request.form["user_id"]
    password = request.form["password"]

    user = Employee.query.filter_by(user_id=user_id).first()

    if user and user.check_password(password):
        return "Login Successful!"
    else:
        flash("Invalid credentials, please try again.", "error")
        return redirect("/")


# Route to Register a New Employee (For Testing)
@app.route("/register", methods=["POST"])
def register():
    user_id = request.form["user_id"]
    password = request.form["password"]

    if Employee.query.filter_by(user_id=user_id).first():
        flash("User ID already exists.", "error")
        return redirect("/")

    new_employee = Employee(user_id=user_id)
    new_employee.set_password(password)

    db.session.add(new_employee)
    db.session.commit()

    flash("Registration Successful! You can now log in.", "success")
    return redirect("/")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables
    app.run(debug=True)
