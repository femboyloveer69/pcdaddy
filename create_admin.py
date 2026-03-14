from models import create_user

create_user("admin", "admin123", is_admin=True)
print("Admin user created: username='admin', password='admin123'")