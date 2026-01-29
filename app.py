from flask import Flask, render_template

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

@app.route("/admin/add", methods=["GET", "POST"])
def add_product():
    # add new product
    return

@app.route("/admin/remove", methods=["GET", "POST"])
def remove_product():
    # remove product
    return