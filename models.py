import sqlite3

DB_NAME = "database.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # ✅ enables category["name"]
    return conn

# ----------------- Products -----------------
def get_all_products():
    db = get_db()
    products = db.execute("""
        SELECT products.id, products.name, products.description, products.price, products.image, categories.name as category
        FROM products
        JOIN categories ON products.category_id = categories.id
    """).fetchall()
    db.close()
    return products

def get_product(product_id):
    db = get_db()
    product = db.execute("""
        SELECT products.id, products.name, products.description, products.price, products.image, categories.name as category
        FROM products
        JOIN categories ON products.category_id = categories.id
        WHERE products.id = ?
    """, (product_id,)).fetchone()
    db.close()
    return product

def add_product(name, description, price, image, category_id):
    try:
        db = get_db()
        db.execute(
            "INSERT INTO products (name, description, price, image, category_id) VALUES (?, ?, ?, ?, ?)",
            (name, description, price, image, category_id)
        )
        db.commit()
    except Exception as e:
        print("Error inserting product:", e)
        raise  # re-raise to catch in route if needed
    finally:
        db.close()
def remove_product(product_id):
    db = get_db()
    db.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit()
    db.close()

# ----------------- Cart -----------------
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
        SELECT products.id, products.name, products.price, products.image, categories.name as category, cart.quantity
        FROM cart
        JOIN products ON cart.product_id = products.id
        JOIN categories ON products.category_id = categories.id
    """).fetchall()
    db.close()
    return items

def clear_cart():
    db = get_db()
    db.execute("DELETE FROM cart")
    db.commit()
    db.close()

# ----------------- Categories -----------------
def get_all_categories():
    db = get_db()
    categories = db.execute("SELECT * FROM categories").fetchall()
    db.close()
    return categories

def add_category(name):
    try:
        db = get_db()
        db.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        db.commit()
        db.close()
        return True
    except sqlite3.IntegrityError:
        # Category already exists
        db.close()
        return False
    
def remove_category(category_id):
    db = get_db()
    # Optional: remove all products in that category first
    db.execute("DELETE FROM products WHERE category_id = ?", (category_id,))
    # Then remove the category itself
    db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    db.commit()
    db.close()