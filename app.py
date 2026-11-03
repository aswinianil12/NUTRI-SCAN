from flask import Flask, render_template, request, redirect, session
import csv
import os
import numpy as np
from tensorflow.keras.models import load_model
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.secret_key = "nutriscan"

# model load
model = load_model("model/anemia_model.h5")
nail_model = load_model("model/nail_model.h5")

# upload folder
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- Guidlines ----------------

@app.route("/guidelines")
def guidelines():
    
    return render_template("guidelines.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":                
        username = request.form["username"]
        password = request.form["password"]


        with open("users.csv", "r") as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                if row and row[0] == username and check_password_hash(row[1], password):
                    session["user"] = username
                    session["name"] = row[2]
                    session["age"] = row[3]
                    session["gender"] = row[4]
                    return redirect("/profile")

        return render_template("login.html", error="Invalid Username or Password")

    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        password = generate_password_hash(request.form["password"])

        with open("users.csv", "r") as file:
            reader = csv.reader(file)
            next(reader)

            for row in reader:
                if row and row[0] == username:
                    return render_template("register.html", error="User already exists")

        with open("users.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([username, password, name, age, gender])

        return redirect("/login")

    return render_template("register.html")


# ---------------- INTAKE ----------------
@app.route("/intake")
def intake():

    if "user" not in session:
        return redirect("/login")

    return render_template("intake.html")


# ---------------- PREDICT ----------------
@app.route("/predict", methods=["POST"])
def predict():

    if "user" not in session:
        return redirect("/login")

    file = request.files["image"]

    if file.filename == "":
        return "No file selected ❌"

    filename = secure_filename(file.filename)

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    
    # image verify
    try:
        img = Image.open(filepath).convert("RGB")
        
        img = img.resize((160, 160)) 
    except:
        return "Invalid image file ❌"

    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis=0)

    prediction = model.predict(img)[0][0]
    print("Prediction Value:", prediction)

    # class result 
    if prediction > 0.5:
        result = "Anemia Detected ⚠️"
        suggestion = suggestion = """
        • Eat iron-rich foods (spinach, ragi, dates, beetroot)
        • Include vitamin C (lemon, amla, orange)
        • Avoid tea/coffee immediately after meals
        • Consult a doctor for proper diagnosis
        """
    else:
        result = "Non-Anemic ✅"
        suggestion = "Maintaine Healthy diet with proper iron-rich food."

    return render_template(
    "result.html",
    result=result,
    suggestion=suggestion,
    image_path="uploads/" + filename
    )
@app.route("/predict_nail", methods=["POST"])
def predict_nail():

    if "user" not in session:
        return redirect("/login")

    file = request.files["image"]

    if file.filename == "":
        return "No file selected ❌"

    filename = secure_filename(file.filename)

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Image processing logic
    try:
        img = Image.open(filepath).convert("RGB")
        img = img.resize((160, 160)) # Training size-um ithum match aayirikkanam
    except Exception as e:
        print(f"Error opening image: {e}")
        return "Invalid image file ❌"

    # Preprocessing
    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis=0)

    # Prediction
    prediction = nail_model.predict(img)[0][0]
    print(f"DEBUG: Nail Prediction Value = {prediction}")

    # Result Logic (Based on anemic=0, healthy=1)
    if prediction > 0.1:
        # Lower value indicates the first class (Anemic)
        result = "Koilonychia Detected ⚠️"
        deficiency = "Possible Iron Deficiency"
        suggestion = "Include spinach, dates, beetroot and iron-rich foods. Consult a doctor for a blood test."
    else:
        # Higher value indicates the second class (Healthy)
        result = "Healthy Nail ✅"
        deficiency = "No major nutritional deficiency detected"
        suggestion = "Maintain balanced nutrition and stay hydrated."

    return render_template(
        "result.html",
        result=result,
        deficiency=deficiency,
        suggestion=suggestion,
        image_path="uploads/" + filename
    
    )
# ---------------- profile ---------------
@app.route("/profile")
def profile():

    if "user" not in session:
        return redirect("/login")

    return render_template(
        "profile.html",
        username=session["user"],
        name=session["name"],
        age=session["age"],
        gender=session["gender"]
    )
# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)