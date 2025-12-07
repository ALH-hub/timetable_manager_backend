#!/usr/bin/env python3
"""
Advanced Database Seeding Script for Timetable Manager
AUTHOR: ALHADJI OUMATE
STUDENT ID: 22U2033

This script populates the database with realistic academic data with:
- Comprehensive conflict detection
- Smart scheduling algorithms
- Teacher availability tracking
- Room capacity validation
- Duplicate prevention
"""

import random
from datetime import datetime, date, time, timedelta
import sys
import os
from collections import defaultdict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import create_app
from config.db import db
from models import Admin, Department, Teacher, Room, Course, TimeTable, TimeTableSlot, Level


class ConflictDetector:
    """Utility class for detecting scheduling conflicts"""

    def __init__(self):
        # Track room usage: {(timetable_id, day, start_time, room_id): slot_id}
        self.room_schedule = {}
        # Track teacher usage: {(timetable_id, day, start_time, teacher_id): slot_id}
        self.teacher_schedule = {}
        # Track course sessions: {course_id: count}
        self.course_sessions = defaultdict(int)

    def has_room_conflict(self, timetable_id, day, start_time, end_time, room_id):
        """Check if room is already booked for this time slot"""
        # Check all time slots that would overlap
        for existing_key in self.room_schedule.keys():
            existing_tt_id, existing_day, existing_start, existing_room_id = existing_key

            if (existing_tt_id == timetable_id and
                existing_day == day and
                existing_room_id == room_id):
                # Check for time overlap
                if self._times_overlap(start_time, end_time, existing_start):
                    return True
        return False

    def has_teacher_conflict(self, timetable_id, day, start_time, end_time, teacher_id):
        """Check if teacher is already scheduled for this time slot"""
        if teacher_id is None:
            return False

        for existing_key in self.teacher_schedule.keys():
            existing_tt_id, existing_day, existing_start, existing_teacher_id = existing_key

            if (existing_tt_id == timetable_id and
                existing_day == day and
                existing_teacher_id == teacher_id):
                # Check for time overlap
                if self._times_overlap(start_time, end_time, existing_start):
                    return True
        return False

    def _times_overlap(self, start1, end1, start2):
        """Check if two time periods overlap (simplified check)"""
        # Assuming standard 2-hour slots, check if they're the same start time
        return start1 == start2

    def register_slot(self, timetable_id, day, start_time, room_id, teacher_id, course_id, slot_id):
        """Register a scheduled slot to track conflicts"""
        self.room_schedule[(timetable_id, day, start_time, room_id)] = slot_id
        if teacher_id:
            self.teacher_schedule[(timetable_id, day, start_time, teacher_id)] = slot_id
        self.course_sessions[course_id] += 1

    def get_course_sessions(self, course_id):
        """Get number of sessions scheduled for a course"""
        return self.course_sessions.get(course_id, 0)


def clear_database():
    """Clear all existing data from the database"""
    print("=" * 70)
    print("CLEARING DATABASE")
    print("=" * 70)

    try:
        # Delete in correct order to respect foreign keys
        deleted_counts = {}

        deleted_counts['TimeTableSlot'] = TimeTableSlot.query.count()
        TimeTableSlot.query.delete()

        deleted_counts['TimeTable'] = TimeTable.query.count()
        TimeTable.query.delete()

        deleted_counts['Course'] = Course.query.count()
        Course.query.delete()

        deleted_counts['Teacher'] = Teacher.query.count()
        Teacher.query.delete()

        deleted_counts['Room'] = Room.query.count()
        Room.query.delete()

        deleted_counts['Department'] = Department.query.count()
        Department.query.delete()

        deleted_counts['Admin'] = Admin.query.count()
        Admin.query.delete()

        db.session.commit()

        print("\nDeleted Records:")
        for model, count in deleted_counts.items():
            print(f"  - {model}: {count} records")
        print("\nDatabase cleared successfully!")

    except Exception as e:
        db.session.rollback()
        print(f"Error clearing database: {e}")
        raise


def seed_admins():
    """Create admin users with unique credentials"""
    print("\n" + "=" * 70)
    print("CREATING ADMINS")
    print("=" * 70)

    admins_data = [
        {
            'username': 'admin',
            'email': 'admin@university.edu',
            'password': 'admin123',
            'role': 'super_admin'
        },
        {
            'username': 'registrar',
            'email': 'registrar@university.edu',
            'password': 'registrar123',
            'role': 'admin'
        },
        {
            'username': 'scheduler',
            'email': 'scheduler@university.edu',
            'password': 'scheduler123',
            'role': 'admin'
        }
    ]

    admins = []
    for admin_data in admins_data:
        # Check if admin already exists
        existing = Admin.query.filter_by(username=admin_data['username']).first()
        if existing:
            print(f"  [SKIP] Admin '{admin_data['username']}' already exists")
            admins.append(existing)
            continue

        admin = Admin(
            username=admin_data['username'],
            email=admin_data['email'],
            role=admin_data['role']
        )
        admin.set_password(admin_data['password'])
        db.session.add(admin)
        admins.append(admin)
        print(f"  [CREATE] {admin_data['username']} ({admin_data['role']})")

    db.session.commit()
    print(f"\nTotal Admins: {len(admins)}")
    return admins


def seed_departments():
    """Create academic departments with unique codes"""
    print("\n" + "=" * 70)
    print("CREATING DEPARTMENTS")
    print("=" * 70)

    departments_data = [
        {'name': 'Computer Science', 'code': 'CS', 'head': 'Dr. Alan Turing', 'contact_email': 'cs@university.edu'},
        {'name': 'Mathematics', 'code': 'MATH', 'head': 'Dr. Ada Lovelace', 'contact_email': 'math@university.edu'},
        {'name': 'Physics', 'code': 'PHY', 'head': 'Dr. Marie Curie', 'contact_email': 'physics@university.edu'},
        {'name': 'Chemistry', 'code': 'CHEM', 'head': 'Dr. Dmitri Mendeleev', 'contact_email': 'chem@university.edu'},
        {'name': 'Biology', 'code': 'BIO', 'head': 'Dr. Charles Darwin', 'contact_email': 'bio@university.edu'},
        {'name': 'Engineering', 'code': 'ENG', 'head': 'Dr. Nikola Tesla', 'contact_email': 'eng@university.edu'},
        {'name': 'Business Administration', 'code': 'BUS', 'head': 'Dr. Peter Drucker', 'contact_email': 'business@university.edu'},
    ]

    departments = []
    for dept_data in departments_data:
        # Check for duplicate code
        existing = Department.query.filter_by(code=dept_data['code']).first()
        if existing:
            print(f"  [SKIP] {dept_data['code']}: {dept_data['name']} (already exists)")
            departments.append(existing)
            continue

        dept = Department(**dept_data)
        db.session.add(dept)
        departments.append(dept)
        print(f"  [CREATE] {dept_data['code']}: {dept_data['name']}")

    db.session.commit()
    print(f"\nTotal Departments: {len(departments)}")
    return departments


def seed_teachers(departments):
    """Create teachers with unique email addresses"""
    print("\n" + "=" * 70)
    print("CREATING TEACHERS")
    print("=" * 70)

    first_names = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
                   'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
                   'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa']

    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                  'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Wilson', 'Anderson', 'Thomas', 'Taylor',
                  'Moore', 'Jackson', 'Martin', 'Lee', 'Thompson', 'White', 'Harris', 'Clark']

    titles = ['Dr.', 'Prof.', 'Dr.', 'Prof.', 'Dr.']

    specializations = {
        'CS': ['Artificial Intelligence', 'Database Systems', 'Software Engineering', 'Cybersecurity',
               'Web Development', 'Machine Learning', 'Data Science'],
        'MATH': ['Calculus', 'Linear Algebra', 'Statistics', 'Discrete Mathematics', 'Number Theory',
                 'Abstract Algebra', 'Mathematical Analysis'],
        'PHY': ['Quantum Physics', 'Classical Mechanics', 'Thermodynamics', 'Electromagnetism',
                'Optics', 'Astrophysics', 'Particle Physics'],
        'CHEM': ['Organic Chemistry', 'Inorganic Chemistry', 'Physical Chemistry', 'Analytical Chemistry',
                 'Biochemistry', 'Chemical Engineering'],
        'BIO': ['Molecular Biology', 'Genetics', 'Ecology', 'Microbiology', 'Anatomy',
                'Cell Biology', 'Evolutionary Biology'],
        'ENG': ['Mechanical Engineering', 'Electrical Engineering', 'Civil Engineering',
                'Chemical Engineering', 'Computer Engineering'],
        'BUS': ['Marketing', 'Finance', 'Management', 'Accounting', 'Economics',
                'Business Strategy', 'Entrepreneurship']
    }

    teachers = []
    teacher_count_per_dept = 6  # 6 teachers per department for better coverage
    existing_emails = set()

    # Get existing teacher emails to avoid duplicates
    for existing_teacher in Teacher.query.all():
        existing_emails.add(existing_teacher.email)

    print(f"\nCreating {teacher_count_per_dept} teachers per department...")

    for dept in departments:
        dept_specs = specializations.get(dept.code, ['General Studies'])
        print(f"\n{dept.code} - {dept.name}:")

        for i in range(teacher_count_per_dept):
            # Generate unique email
            attempts = 0
            while attempts < 100:
                title = random.choice(titles)
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)

                email = f"{first_name.lower()}.{last_name.lower()}@university.edu"
                if attempts > 0:
                    email = f"{first_name.lower()}.{last_name.lower()}{attempts}@university.edu"

                if email not in existing_emails:
                    existing_emails.add(email)
                    break
                attempts += 1

            if attempts >= 100:
                print(f"  [ERROR] Could not generate unique email after 100 attempts")
                continue

            name = f"{title} {first_name} {last_name}"

            teacher = Teacher(
                name=name,
                email=email,
                phone=f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
                department_id=dept.id,
                specialization=random.choice(dept_specs),
                is_active=True
            )
            db.session.add(teacher)
            teachers.append(teacher)
            print(f"  [CREATE] {name} - {teacher.specialization}")

    db.session.commit()
    print(f"\nTotal Teachers: {len(teachers)}")
    return teachers


def seed_levels():
    """Create default student levels"""
    print("\n" + "=" * 70)
    print("CREATING LEVELS")
    print("=" * 70)

    levels_data = [
        {'name': 'Level 1', 'code': 'L1', 'order': 1, 'description': 'First year undergraduate level'},
        {'name': 'Level 2', 'code': 'L2', 'order': 2, 'description': 'Second year undergraduate level'},
        {'name': 'Level 3', 'code': 'L3', 'order': 3, 'description': 'Third year undergraduate level'},
        {'name': 'Master 1', 'code': 'M1', 'order': 4, 'description': 'First year master level'},
        {'name': 'Master 2', 'code': 'M2', 'order': 5, 'description': 'Second year master level'},
    ]

    levels = []
    existing_codes = set(l.code for l in Level.query.all())

    for level_data in levels_data:
        if level_data['code'] in existing_codes:
            existing = Level.query.filter_by(code=level_data['code']).first()
            print(f"  [SKIP] {level_data['code']}: {level_data['name']} (already exists)")
            levels.append(existing)
            continue

        level = Level(**level_data)
        db.session.add(level)
        levels.append(level)
        print(f"  [CREATE] {level_data['code']}: {level_data['name']}")

    db.session.commit()
    print(f"\nTotal Levels: {len(levels)}")
    return levels


def seed_rooms():
    """Create classrooms, labs, and lecture halls with unique names"""
    print("\n" + "=" * 70)
    print("CREATING ROOMS")
    print("=" * 70)

    rooms = []
    existing_names = set(r.name for r in Room.query.all())

    # Regular classrooms (capacity: 30-50)
    print("\nClassrooms:")
    for i in range(1, 21):
        name = f"Room {100 + i}"
        if name in existing_names:
            print(f"  [SKIP] {name} (already exists)")
            continue

        room = Room(
            name=name,
            room_type='classroom',
            capacity=random.choice([30, 35, 40, 45, 50]),
            is_available=True
        )
        db.session.add(room)
        rooms.append(room)
        print(f"  [CREATE] {name} (capacity: {room.capacity})")

    # Computer labs (capacity: 25-40)
    print("\nLaboratories:")
    for i in range(1, 11):
        name = f"Lab {200 + i}"
        if name in existing_names:
            print(f"  [SKIP] {name} (already exists)")
            continue

        room = Room(
            name=name,
            room_type='lab',
            capacity=random.choice([25, 30, 35, 40]),
            is_available=True
        )
        db.session.add(room)
        rooms.append(room)
        print(f"  [CREATE] {name} (capacity: {room.capacity})")

    # Lecture halls (capacity: 100-300)
    print("\nLecture Halls:")
    lecture_halls = [
        ('Auditorium A', 300),
        ('Auditorium B', 250),
        ('Hall 301', 150),
        ('Hall 302', 150),
        ('Grand Hall', 200),
    ]
    for name, capacity in lecture_halls:
        if name in existing_names:
            print(f"  [SKIP] {name} (already exists)")
            continue

        room = Room(
            name=name,
            room_type='lecture_hall',
            capacity=capacity,
            is_available=True
        )
        db.session.add(room)
        rooms.append(room)
        print(f"  [CREATE] {name} (capacity: {capacity})")

    db.session.commit()
    print(f"\nTotal Rooms: {len(rooms)}")
    return rooms


def seed_courses(departments, teachers, levels=None):
    """Create courses with unique codes"""
    print("\n" + "=" * 70)
    print("CREATING COURSES")
    print("=" * 70)

    course_templates = {
        'CS': [
            ('Introduction to Programming', 'CS101', 3),
            ('Data Structures', 'CS201', 3),
            ('Algorithms', 'CS301', 2),
            ('Database Systems', 'CS202', 2),
            ('Web Development', 'CS203', 2),
            ('Software Engineering', 'CS302', 2),
            ('Operating Systems', 'CS303', 2),
            ('Computer Networks', 'CS304', 2),
            ('Artificial Intelligence', 'CS401', 2),
            ('Machine Learning', 'CS402', 2),
        ],
        'MATH': [
            ('Calculus I', 'MATH101', 4),
            ('Calculus II', 'MATH102', 4),
            ('Linear Algebra', 'MATH201', 3),
            ('Statistics', 'MATH202', 2),
            ('Discrete Mathematics', 'MATH203', 2),
            ('Differential Equations', 'MATH301', 2),
            ('Abstract Algebra', 'MATH302', 2),
            ('Real Analysis', 'MATH401', 2),
        ],
        'PHY': [
            ('Physics I', 'PHY101', 3),
            ('Physics II', 'PHY102', 3),
            ('Quantum Mechanics', 'PHY301', 2),
            ('Thermodynamics', 'PHY201', 2),
            ('Electromagnetism', 'PHY202', 2),
            ('Optics', 'PHY203', 2),
            ('Astrophysics', 'PHY401', 2),
        ],
        'CHEM': [
            ('General Chemistry', 'CHEM101', 3),
            ('Organic Chemistry I', 'CHEM201', 3),
            ('Organic Chemistry II', 'CHEM202', 3),
            ('Physical Chemistry', 'CHEM301', 2),
            ('Analytical Chemistry', 'CHEM203', 2),
            ('Biochemistry', 'CHEM302', 2),
        ],
        'BIO': [
            ('Biology I', 'BIO101', 3),
            ('Biology II', 'BIO102', 3),
            ('Genetics', 'BIO201', 2),
            ('Molecular Biology', 'BIO301', 2),
            ('Ecology', 'BIO202', 2),
            ('Microbiology', 'BIO203', 2),
            ('Anatomy', 'BIO302', 2),
        ],
        'ENG': [
            ('Engineering Fundamentals', 'ENG101', 3),
            ('Mechanics', 'ENG201', 2),
            ('Circuits', 'ENG202', 2),
            ('Materials Science', 'ENG301', 2),
            ('Design Principles', 'ENG203', 2),
            ('Thermodynamics', 'ENG302', 2),
        ],
        'BUS': [
            ('Business Fundamentals', 'BUS101', 2),
            ('Marketing', 'BUS201', 2),
            ('Finance', 'BUS202', 2),
            ('Management', 'BUS203', 2),
            ('Economics', 'BUS204', 2),
            ('Accounting', 'BUS301', 2),
            ('Business Strategy', 'BUS302', 2),
        ]
    }

    courses = []
    current_year = datetime.now().year
    semesters = ['Fall', 'Spring']
    existing_codes = set(c.code for c in Course.query.all())

    for dept in departments:
        dept_teachers = [t for t in teachers if t.department_id == dept.id]
        templates = course_templates.get(dept.code, [])

        print(f"\n{dept.code} - {dept.name}:")

        for name, code, weekly_sessions in templates:
            if code in existing_codes:
                print(f"  [SKIP] {code}: {name} (already exists)")
                continue

            # Assign a random teacher from the department
            teacher = random.choice(dept_teachers) if dept_teachers else None

            # Assign level based on course code (101-199 = L1, 201-299 = L2, 301-399 = L3, 401+ = M1/M2)
            level = None
            if levels:
                course_number = int(''.join(filter(str.isdigit, code)))
                if 101 <= course_number <= 199:
                    level = next((l for l in levels if l.code == 'L1'), None)
                elif 201 <= course_number <= 299:
                    level = next((l for l in levels if l.code == 'L2'), None)
                elif 301 <= course_number <= 399:
                    level = next((l for l in levels if l.code == 'L3'), None)
                elif 401 <= course_number <= 499:
                    # Alternate between M1 and M2 for 400-level courses
                    level = next((l for l in levels if l.code == ('M1' if course_number % 2 == 1 else 'M2')), None)

            course = Course(
                name=name,
                code=code,
                department_id=dept.id,
                teacher_id=teacher.id if teacher else None,
                level_id=level.id if level else None,
                weekly_sessions=weekly_sessions,
                semester=random.choice(semesters),
                year=current_year,
                is_active=True
            )
            db.session.add(course)
            courses.append(course)

            teacher_name = teacher.name if teacher else 'Unassigned'
            level_name = level.code if level else 'Unassigned'
            print(f"  [CREATE] {code}: {name} ({weekly_sessions} sessions/week) - {teacher_name} - Level: {level_name}")

    db.session.commit()
    print(f"\nTotal Courses: {len(courses)}")
    return courses


def seed_timetables(departments, admins):
    """Create timetables for each department"""
    print("\n" + "=" * 70)
    print("CREATING TIMETABLES")
    print("=" * 70)

    timetables = []
    current_year = datetime.now().year

    # Create Fall 2024 timetable
    fall_start = date(2024, 9, 2)
    fall_end = date(2024, 12, 20)

    # Create Spring 2025 timetable
    spring_start = date(2025, 1, 13)
    spring_end = date(2025, 5, 16)

    semesters = [
        ('Fall', 2024, fall_start, fall_end),
        ('Spring', 2025, spring_start, spring_end)
    ]

    admin = admins[0] if admins else None

    for dept in departments:
        print(f"\n{dept.code} - {dept.name}:")
        for semester, year, week_start, week_end in semesters:
            # Check if timetable already exists
            existing = TimeTable.query.filter_by(
                department_id=dept.id,
                semester=semester,
                academic_year=f"{year}-{year+1}"
            ).first()

            if existing:
                print(f"  [SKIP] {semester} {year} (already exists)")
                timetables.append(existing)
                continue

            timetable = TimeTable(
                name=f"{dept.name} {semester} {year}",
                department_id=dept.id,
                week_start=week_start,
                week_end=week_end,
                academic_year=f"{year}-{year+1}",
                semester=semester,
                status='published' if semester == 'Fall' else 'draft',
                created_by=admin.id if admin else None
            )
            db.session.add(timetable)
            timetables.append(timetable)
            print(f"  [CREATE] {semester} {year} ({timetable.status})")

    db.session.commit()
    print(f"\nTotal Timetables: {len(timetables)}")
    return timetables


def seed_timetable_slots(timetables, courses, rooms):
    """Create time slots with comprehensive conflict detection"""
    print("\n" + "=" * 70)
    print("CREATING TIMETABLE SLOTS")
    print("=" * 70)

    # Initialize conflict detector
    conflict_detector = ConflictDetector()

    # Time slots: 8:00 AM to 6:00 PM (2-hour blocks)
    time_slots = [
        (time(8, 0), time(10, 0)),   # 8:00 - 10:00 AM
        (time(10, 0), time(12, 0)),  # 10:00 AM - 12:00 PM
        (time(12, 0), time(14, 0)),  # 12:00 - 2:00 PM
        (time(14, 0), time(16, 0)),  # 2:00 - 4:00 PM
        (time(16, 0), time(18, 0)),  # 4:00 - 6:00 PM
    ]

    slots = []
    skipped_due_to_conflicts = 0

    # Organize rooms by type for efficient lookup
    classrooms = [r for r in rooms if r.room_type == 'classroom']
    labs = [r for r in rooms if r.room_type == 'lab']
    lecture_halls = [r for r in rooms if r.room_type == 'lecture_hall']

    for timetable in timetables:
        print(f"\n{timetable.name}:")

        # Get courses for this department and semester
        dept_courses = [c for c in courses
                       if c.department_id == timetable.department_id
                       and c.semester == timetable.semester]

        if not dept_courses:
            print("  [INFO] No courses found for this timetable")
            continue

        scheduled_count = 0
        conflict_count = 0

        for course in dept_courses:
            sessions_needed = course.weekly_sessions
            sessions_scheduled = 0
            attempts = 0
            max_attempts = 100  # Increased attempts for better coverage

            while sessions_scheduled < sessions_needed and attempts < max_attempts:
                attempts += 1

                # Random day (0-4 for Mon-Fri)
                day = random.randint(0, 4)

                # Random time slot
                start_time, end_time = random.choice(time_slots)

                # Choose appropriate room based on course code and requirements
                if course.code.startswith(('CS', 'ENG', 'CHEM', 'PHY', 'BIO')) and any(
                    keyword in course.name.lower() for keyword in ['lab', 'laboratory', 'practical']
                ):
                    suitable_rooms = labs if labs else classrooms
                elif course.code.endswith(('101', '102')):  # Introductory courses might need larger rooms
                    suitable_rooms = lecture_halls + classrooms
                else:
                    suitable_rooms = classrooms

                if not suitable_rooms:
                    suitable_rooms = rooms  # Fallback to all rooms

                # Try to find a room without conflicts
                room_found = False
                random.shuffle(suitable_rooms)  # Randomize to distribute load

                for room in suitable_rooms:
                    # Check for room conflicts
                    if conflict_detector.has_room_conflict(
                        timetable.id, day, start_time, end_time, room.id
                    ):
                        continue

                    # Check for teacher conflicts
                    if conflict_detector.has_teacher_conflict(
                        timetable.id, day, start_time, end_time, course.teacher_id
                    ):
                        continue

                    # No conflicts found - create the slot
                    day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
                    slot = TimeTableSlot(
                        timetable_id=timetable.id,
                        course_id=course.id,
                        room_id=room.id,
                        day_of_week=day,
                        start_time=start_time,
                        end_time=end_time,
                        notes=f"Instructor: {course.teacher.name if course.teacher else 'TBA'}"
                    )
                    db.session.add(slot)
                    db.session.flush()  # Get slot ID

                    # Register slot to track conflicts
                    conflict_detector.register_slot(
                        timetable.id, day, start_time, room.id,
                        course.teacher_id, course.id, slot.id
                    )

                    slots.append(slot)
                    sessions_scheduled += 1
                    scheduled_count += 1
                    room_found = True

                    # print(f"  [SCHEDULE] {course.code} - {day_names[day]} {start_time} in {room.name}")
                    break

                if not room_found:
                    conflict_count += 1

            if sessions_scheduled < sessions_needed:
                print(f"  [WARNING] {course.code}: Only scheduled {sessions_scheduled}/{sessions_needed} sessions")

        print(f"  [SUMMARY] Scheduled: {scheduled_count} slots, Conflicts avoided: {conflict_count}")

    db.session.commit()
    print(f"\nTotal TimeTable Slots: {len(slots)}")
    print(f"Total Conflicts Avoided: {skipped_due_to_conflicts}")
    return slots


def print_summary(admins, departments, teachers, rooms, courses, timetables, slots):
    """Print comprehensive summary of seeded data"""
    print("\n" + "=" * 70)
    print("DATABASE SEEDING SUMMARY")
    print("=" * 70)

    print("\nRecords Created:")
    print(f"  Admins:              {len(admins)}")
    print(f"  Departments:         {len(departments)}")
    print(f"  Teachers:            {len(teachers)}")
    print(f"  Rooms:               {len(rooms)}")
    print(f"  Courses:             {len(courses)}")
    print(f"  Timetables:          {len(timetables)}")
    print(f"  TimeTable Slots:     {len(slots)}")

    # Calculate some statistics
    if rooms:
        classrooms = sum(1 for r in rooms if r.room_type == 'classroom')
        labs = sum(1 for r in rooms if r.room_type == 'lab')
        halls = sum(1 for r in rooms if r.room_type == 'lecture_hall')
        print(f"\nRoom Breakdown:")
        print(f"  Classrooms:          {classrooms}")
        print(f"  Laboratories:        {labs}")
        print(f"  Lecture Halls:       {halls}")

    if slots:
        print(f"\nScheduling Statistics:")
        print(f"  Average slots/timetable: {len(slots) // len(timetables) if timetables else 0}")

        # Count slots per day
        day_counts = defaultdict(int)
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for slot in slots:
            day_counts[slot.day_of_week] += 1

        print(f"  Slots per day:")
        for day_num in sorted(day_counts.keys()):
            print(f"    {day_names[day_num]}: {day_counts[day_num]}")

    print("\n" + "-" * 70)
    print("ADMIN LOGIN CREDENTIALS")
    print("-" * 70)
    print("Username: admin     | Password: admin123     | Role: super_admin")
    print("Username: registrar | Password: registrar123 | Role: admin")
    print("Username: scheduler | Password: scheduler123 | Role: admin")
    print("-" * 70)

    print("\nDatabase seeding completed successfully!")
    print("You can now start the application and test the API.")
    print("\nQuick Start:")
    print("  1. Start the server: flask run")
    print("  2. Login: POST /api/auth/login")
    print("  3. View departments: GET /api/departments")
    print("=" * 70 + "\n")


def main():
    """Main seeding function"""
    print("\n" + "=" * 70)
    print("TIMETABLE MANAGER - ADVANCED DATABASE SEEDING")
    print("=" * 70)
    print("This script will populate the database with realistic data")
    print("including comprehensive conflict detection and validation.")
    print("=" * 70)

    # Create Flask app
    app = create_app()

    with app.app_context():
        try:
            # Clear existing data
            clear_database()

            # Seed data in correct order
            admins = seed_admins()
            departments = seed_departments()
            teachers = seed_teachers(departments)
            levels = seed_levels()
            rooms = seed_rooms()
            courses = seed_courses(departments, teachers, levels)
            timetables = seed_timetables(departments, admins)
            slots = seed_timetable_slots(timetables, courses, rooms)

            # Print summary
            print_summary(admins, departments, teachers, rooms, courses, timetables, slots)

        except Exception as e:
            print(f"\n{'=' * 70}")
            print("ERROR DURING SEEDING")
            print("=" * 70)
            print(f"An error occurred: {e}")
            print("\nPlease check your database connection and try again.")
            import traceback
            traceback.print_exc()
            return 1

    return 0


if __name__ == '__main__':
    exit(main())
