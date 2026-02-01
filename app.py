from flask import Flask, render_template, request, redirect, url_for
from models import *
import os
from werkzeug.utils import secure_filename
app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route("/")
def home():
    categories = get_all_categories()
    return render_template("home.html", categories=categories)

@app.route("/products")
def products():
    return render_template("products.html")

@app.route("/product/<int:id>")
def product(id):
    #show one product
    return render_template("product.html")

@app.route("/cart")
def cart():
    # show cart
    return

@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):
    # add product
    return

@app.route("/remove_from_cart/<int:id>")
def remove_from_cart(id):
    # remove productfrom models import *
    return

@app.route("/add-product", methods=["GET", "POST"])
def add_product_form():
    if request.method == "POST":
        try:
            # Get form data
            name = request.form["name"]
            description = request.form["description"]
            price = float(request.form["price"])  # ensure it's a number
            category_id = int(request.form["category_id"])

            # Handle file upload
            file = request.files["image"]
            if not file or file.filename == "":
                return "No image uploaded", 400

            if not allowed_file(file.filename):
                return "Invalid file type. Only images allowed.", 400

            # Ensure upload folder exists
            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            # Add product to the database
            add_product(name, description, price, filename, category_id)

            return redirect(url_for("add_product_form"))  # redirect after success

        except Exception as e:
            print("Error adding product:", e)
            return f"Error adding product: {e}", 500

    # GET request: show form
    categories = get_all_categories()
    return render_template("add_product.html", categories=categories)

@app.route("/add-category", methods=["GET", "POST"])
def create_category():
    if request.method == "POST":
        name = request.form.get("name", "").strip()  # safe: defaults to empty string
        if name != "":
            add_category(name)
        else:
            return "empty name", 400
        return redirect(url_for("create_category"))
    categories = get_all_categories()
    return render_template("add_category.html", categories=categories)