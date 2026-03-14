from models import create_user, add_product, add_category

try:
    create_user("admin", "admin123", is_admin=True)
    print("Admin user created")
except:
    print("Admin user already exists")

try:
    add_category("Videókártyák", "gpu.jpg")
    add_category("Processzorok", "cpu.jpg")
    add_category("Memóriák", "ram.jpg")
    print("Sample categories added")
except:
    print("Categories already exist")

try:
    add_product("RTX 4070 Ti", "Nagy teljesítményű videókártya", 349999, "rtx4070ti.jpg", 1, 5)
    add_product("RTX 4060", "Közepes teljesítményű videókártya", 199999, "rtx4060.jpg", 1, 10)
    add_product("Intel i7-13700K", "12. generációs processzor", 149999, "i713700k.jpg", 2, 8)
    add_product("AMD Ryzen 7 7800X3D", "Erőteljes gaming processzor", 129999, "ryzen77800x3d.jpg", 2, 6)
    add_product("Corsair Vengeance 32GB DDR5", "Gyors DDR5 memória", 79999, "corsair32gb.jpg", 3, 15)
    print("Sample products added")
except Exception as e:
    print(f"Error adding products: {e}")