from flask import Flask, render_template
from models import *

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/products")
def products():
    return 

@app.route("/product/<int:id>")
def product(id):
    #show one product
    return

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
    # remove product
    return
    
@app.route("/add-product", methods=["GET"])
def add_product_form():
    conn = get_db()
    categories = conn.execute("SELECT * FROM categories").fetchall()
    conn.close()
    return render_template("add_product.html", categories=categories)

@app.route("/add-product", methods=["POST"])
def add_product():
    name = request.form["name"]
    description = request.form["description"]
    price = request.form["price"]
    image = request.form["image"]
    category_id = request.form["category_id"]

    conn = get_db()
    conn.execute("""
        INSERT INTO products (name, description, price, image, category_id)
        VALUES (?, ?, ?, ?, ?)
    """, (name, description, price, image, category_id))
    conn.commit()
    conn.close()

    return redirect(url_for("add_product_form"))