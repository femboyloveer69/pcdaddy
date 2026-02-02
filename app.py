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
    products = get_all_products()
    categories = get_all_categories()
    return render_template("products.html", categories = categories, products = products)

@app.route("/product/<int:id>")
def product(id):
    product = get_product(id)
    return render_template("product.html", product = product)

@app.route("/cart")
def cart():
    return

@app.route("/add_to_cart/<int:id>")
def add_to_cart(id):
    return

@app.route("/remove_from_cart/<int:id>")
def remove_from_cart(id):
    return

@app.route("/add-product", methods=["GET", "POST"])
def add_product_form():
    if request.method == "POST":
        try:
            name = request.form["name"]
            description = request.form["description"]
            price = float(request.form["price"]) 
            category_id = int(request.form["category_id"])

            file = request.files["image"]
            if not file or file.filename == "":
                return "No image uploaded", 400

            if not allowed_file(file.filename):
                return "Invalid file type. Only images allowed.", 400

            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            add_product(name, description, price, filename, category_id)

            return redirect(url_for("add_product_form"))

        except Exception as e:
            print("Error adding product:", e)
            return f"Error adding product: {e}", 500

    categories = get_all_categories()
    return render_template("add_product.html", categories=categories)

@app.route("/add-category", methods=["GET", "POST"])
def add_category_form():
    if request.method == "POST":
        try:
            name = request.form["name"]
            file = request.files["image"]
            if not file or file.filename == "":
                return "No image uploaded", 400

            if not allowed_file(file.filename):
                return "Invalid file type. Only images allowed.", 400

            os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(filepath)

            add_category(name, filename)

            return redirect(url_for("add_product_form"))

        except Exception as e:
            print("Error adding product:", e)
            return f"Error adding product: {e}", 500

    categories = get_all_categories()
    return render_template("add_product.html", categories=categories)
