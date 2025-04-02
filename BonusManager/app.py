from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    user_id = request.form["user_id"]
    password = request.form["password"]
    # Add authentication logic here
    return f"User ID: {user_id}, Password: {password}"  # Placeholder response

if __name__ == "__main__":
    app.run(debug=True)
