# Database Migrations Guide - Timetable Manager

## Overview

This guide shows you how to create and apply database migrations for your Flask application using Flask-Migrate (Alembic).

## Quick Start

### 1. **Apply Existing Migrations**

```bash
# Navigate to src directory
cd /home/oumate/Documents/timetable_manager_backend

# Apply all pending migrations
flask db upgrade
```

### 2. **Check Migration Status**

```bash
# Show current migration
flask db current

# Show migration history
flask db history
```

## Common Migration Commands

### **Initialize Migration Repository (First Time Only)**

```bash
flask db init
```

_Note: This has already been done for your project._

### **Create a New Migration**

```bash
# Auto-generate migration from model changes
flask db migrate -m "Description of changes"

# Examples:
flask db migrate -m "Add email column to teachers"
flask db migrate -m "Create user_preferences table"
```

### **Apply Migrations**

```bash
# Apply all pending migrations
flask db upgrade

# Apply to specific revision
flask db upgrade <revision_id>
```

### **Rollback Migrations**

```bash
# Downgrade by one migration
flask db downgrade

# Downgrade to specific revision
flask db downgrade <revision_id>
```

### **View Migration Information**

```bash
# Show current migration
flask db current

# Show migration history
flask db history

# Show migration details
flask db show <revision_id>
```

## Typical Workflow

### **When You Modify Models:**

1. **Make changes to your model files** (e.g., add a column, create a new table)

   ```python
   # Example: Add a new column to Teacher model
   class Teacher(db.Model):
       # ... existing fields ...
       office_location = db.Column(db.String(100))  # NEW FIELD
   ```

2. **Create migration**

   ```bash
   cd /home/oumate/Documents/timetable_manager_backend/src
   flask db migrate -m "Add office_location to teachers"
   ```

3. **Review the generated migration file**

   - Check `migrations/versions/*.py`
   - Ensure the changes are correct
   - Edit if necessary

4. **Apply the migration**
   ```bash
   flask db upgrade
   ```

## Project Structure

Your migration files are located in:

```
src/
├── migrations/
│   ├── alembic.ini          # Alembic configuration
│   ├── env.py              # Migration environment
│   ├── script.py.mako      # Migration template
│   └── versions/           # Individual migration files
│       └── *.py           # Migration scripts
```

## Using the Custom Migration Manager

You can use the provided `migrations_manager.py` script for easier migration management:

```bash
# Show help
python migrations_manager.py help

# Apply migrations
python migrations_manager.py upgrade

# Create new migration
python migrations_manager.py create "Add new feature"

# Check status
python migrations_manager.py status

# Show history
python migrations_manager.py history
```

## Checking Database State

### **Connect to PostgreSQL and check tables:**

```bash
psql -d "postgresql://<username>:<password>.@<host>:<port>/<database>"
```

### **Common PostgreSQL commands:**

```sql
-- List all tables
\dt

-- Describe a specific table
\d table_name

-- Show table data
SELECT * FROM table_name LIMIT 5;

-- Show migration history
SELECT * FROM alembic_version;
```

## Important Notes

### **Before Making Changes:**

- Always backup your database before applying migrations in production
- Test migrations on a development database first
- Review auto-generated migrations before applying

### **Best Practices:**

- Use descriptive migration messages
- Make small, focused changes in each migration
- Keep migrations reversible when possible
- Don't edit existing migration files after they've been applied

### **Troubleshooting:**

**Migration conflicts:**

```bash
# If you have conflicts, you might need to merge migrations
flask db merge -m "Merge migrations"
```

**Reset migrations (DESTRUCTIVE):**

```bash
# Only for development - this will lose data!
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Examples

### **Example 1: Add a new column**

```python
# 1. Modify model
class Department(db.Model):
    # ... existing fields ...
    budget = db.Column(db.Float, default=0.0)  # NEW

# 2. Create migration
# flask db migrate -m "Add budget column to departments"

# 3. Apply migration
# flask db upgrade
```

### **Example 2: Create a new table**

```python
# 1. Create new model
class StudentEnrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)

# 2. Create migration
# flask db migrate -m "Create student_enrollment table"

# 3. Apply migration
# flask db upgrade
```

## Environment Variables

Make sure your `.env` file is properly configured:

```properties
SECRET_KEY='your-secret-key'
DEBUG=True
DATABASE_URL='postgresql://username:password@localhost:5432/database_name'
```

---

## Your Current Status

**Migration repository initialized**
**Initial migration created**
**Models registered**: Admin, Department, Teacher, Room, Course, TimeTable, TimeTableSlot

**Next step:** Run `flask db upgrade` to apply the initial migration to your database!

## Database Cleanup & Reset

### **Quick Commands to Clear Database**

```bash
psql -d "postgresql://<username>:<password>.@<host>:<port>/<database>" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Method 3: Flask-Migrate downgrade (if you want to keep migration history)
flask db downgrade base
```

### **Database Reset Options**

#### **Option 1: Complete Database Reset**

```bash
psql -d "postgresql://<username>:<password>.@<host>:<port>/<database>" -c "
  DROP SCHEMA public CASCADE;
  CREATE SCHEMA public;
  GRANT ALL ON SCHEMA public TO postgres;
  GRANT ALL ON SCHEMA public TO public;
"
```

#### **Option 2: Clear Data Only**

This keeps table structure but removes all data:

```bash
psql -d "postgresql://<username>:<password>.@<host>:<port>/<database>" -c "
  TRUNCATE admin, department, teacher, room, course, time_table, timetable_slot RESTART IDENTITY CASCADE;
"
```

#### **Option 3: Reset Migrations**

This resets the migration history:

```bash
# Delete migrations and start fresh
rm -rf migrations/
cd src
flask db init
flask db migrate -m "Fresh start"
flask db upgrade
```

### **DANGER ZONE - Nuclear Options**

**Drop entire database and recreate:**

```sql
-- Connect as postgres superuser
psql -U postgres

-- Drop and recreate database
DROP DATABASE timetable_manager;
CREATE DATABASE timetable_manager OWNER <username>;
```

**Reset everything including migrations:**

```bash
# Delete everything
rm -rf migrations/
psql -d "postgresql://<username>:<password>.@<host>:<port>/<database>" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Start completely fresh
cd src
flask db init
flask db migrate -m "Fresh start"
flask db upgrade
```

### **Safe Development Practices**

Before clearing your database:

1. **Backup your data (if needed):**

   ```bash
   pg_dump -U <username> timetable_manager > backup.sql
   ```

2. **Restore from backup (if needed):**
   ```bash
   psql -U oumate timetable_manager < backup.sql
   ```
