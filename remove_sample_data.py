from models import *

def remove_sample_data():
    sample_products = [
        "RTX 4070 Ti",
        "RTX 4060",
        "Intel i7-13700K",
        "AMD Ryzen 7 7800X3D",
        "Corsair Vengeance 32GB DDR5"
    ]

    for product_name in sample_products:
        try:
            db = get_db()
            product = db.execute("SELECT id FROM products WHERE name = ?", (product_name,)).fetchone()
            if product:
                remove_product(product['id'])
                print(f"Removed product: {product_name}")
            else:
                print(f"Product not found: {product_name}")
            db.close()
        except Exception as e:
            print(f"Error removing product {product_name}: {e}")

    sample_categories = [
        "Videókártyák",
        "Processzorok",
        "Memóriák"
    ]

    for category_name in sample_categories:
        try:
            db = get_db()
            product_count = db.execute("SELECT COUNT(*) FROM products WHERE category_id = (SELECT id FROM categories WHERE name = ?)", (category_name,)).fetchone()[0]

            if product_count == 0:
                category = db.execute("SELECT id FROM categories WHERE name = ?", (category_name,)).fetchone()
                if category:
                    remove_category(category['id'])
                    print(f"Removed category: {category_name}")
                else:
                    print(f"Category not found: {category_name}")
            else:
                print(f"Category {category_name} has {product_count} products, skipping removal")
            db.close()
        except Exception as e:
            print(f"Error removing category {category_name}: {e}")

    print("Sample data removal completed!")

if __name__ == "__main__":
    remove_sample_data()