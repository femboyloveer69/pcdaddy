import sqlite3

with sqlite3.connect("database.db") as db:
    with open("schema.sql") as f:
        db.executescript(f.read())

print("Database initialized.")
