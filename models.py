import sqlite3
import hashlib

DB_NAME = "database.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
def get_all_products():
    db = get_db()
    products = db.execute("""
        SELECT products.id, products.name, products.description, products.price, products.image, products.quantity, categories.name as category
        FROM products
        JOIN categories ON products.category_id = categories.id
    """).fetchall()
    db.close()
    return products

def get_product(product_id):
    db = get_db()
    product = db.execute("""
        SELECT products.id, products.name, products.description, products.price, products.image, products.quantity, categories.name as category
        FROM products
        JOIN categories ON products.category_id = categories.id
        WHERE products.id = ?
    """, (product_id,)).fetchone()
    db.close()
    return product

def add_product(name, description, price, image, category_id, quantity):
    try:
        db = get_db()
        db.execute(
            "INSERT INTO products (name, description, price, image, category_id, quantity) VALUES (?, ?, ?, ?, ?, ?)",
            (name, description, price, image, category_id, quantity)
        )
        db.commit()
    except Exception as e:
        print("Error inserting product:", e)
        raise 
    finally:
        db.close()
def remove_product(product_id):
    db = get_db()
    db.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit()
    db.close()

def update_product_quantity(product_id, quantity):
    db = get_db()
    db.execute("UPDATE products SET quantity = ? WHERE id = ?", (quantity, product_id))
    db.commit()
    db.close()

def get_cart_items():
    from flask import session
    cart = session.get('cart', {})
    db = get_db()
    db.row_factory = sqlite3.Row
    
    items = []
    for product_id, quantity in cart.items():
        product = db.execute("""
            SELECT
                products.id AS product_id,
                products.name,
                products.price,
                products.image
            FROM products
            WHERE products.id = ?
        """, (product_id,)).fetchone()
        
        if product:
            items.append({
                'product_id': product['product_id'],
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'quantity': quantity
            })
    
    db.close()
    return items

def get_cart_product_count():
    from flask import session
    cart = session.get('cart', {})
    return sum(cart.values())


def add_to_cart(product_id):
    from flask import session
    if 'cart' not in session:
        session['cart'] = {}
    
    # Check available stock
    product = get_product(product_id)
    if not product:
        return False  # Product doesn't exist
    
    current_quantity_in_cart = session['cart'].get(str(product_id), 0)
    if current_quantity_in_cart >= product['quantity']:
        return False  # Not enough stock
    
    if str(product_id) in session['cart']:
        session['cart'][str(product_id)] += 1
    else:
        session['cart'][str(product_id)] = 1
    
    session.modified = True
    return True


def increase_cart_quantity(product_id):
    from flask import session
    if 'cart' not in session or str(product_id) not in session['cart']:
        return False
    
    # Check available stock
    product = get_product(product_id)
    if not product:
        return False
    
    current_quantity_in_cart = session['cart'][str(product_id)]
    if current_quantity_in_cart >= product['quantity']:
        return False  # Not enough stock
    
    session['cart'][str(product_id)] += 1
    session.modified = True
    return True


def decrease_cart_quantity(product_id):
    from flask import session
    if 'cart' not in session or str(product_id) not in session['cart']:
        return False
    
    if session['cart'][str(product_id)] > 1:
        session['cart'][str(product_id)] -= 1
        session.modified = True
        return True
    else:
        # If quantity would be 0, remove the item entirely
        del session['cart'][str(product_id)]
        session.modified = True
        return True
    
    return False


def remove_from_cart(product_id):
    from flask import session
    if 'cart' in session and str(product_id) in session['cart']:
        del session['cart'][str(product_id)]
        session.modified = True



def get_all_categories():
    db = get_db()
    categories = db.execute("SELECT * FROM categories").fetchall()
    db.close()
    return categories

def get_category(category_id):
    db = get_db()
    category = db.execute("SELECT * FROM categories WHERE id = ?", (category_id,)).fetchone()
    db.close()
    return category

def add_category(name, image):
    try:
        db = get_db()
        db.execute(
            "INSERT INTO categories (name, image) VALUES (?, ?)",
            (name, image)
        )
        db.commit()
    except Exception as e:
        print("Error inserting product:", e)
        raise 
    finally:
        db.close()
    
def remove_category(category_id):
    db = get_db()
    db.execute("DELETE FROM products WHERE category_id = ?", (category_id,))
    db.execute("DELETE FROM categories WHERE id = ?", (category_id,))
    db.commit()
    db.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, is_admin=False):
    db = get_db()
    db.execute(
        "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
        (username, hash_password(password), is_admin)
    )
    db.commit()
    db.close()

def authenticate_user(username, password):
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, hash_password(password))
    ).fetchone()
    db.close()
    return user

def get_user_by_username(username):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    db.close()
    return user