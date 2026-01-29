import sqlite3

DB_NAME = "database.db"

def get_db():
    return sqlite3.connect(DB_NAME)

def get_all_products():
    db = get_db()
    products = db.execute("SELECT * FROM products").fetchall()
    db.close()
    return products

def get_product(product_id):
    db = get_db()
    product = db.execute(
        "SELECT * FROM products WHERE id = ?",
        (product_id,)
    ).fetchone()
    db.close()
    return product

def add_product(name, description, price, image):
    db = get_db()
    db.execute(
        "INSERT INTO products (name, description, price, image) VALUES (?, ?, ?, ?)",
        (name, description, price, image)
    )
    db.commit()
    db.close()

def remove_product(product_id):
    db = get_db()
    db.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit()
    db.close()

def add_to_cart(product_id):
    db = get_db()

    item = db.execute(
        "SELECT * FROM cart WHERE product_id = ?",
        (product_id,)
    ).fetchone()

    if item:
        db.execute(
            "UPDATE cart SET quantity = quantity + 1 WHERE product_id = ?",
            (product_id,)
        )
    else:
        db.execute(
            "INSERT INTO cart (product_id, quantity) VALUES (?, 1)",
            (product_id,)
        )

    db.commit()
    db.close()

def remove_from_cart(product_id):
    db = get_db()
    db.execute("DELETE FROM cart WHERE product_id = ?", (product_id,))
    db.commit()
    db.close()

def get_cart():
    db = get_db()
    items = db.execute("""
        SELECT products.id, products.name, products.price, cart.quantity
        FROM cart
        JOIN products ON cart.product_id = products.id
    """).fetchall()
    db.close()
    return items

def clear_cart():
    db = get_db()
    db.execute("DELETE FROM cart")
    db.commit()
    db.close()



