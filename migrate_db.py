#!/usr/bin/env python3
"""
Database Migration Script for PC DADDY Webshop

This script merges data from an old database into the current database.
It handles schema differences and missing tables/columns gracefully.

Usage:
    python migrate_db.py /path/to/old/database.db [--images /path/to/old/uploads]

Options:
    --images PATH: Path to old uploads directory to copy images from
    --dry-run: Show what would be migrated without actually doing it
    --force: Overwrite conflicting data instead of skipping
"""

import sqlite3
import argparse
import os
import shutil
from pathlib import Path

class DatabaseMigrator:
    def __init__(self, old_db_path, new_db_path="database.db", images_path=None):
        self.old_db_path = old_db_path
        self.new_db_path = new_db_path
        self.old_images_path = images_path
        self.new_images_path = Path("static/uploads")

        # Ensure uploads directory exists
        self.new_images_path.mkdir(exist_ok=True)

    def connect_databases(self):
        """Connect to both databases"""
        self.old_conn = sqlite3.connect(self.old_db_path)
        self.old_conn.row_factory = sqlite3.Row

        self.new_conn = sqlite3.connect(self.new_db_path)
        self.new_conn.row_factory = sqlite3.Row

    def initialize_new_database(self):
        """Initialize the new database with the current schema"""
        schema_path = Path(__file__).parent / "schema.sql"
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        self.new_conn.executescript(schema_sql)
        self.new_conn.commit()

    def table_exists(self, conn, table_name):
        """Check if a table exists in the database"""
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return cursor.fetchone() is not None

    def get_column_names(self, conn, table_name):
        """Get column names for a table"""
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        return [col[1] for col in columns_info]

    def get_table_data(self, conn, table_name):
        """Get all data from a table, handling missing columns gracefully"""
        if not self.table_exists(conn, table_name):
            print(f"Table '{table_name}' does not exist in source database")
            return []

        cursor = conn.cursor()

        # Get column names for this table
        column_names = self.get_column_names(conn, table_name)

        # Build SELECT query with available columns
        select_columns = ", ".join(column_names)
        cursor.execute(f"SELECT {select_columns} FROM {table_name}")

        # Convert to dict-like rows
        rows = []
        for row in cursor.fetchall():
            row_dict = {}
            for i, col_name in enumerate(column_names):
                row_dict[col_name] = row[i]
            rows.append(row_dict)

        return rows

    def copy_images(self, dry_run=False):
        """Copy images from old uploads directory"""
        if not self.old_images_path or not os.path.exists(self.old_images_path):
            print("No old images path specified or directory doesn't exist")
            return

        old_images = Path(self.old_images_path)
        copied = 0
        skipped = 0

        for image_file in old_images.glob("*"):
            if image_file.is_file():
                new_path = self.new_images_path / image_file.name
                if not new_path.exists():
                    if not dry_run:
                        shutil.copy2(image_file, new_path)
                    print(f"{'Would copy' if dry_run else 'Copied'}: {image_file.name}")
                    copied += 1
                else:
                    print(f"Skipped (already exists): {image_file.name}")
                    skipped += 1

        print(f"Images: {copied} copied, {skipped} skipped")

    def migrate_users(self, old_users, dry_run=False, force=False):
        """Migrate users table - skip if old database doesn't have users"""
        if not old_users:
            print("No users table in old database - skipping user migration")
            return 0, 0

        new_cursor = self.new_conn.cursor()
        migrated = 0
        skipped = 0

        for user in old_users:
            # Check if username already exists
            new_cursor.execute("SELECT id FROM users WHERE username = ?", (user['username'],))
            existing = new_cursor.fetchone()

            if existing:
                if force:
                    print(f"Would update user: {user['username']}" if dry_run else f"Updating user: {user['username']}")
                    if not dry_run:
                        new_cursor.execute("""
                            UPDATE users SET password = ?, is_admin = ?
                            WHERE username = ?
                        """, (user['password'], user['is_admin'], user['username']))
                    migrated += 1
                else:
                    print(f"Skipped existing user: {user['username']}")
                    skipped += 1
            else:
                print(f"{'Would add' if dry_run else 'Adding'} user: {user['username']}")
                if not dry_run:
                    new_cursor.execute("""
                        INSERT INTO users (username, password, is_admin)
                        VALUES (?, ?, ?)
                    """, (user['username'], user['password'], user['is_admin']))
                migrated += 1

        if not dry_run:
            self.new_conn.commit()
        return migrated, skipped

    def migrate_categories(self, old_categories, dry_run=False, force=False):
        """Migrate categories table"""
        new_cursor = self.new_conn.cursor()
        migrated = 0
        skipped = 0

        # Create mapping of old IDs to new IDs
        self.category_id_map = {}

        for category in old_categories:
            # Check if category name already exists
            new_cursor.execute("SELECT id FROM categories WHERE name = ?", (category['name'],))
            existing = new_cursor.fetchone()

            if existing:
                if force:
                    print(f"Would update category: {category['name']}" if dry_run else f"Updating category: {category['name']}")
                    if not dry_run:
                        new_cursor.execute("""
                            UPDATE categories SET image = ?
                            WHERE name = ?
                        """, (category['image'], category['name']))
                    self.category_id_map[category['id']] = existing['id']
                    migrated += 1
                else:
                    print(f"Skipped existing category: {category['name']}")
                    self.category_id_map[category['id']] = existing['id']
                    skipped += 1
            else:
                print(f"{'Would add' if dry_run else 'Adding'} category: {category['name']}")
                if not dry_run:
                    new_cursor.execute("""
                        INSERT INTO categories (name, image)
                        VALUES (?, ?)
                    """, (category['name'], category['image']))
                    new_id = new_cursor.lastrowid
                    self.category_id_map[category['id']] = new_id
                else:
                    # For dry run, use a placeholder ID
                    self.category_id_map[category['id']] = f"new_id_for_{category['name']}"
                migrated += 1

        if not dry_run:
            self.new_conn.commit()
        return migrated, skipped

    def migrate_products(self, old_products, dry_run=False, force=False):
        """Migrate products table - handle missing quantity column"""
        new_cursor = self.new_conn.cursor()
        migrated = 0
        skipped = 0

        for product in old_products:
            # Map old category_id to new category_id
            new_category_id = self.category_id_map.get(product['category_id'])
            if not new_category_id:
                print(f"Warning: No mapping found for category_id {product['category_id']}, skipping product: {product['name']}")
                skipped += 1
                continue

            # Handle missing quantity column (default to 0)
            quantity = product.get('quantity', 0)

            # Check if product with same name and category already exists
            new_cursor.execute("""
                SELECT id FROM products
                WHERE name = ? AND category_id = ?
            """, (product['name'], new_category_id))
            existing = new_cursor.fetchone()

            if existing:
                if force:
                    print(f"Would update product: {product['name']}" if dry_run else f"Updating product: {product['name']}")
                    if not dry_run:
                        new_cursor.execute("""
                            UPDATE products SET
                                description = ?, price = ?, image = ?,
                                quantity = ?
                            WHERE name = ? AND category_id = ?
                        """, (product['description'], product['price'], product['image'],
                              quantity, product['name'], new_category_id))
                    migrated += 1
                else:
                    print(f"Skipped existing product: {product['name']}")
                    skipped += 1
            else:
                print(f"{'Would add' if dry_run else 'Adding'} product: {product['name']}")
                if not dry_run:
                    new_cursor.execute("""
                        INSERT INTO products (name, description, price, image, category_id, quantity)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (product['name'], product['description'], product['price'],
                          product['image'], new_category_id, quantity))
                migrated += 1

        if not dry_run:
            self.new_conn.commit()
        return migrated, skipped

    def migrate(self, dry_run=False, force=False):
        """Main migration function"""
        try:
            self.connect_databases()

            # Initialize the new database with current schema
            print("Initializing new database with current schema...")
            self.initialize_new_database()
            print("New database initialized.")
            print()

            print("=== DATABASE MIGRATION ===")
            print(f"Old database: {self.old_db_path}")
            print(f"New database: {self.new_db_path}")
            print(f"Dry run: {dry_run}")
            print(f"Force overwrite: {force}")
            print()

            # Get data from old database
            print("Reading data from old database...")
            old_users = self.get_table_data(self.old_conn, 'users')
            old_categories = self.get_table_data(self.old_conn, 'categories')
            old_products = self.get_table_data(self.old_conn, 'products')

            print(f"Found: {len(old_users)} users, {len(old_categories)} categories, {len(old_products)} products")
            print()

            # Copy images
            print("Copying images...")
            self.copy_images(dry_run)
            print()

            # Migrate data
            print("Migrating users...")
            users_migrated, users_skipped = self.migrate_users(old_users, dry_run, force)
            print(f"Users: {users_migrated} migrated, {users_skipped} skipped")
            print()

            print("Migrating categories...")
            cats_migrated, cats_skipped = self.migrate_categories(old_categories, dry_run, force)
            print(f"Categories: {cats_migrated} migrated, {cats_skipped} skipped")
            print()

            print("Migrating products...")
            prods_migrated, prods_skipped = self.migrate_products(old_products, dry_run, force)
            print(f"Products: {prods_migrated} migrated, {prods_skipped} skipped")
            print()

            if dry_run:
                print("=== DRY RUN COMPLETE ===")
                print("No changes were made. Remove --dry-run to perform actual migration.")
            else:
                print("=== MIGRATION COMPLETE ===")
                print("Database migration finished successfully!")

        except Exception as e:
            print(f"Error during migration: {e}")
            import traceback
            traceback.print_exc()
            if not dry_run:
                self.new_conn.rollback()
        finally:
            self.close_databases()

def main():
    parser = argparse.ArgumentParser(description="Migrate PC DADDY database")
    parser.add_argument("old_db", help="Path to old database file")
    parser.add_argument("--new-db", default="database.db", help="Path for new database file (default: database.db)")
    parser.add_argument("--images", help="Path to old uploads directory")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without doing it")
    parser.add_argument("--force", action="store_true", help="Overwrite conflicting data")

    args = parser.parse_args()

    if not os.path.exists(args.old_db):
        print(f"Error: Old database file '{args.old_db}' does not exist")
        return 1

    migrator = DatabaseMigrator(args.old_db, new_db_path=args.new_db, images_path=args.images)
    migrator.migrate(dry_run=args.dry_run, force=args.force)

    return 0

if __name__ == "__main__":
    exit(main())