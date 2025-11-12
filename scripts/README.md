# Scripts Directory

This directory contains utility scripts for database management and seeding.

## Available Scripts

### seed_database.py

Advanced database seeding script with comprehensive conflict detection and prevention.

#### Features

- **Conflict Detection**: Prevents double-booking of rooms and teachers
- **Smart Scheduling**: Intelligent room assignment based on course type
- **Duplicate Prevention**: Checks for existing records before creation
- **Teacher Availability**: Tracks teacher schedules to avoid conflicts
- **Room Capacity Validation**: Assigns appropriate rooms for course needs
- **Comprehensive Logging**: Detailed output showing what was created/skipped

#### Usage

```bash
# From project root
python3 scripts/seed_database.py

# Or make it executable
chmod +x scripts/seed_database.py
./scripts/seed_database.py
```

#### What It Creates

- **3 Admin Users** with credentials

  - admin/admin123 (super_admin)
  - registrar/registrar123 (admin)
  - scheduler/scheduler123 (admin)

- **7 Departments**

  - Computer Science (CS)
  - Mathematics (MATH)
  - Physics (PHY)
  - Chemistry (CHEM)
  - Biology (BIO)
  - Engineering (ENG)
  - Business Administration (BUS)

- **42 Teachers** (6 per department)

  - Unique email addresses
  - Realistic names with titles
  - Assigned specializations

- **35 Rooms**

  - 20 Classrooms (Room 101-120)
  - 10 Labs (Lab 201-210)
  - 5 Lecture Halls (Auditoriums and Halls)

- **50+ Courses**

  - Realistic course codes (CS101, MATH201, etc.)
  - Assigned teachers
  - Weekly session requirements (2-4 sessions)

- **14 Timetables**

  - Fall 2024 for each department
  - Spring 2025 for each department

- **300+ TimeTable Slots**
  - Monday-Friday schedule
  - 5 time slots per day (8AM-6PM)
  - No scheduling conflicts
  - Appropriate room assignments

#### Conflict Detection

The script uses a `ConflictDetector` class that tracks:

1. **Room Conflicts**: Ensures no room is double-booked
2. **Teacher Conflicts**: Ensures teachers aren't scheduled in multiple places
3. **Time Conflicts**: Validates time slot overlaps
4. **Session Count**: Tracks number of sessions per course

#### Smart Room Assignment

- **Labs**: Assigned to CS, Engineering, Chemistry, Physics, Biology courses with "Lab" in the name
- **Lecture Halls**: Assigned to introductory courses (101, 102 level) that may have large enrollments
- **Classrooms**: Assigned to standard courses

#### Re-running the Script

The script can be safely re-run multiple times:

- Checks for existing records before creating
- Skips duplicates (by username, email, code, etc.)
- Shows detailed output of what was created vs. skipped

#### Output Example

```
==================================================
TIMETABLE MANAGER - ADVANCED DATABASE SEEDING
==================================================

CLEARING DATABASE
==================================================
Deleted Records:
  - TimeTableSlot: 0 records
  - TimeTable: 0 records
  ...

CREATING ADMINS
==================================================
  [CREATE] admin (super_admin)
  [CREATE] registrar (admin)
  ...

Total Admins: 3
...

DATABASE SEEDING SUMMARY
==================================================
Records Created:
  Admins:              3
  Departments:         7
  Teachers:            42
  Rooms:               35
  Courses:             56
  Timetables:          14
  TimeTable Slots:     312

Room Breakdown:
  Classrooms:          20
  Laboratories:        10
  Lecture Halls:       5

Scheduling Statistics:
  Average slots/timetable: 22
  Slots per day:
    Monday: 65
    Tuesday: 62
    Wednesday: 58
    Thursday: 64
    Friday: 63
```

#### Troubleshooting

**Issue**: ModuleNotFoundError

```bash
# Ensure you're in project root and venv is activated
cd /path/to/timetable_manager_backend
source venv/bin/activate
python3 scripts/seed_database.py
```

**Issue**: Database connection error

```bash
# Check .env file has correct DATABASE_URL
# Verify PostgreSQL is running
psql -d timetable_manager -c "SELECT 1"
```

**Issue**: Foreign key constraint violations

```bash
# The script handles order automatically, but if issues persist:
flask db downgrade base
flask db upgrade
python3 scripts/seed_database.py
```

## Future Scripts

Additional scripts that can be added to this directory:

- `backup_database.py` - Database backup utility
- `restore_database.py` - Database restore utility
- `export_timetable.py` - Export timetables to PDF/Excel
- `import_courses.py` - Import courses from CSV
- `clean_old_data.py` - Archive or delete old timetables
- `generate_reports.py` - Generate usage reports
