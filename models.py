import sqlite3

DB_NAME = "database.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
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
        raise 
    finally:
        db.close()
def remove_product(product_id):
    db = get_db()
    db.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit()
    db.close()
# Cart (using sessions)
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
    
    if str(product_id) in session['cart']:
        session['cart'][str(product_id)] += 1
    else:
        session['cart'][str(product_id)] = 1
    
    session.modified = True


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