# PC DADDY Database Migration Tool

This tool helps you merge data from an existing PC DADDY database into your current database, even with different schemas.

## Schema Compatibility

The migration tool handles schema differences automatically:

### Old Schema (Legacy)
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    image TEXT
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    image TEXT,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

### New Schema (Current)
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    is_admin BOOLEAN DEFAULT 0
);

CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    image TEXT
);

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    image TEXT,
    category_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);
```

## Automatic Handling

- **Missing Users Table**: Safely skipped if old database doesn't have users
- **Missing Quantity Column**: Defaults to 0 for products without quantity data
- **Schema Detection**: Automatically detects available columns and tables
- **Backward Compatibility**: Works with older database versions

## Features

- **Safe Migration**: Preserves existing data and handles conflicts intelligently
- **Image Transfer**: Automatically copies product and category images
- **Conflict Resolution**: Options to skip or overwrite duplicate entries
- **Dry Run Mode**: Test migration without making changes
- **Progress Tracking**: Shows exactly what will be migrated

## Usage

### Basic Migration

```bash
python migrate_db.py /path/to/old/database.db
```

### Migration with Images

```bash
python migrate_db.py /path/to/old/database.db --images /path/to/old/uploads
```

### Dry Run (Safe Testing)

```bash
python migrate_db.py /path/to/old/database.db --dry-run
```

### Force Overwrite Conflicts

```bash
python migrate_db.py /path/to/old/database.db --force
```

## Options

- `old_db`: Path to your existing database file (required)
- `--images PATH`: Path to the uploads directory containing images
- `--dry-run`: Show what would be migrated without making changes
- `--force`: Overwrite existing data instead of skipping duplicates

## What Gets Migrated

### Users Table
- **Conflicts**: Username already exists
- **Behavior**: Skips by default, updates with `--force`
- **Note**: Safely skipped if old database doesn't have users table

### Categories Table
- **Conflicts**: Category name already exists
- **Behavior**: Skips by default, updates with `--force`
- **Maps**: Old category IDs to new ones for product relationships

### Products Table
- **Conflicts**: Product with same name in same category
- **Behavior**: Skips by default, adds quantities with `--force`
- **Note**: Missing quantity column defaults to 0

### Images
- **Copies**: All image files from old uploads directory
- **Skips**: Files that already exist in new directory
- **Requires**: `--images` flag with path to old uploads folder

## Example Scenarios

### Scenario 1: Legacy Database Migration
Your old database doesn't have users or quantity columns:

```bash
python migrate_db.py /home/old_site/database.db --images /home/old_site/static/uploads
```

### Scenario 2: Partial Migration
You want to add new products from another site without overwriting existing data:

```bash
python migrate_db.py /home/other_site/database.db --dry-run
# Review the output, then run:
python migrate_db.py /home/other_site/database.db
```

### Scenario 3: Forced Update
You want to update existing products with new data:

```bash
python migrate_db.py /home/old_site/database.db --force --images /home/old_site/static/uploads
```

## Safety Features

- **Transaction Safety**: Uses database transactions - if anything fails, nothing is changed
- **Backup Recommendation**: Always backup your current database before migration
- **Dry Run**: Test everything first with `--dry-run`
- **Conflict Awareness**: Shows exactly what will be skipped vs. migrated
- **Schema Flexibility**: Handles missing tables and columns gracefully

## Troubleshooting

### "Old database file does not exist"
Make sure the path to your old database file is correct.

### "No old images path specified"
Use `--images /path/to/old/uploads` to copy image files.

### "Table 'users' does not exist in source database"
This is normal for legacy databases - the script will skip user migration.

### "Permission denied"
Make sure you have read access to the old database and write access to the current directory.

### Images not copying
Ensure the old uploads directory exists and contains the image files referenced in the database.

## Support

If you encounter issues, check:
1. Database file permissions
2. Image file paths
3. Available disk space
4. Database schema compatibility