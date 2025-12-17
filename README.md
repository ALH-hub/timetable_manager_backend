# Timetable Manager Backend

A comprehensive RESTful API for managing academic timetables, built with Flask and PostgreSQL. This system handles departments, teachers, courses, rooms, and automatic scheduling with conflict detection.

**Version**: 1.0.0

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [System Architecture](#system-architecture)
4. [Technology Stack](#technology-stack)
5. [Project Structure](#project-structure)
6. [Installation](#installation)
7. [Configuration](#configuration)
8. [Database Setup](#database-setup)
9. [Running the Application](#running-the-application)
10. [API Documentation](#api-documentation)
11. [Authentication](#authentication)
12. [Database Models](#database-models)
13. [Testing](#testing)
14. [Development](#development)
15. [Deployment](#deployment)
16. [Troubleshooting](#troubleshooting)
17. [Contributing](#contributing)
18. [License](#license)

---

## Overview

The Timetable Manager Backend is a Flask-based RESTful API designed to manage academic scheduling for educational institutions. It provides a complete solution for managing departments, teachers, courses, classrooms, and generating conflict-free timetables.

### Key Capabilities

- **Department Management**: Organize academic departments with hierarchical structure
- **Teacher Administration**: Manage faculty members with specializations and department assignments
- **Course Catalog**: Maintain course information with teacher assignments and scheduling requirements
- **Room Management**: Track classrooms, labs, and lecture halls with capacity and availability
- **Timetable Generation**: Create and manage weekly schedules with automatic conflict detection
- **Authentication**: Secure JWT-based authentication for administrative access
- **Conflict Detection**: Automatic validation to prevent scheduling conflicts

---

## Features

### Core Functionality

- **CRUD Operations**: Complete Create, Read, Update, Delete operations for all entities
- **Relationship Management**: Handle complex relationships between entities (courses-teachers, slots-rooms)
- **Filtering & Search**: Advanced filtering capabilities across all endpoints
- **Pagination**: Efficient data retrieval with pagination support
- **Bulk Operations**: Bulk creation and updates for efficiency
- **Data Validation**: Comprehensive input validation and error handling

### Advanced Features

- **Automatic Conflict Detection**: Prevents double-booking of rooms and teachers
- **Schedule Cloning**: Duplicate timetables for recurring semesters
- **Status Management**: Draft, published, and archived states for timetables
- **Availability Checking**: Real-time room and teacher availability queries
- **Academic Calendar**: Support for multiple semesters and academic years
- **Audit Trail**: Timestamps for all records (created_at, updated_at)

### Security Features

- **JWT Authentication**: Token-based authentication with expiration
- **Password Hashing**: Secure password storage using Werkzeug
- **Token Refresh**: Automatic token refresh mechanism
- **CORS Support**: Configurable Cross-Origin Resource Sharing
- **Input Sanitization**: Protection against common security vulnerabilities

---

## System Architecture

### Architecture Pattern

The application follows the **MVC (Model-View-Controller)** pattern with Flask Blueprints:

```
Client -> Routes (Controller) -> Services (Business Logic) -> Models (Data Layer) -> Database
```

### Components

1. **Routes Layer**: HTTP endpoints and request handling (Flask Blueprints)
2. **Services Layer**: Business logic and JWT authentication
3. **Models Layer**: SQLAlchemy ORM models and database schema
4. **Configuration Layer**: Environment-specific settings and app initialization
5. **Migration Layer**: Database version control with Alembic

### Database Design

The system uses PostgreSQL with the following entity relationships:

- **One-to-Many**: Department -> Teachers, Department -> Courses, Level -> Courses, Teacher -> Courses
- **Many-to-One**: Course -> Teacher, Course -> Department, Course -> Level, TimeTableSlot -> Room
- **Cascade Operations**: Deleting a timetable removes all associated slots

### Entity Descriptions

- **Admin**: System administrators with JWT authentication
- **Department**: Academic departments organizing the institution
- **Teacher**: Faculty members assigned to departments
- **Level**: Student academic levels (Level 1, Level 2, Level 3, Master 1, Master 2)
- **Course**: Academic courses with department, teacher, and level assignments
- **Room**: Physical spaces (classrooms, labs, lecture halls) with capacity tracking
- **TimeTable**: Weekly schedules for departments with status management
- **TimeTableSlot**: Individual time slots linking courses to rooms and times

---

## Technology Stack

### Core Technologies

- **Python**: 3.8+
- **Flask**: 3.1.1 - Web framework
- **PostgreSQL**: 12+ - Relational database
- **SQLAlchemy**: 2.0.41 - ORM
- **Alembic**: 1.16.1 - Database migrations

### Key Dependencies

| Package          | Version | Purpose               |
| ---------------- | ------- | --------------------- |
| Flask            | 3.1.1   | Web framework         |
| Flask-SQLAlchemy | 3.1.1   | ORM integration       |
| Flask-Migrate    | 4.1.0   | Database migrations   |
| Flask-CORS       | Latest  | Cross-origin support  |
| PyJWT            | 2.10.1  | JWT authentication    |
| psycopg2-binary  | 2.9.11  | PostgreSQL adapter    |
| python-dotenv    | 1.1.0   | Environment variables |
| Werkzeug         | 3.1.3   | Security utilities    |

### Development Tools

- **Git**: Version control
- **Virtual Environment**: Python dependency isolation
- **Flask CLI**: Database migrations and management
- **Makefile**: Task automation (optional)

---

## Project Structure

```
timetable_manager_backend/
├── .env                          # Environment variables (not in git)
├── .flaskenv                     # Flask-specific environment variables
├── .gitignore                    # Git ignore rules
├── app.py                        # Root-level application entry point
├── requirements.txt              # Python dependencies
├── seed.py                       # Quick seed wrapper (backward compatibility)
├── README.md                     # This file
├── API_ROUTES.md                 # Complete API documentation
├── MIGRATIONS_GUIDE.md           # Database migration guide
├── PROJECT_EVALUATION.md         # Project structure evaluation
│
├── migrations/                   # Database migration files
│   ├── alembic.ini              # Alembic configuration
│   ├── env.py                   # Migration environment
│   ├── script.py.mako           # Migration template
│   └── versions/                # Migration versions
│
├── scripts/                      # Utility scripts
│   ├── __init__.py              # Package initialization
│   ├── README.md                # Scripts documentation
│   └── seed_database.py         # Advanced database seeding with conflict detection
│
└── src/                          # Main application code
    ├── __init__.py              # Package initialization
    ├── app.py                   # Application factory (deprecated, use root app.py)
    │
    ├── config/                   # Configuration management
    │   ├── __init__.py          # Config exports
    │   ├── db.py                # Database configuration
    │   ├── env.py               # Environment loader
    │   └── flask.py             # Flask app factory
    │
    ├── models/                   # SQLAlchemy models
    │   ├── __init__.py          # Model exports
    │   ├── admin.py             # Admin user model
    │   ├── classroom.py         # Room model
    │   ├── course.py            # Course model
    │   ├── department.py        # Department model
    │   ├── level.py             # Student level model
    │   ├── teacher.py           # Teacher model
    │   └── timetable.py         # TimeTable and TimeTableSlot models
    │
    ├── routes/                   # API endpoints (Blueprints)
    │   ├── __init__.py          # Blueprint registration
    │   ├── auth.py              # Authentication endpoints
    │   ├── courses.py           # Course management
    │   ├── departments.py       # Department management
    │   ├── levels.py            # Level management
    │   ├── rooms.py             # Room management
    │   ├── slots.py             # TimeTable slot management
    │   ├── teachers.py          # Teacher management
    │   └── timetables.py        # Timetable management
    │
    └── services/                 # Business logic layer
        ├── __init__.py          # Service exports
        ├── jwt_service.py       # JWT authentication service
        ├── level_service.py     # Level business logic
        ├── department_service.py # Department business logic
        ├── teacher_service.py   # Teacher business logic
        ├── course_service.py    # Course business logic
        ├── room_service.py      # Room business logic
        ├── timetable_service.py # Timetable business logic
        └── slot_service.py      # Slot business logic
```

### Directory Descriptions

#### `/src/config/`

Contains all configuration-related code:

- **db.py**: SQLAlchemy database instance and configuration class
- **env.py**: Loads environment variables from .env file
- **flask.py**: Flask application factory with initialization

#### `/src/models/`

SQLAlchemy ORM models defining the database schema:

- **admin.py**: Admin users with password hashing
- **department.py**: Academic departments
- **teacher.py**: Faculty members
- **classroom.py**: Physical rooms (classrooms, labs, lecture halls)
- **course.py**: Academic courses with level assignments
- **level.py**: Student levels (Level 1, 2, 3, Master 1, Master 2)
- **timetable.py**: Timetables and individual time slots

#### `/src/routes/`

Flask Blueprints for API endpoints:

- Each file handles HTTP request/response and delegates to services
- All routes are protected with JWT authentication (except auth endpoints)
- Routes are thin controllers that validate input and format output
- Business logic is handled by the service layer

#### `/src/services/`

Business logic layer containing all domain logic:

- **jwt_service.py**: Token generation, validation, and authentication decorators
- **level_service.py**: Level CRUD operations and default level initialization
- **department_service.py**: Department management and serialization
- **teacher_service.py**: Teacher management, schedule retrieval, and serialization
- **course_service.py**: Course management, teacher assignment, and serialization
- **room_service.py**: Room management, availability checking, and schedule retrieval
- **timetable_service.py**: Timetable CRUD, publishing, archiving, cloning, and statistics
- **slot_service.py**: Slot management, conflict detection, and bulk operations

The service layer follows a consistent pattern:

- Service functions return tuples of (result, error_message)
- All database operations are encapsulated in services
- Services handle validation, business rules, and data transformation
- Serialization functions convert models to dictionaries for JSON responses

---

## Installation

### Prerequisites

- **Python**: 3.8 or higher (for local development)
- **PostgreSQL**: 12 or higher (for local development)
- **Docker**: 20.10+ and Docker Compose 2.0+ (recommended)
- **Git**: For cloning the repository
- **pip**: Python package manager
- **virtualenv**: For creating isolated Python environments

### Method 1: Docker Installation (Recommended)

The easiest way to get started is using Docker Compose:

#### Step 1: Clone the Repository

```bash
git clone https://github.com/ALH-hub/timetable_manager_backend.git
cd timetable_manager_backend
```

#### Step 2: Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` with your preferred settings (or use defaults):

```env
# Database Configuration
POSTGRES_USER=oumate
POSTGRES_PASSWORD=oumate
POSTGRES_DB=timetableDB
DB_PORT=5433
DB_HOST=db

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_PORT=5000

# Secret Key (CHANGE THIS IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-in-production
```

#### Step 3: Build and Start Containers

```bash
# Build and start all services
docker compose up --build

# Or run in detached mode
docker compose up --build -d
```

#### Step 4: Verify Installation

```bash
# Check container status
docker compose ps

# View logs
docker compose logs web

# Test API endpoint
curl http://localhost:5000/
```

Expected response: `{"message": "Welcome to the Timetable Manager Backend!"}`

#### Step 5: Initialize Database (First Time Only)

The database migrations run automatically on container start. To seed with sample data:

```bash
# Access the web container
docker compose exec web bash

# Run seeding script
python3 scripts/seed_database.py

# Exit container
exit
```

### Method 2: Local Installation (Without Docker)

#### Step 1: Clone the Repository

```bash
git clone https://github.com/ALH-hub/timetable_manager_backend.git
cd timetable_manager_backend
```

#### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your database connection:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/timetable_manager
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_ENV=development
FLASK_DEBUG=1
```

#### Step 5: Set Up Database

```bash
# Create database (if not exists)
createdb timetable_manager

# Initialize migrations
flask db upgrade

# Seed database (optional)
python3 scripts/seed_database.py
```

#### Step 6: Verify Installation

```bash
python3 -c "import flask; print(f'Flask version: {flask.__version__}')"
```

Expected output: `Flask version: 3.1.1`

---

## Configuration

### Environment Variables

The application uses environment variables for configuration. Docker Compose automatically reads from a `.env` file in the project root.

#### Using Docker Compose

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
# Database Configuration
POSTGRES_USER=oumate
POSTGRES_PASSWORD=oumate
POSTGRES_DB=timetableDB
DB_PORT=5433
DB_HOST=db

# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_PORT=5000

# Secret Key (CHANGE THIS IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-in-production
```

#### Local Development (Without Docker)

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/timetable_manager

# Flask Configuration
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_ENV=development
FLASK_DEBUG=1

# JWT Configuration (optional, uses SECRET_KEY if not set)
JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production
JWT_EXPIRATION_HOURS=24

# CORS Configuration (optional)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Flask Environment (.flaskenv)

The `.flaskenv` file is already configured:

```bash
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
```

### Configuration Parameters

| Variable             | Description                          | Required | Default     |
| -------------------- | ------------------------------------ | -------- | ----------- |
| DATABASE_URL         | PostgreSQL connection string         | Yes      | None        |
| SECRET_KEY           | Flask secret key                     | Yes      | None        |
| JWT_SECRET_KEY       | JWT token signing key                | Yes      | None        |
| JWT_EXPIRATION_HOURS | Token expiration time                | No       | 24          |
| FLASK_ENV            | Environment (development/production) | No       | development |
| FLASK_DEBUG          | Debug mode                           | No       | 1           |
| CORS_ORIGINS         | Allowed origins for CORS             | No       | \*          |

### Security Considerations

1. **Never commit .env to version control** (already in .gitignore)
2. **Use strong, random keys** for SECRET_KEY and JWT_SECRET_KEY
3. **Change default keys** before deploying to production
4. **Use environment-specific .env files** for different environments

### Generating Secure Keys

```bash
# Generate a secure random key
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## Database Setup

### Step 1: Create PostgreSQL Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE timetable_manager;

# Create user (optional)
CREATE USER timetable_user WITH PASSWORD 'secure_password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE timetable_manager TO timetable_user;

# Exit
\q
```

### Step 2: Update .env File

```bash
DATABASE_URL=postgresql://timetable_user:secure_password@localhost:5432/timetable_manager
```

### Step 3: Initialize Migrations

If migrations folder doesn't exist:

```bash
flask db init
```

### Step 4: Create Initial Migration

```bash
flask db migrate -m "Initial migration: create all tables"
```

### Step 5: Apply Migrations

```bash
flask db upgrade
```

### Step 6: Verify Tables

```bash
psql -d timetable_manager -c "\dt"
```

Expected tables:

- admin
- department
- teacher
- room
- course
- time_table
- timetable_slot
- alembic_version

### Step 7: Seed Database (Optional)

Populate the database with sample data using the advanced seeding script:

```bash
# Using the main script with conflict detection
python3 scripts/seed_database.py

# Or using the quick wrapper
python3 seed.py
```

The advanced seeding script includes:

- **Comprehensive Conflict Detection**: Prevents room and teacher double-booking
- **Smart Room Assignment**: Labs for CS/Engineering, lecture halls for large classes
- **Duplicate Prevention**: Checks for existing records before creation
- **Detailed Logging**: Shows what was created vs. skipped

This creates:

- 3 admin users (admin/admin123, registrar/registrar123, scheduler/scheduler123)
- 7 departments (CS, Math, Physics, Chemistry, Biology, Engineering, Business)
- 42 teachers (6 per department with unique emails)
- 35 rooms (20 classrooms, 10 labs, 5 lecture halls)
- 50+ courses with realistic course codes and assigned teachers
- 14 timetables (Fall 2024 and Spring 2025 for each department)
- 300+ scheduled time slots with no conflicts

For detailed information about seeding, see [scripts/README.md](scripts/README.md)

---

## Running the Application

### Method 1: Using Docker Compose (Recommended)

```bash
# Start all services (database + web)
docker compose up

# Start in detached mode (background)
docker compose up -d

# View logs
docker compose logs -f web

# Stop services
docker compose down

# Stop and remove volumes (WARNING: deletes database)
docker compose down -v

# Rebuild after code changes
docker compose up --build
```

**Accessing the Application:**

- **Base URL**: http://localhost:5000 (or port specified in FLASK_PORT)
- **Health Check**: http://localhost:5000/
- **API Prefix**: http://localhost:5000/api
- **Database**: localhost:5433 (or port specified in DB_PORT)

### Method 2: Using Flask CLI (Local Development)

```bash
# Activate virtual environment
source venv/bin/activate

# Ensure PostgreSQL is running and .env is configured
# Run development server
flask run

# Run on specific host/port
flask run --host=0.0.0.0 --port=8000

# Run with debugger and reloader
flask run --debug
```

### Method 3: Using Python Directly

```bash
python3 app.py
```

### Accessing the Application

- **Base URL**: http://127.0.0.1:5000
- **Health Check**: http://127.0.0.1:5000/
- **API Prefix**: http://127.0.0.1:5000/api

### Development Server Features

- **Auto-reload**: Automatically restarts on code changes (debug mode)
- **Interactive Debugger**: In-browser debugger for exceptions (debug mode)
- **Request Logging**: Logs all incoming requests
- **Error Pages**: Detailed error pages in development
- **Database Migrations**: Automatically run on container start (Docker)

### Docker Commands Reference

```bash
# View running containers
docker compose ps

# View logs
docker compose logs web
docker compose logs db

# Execute commands in container
docker compose exec web bash
docker compose exec web flask shell
docker compose exec db psql -U oumate -d timetableDB

# Restart services
docker compose restart web

# Rebuild specific service
docker compose build web
docker compose up -d web
```

### Production Considerations

For production deployment, use a WSGI server:

```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Using uWSGI
pip install uwsgi
uwsgi --http :8000 --wsgi-file app.py --callable app --processes 4
```

**Production Docker Setup:**

Update `docker-compose.yml` command to use Gunicorn:

```yaml
command: >
  bash -c "
    flask db upgrade || true;
    exec gunicorn -w 4 -b 0.0.0.0:5000 app:app;
  "
```

---

## API Documentation

### Base URL

```
http://127.0.0.1:5000/api
```

### Authentication

All endpoints (except `/api/auth/login` and `/api/auth/register`) require JWT authentication.

Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

### API Endpoints Overview

#### Authentication (`/api/auth`)

| Method | Endpoint         | Description                  | Auth Required |
| ------ | ---------------- | ---------------------------- | ------------- |
| POST   | /login           | Login and receive JWT token  | No            |
| POST   | /register        | Create new admin account     | No            |
| GET    | /me              | Get current admin profile    | Yes           |
| PUT    | /me              | Update current admin profile | Yes           |
| POST   | /change-password | Change admin password        | Yes           |

#### Departments (`/api/departments`)

| Method | Endpoint      | Description                |
| ------ | ------------- | -------------------------- |
| GET    | /             | List all departments       |
| GET    | /:id          | Get department by ID       |
| POST   | /             | Create new department      |
| PUT    | /:id          | Update department          |
| DELETE | /:id          | Delete department          |
| GET    | /:id/teachers | Get teachers in department |
| GET    | /:id/courses  | Get courses in department  |

#### Teachers (`/api/teachers`)

| Method | Endpoint      | Description                   |
| ------ | ------------- | ----------------------------- |
| GET    | /             | List all teachers             |
| GET    | /:id          | Get teacher by ID             |
| POST   | /             | Create new teacher            |
| PUT    | /:id          | Update teacher                |
| DELETE | /:id          | Delete teacher                |
| GET    | /:id/courses  | Get courses taught by teacher |
| GET    | /:id/schedule | Get teacher's schedule        |

#### Rooms (`/api/rooms`)

| Method | Endpoint            | Description             |
| ------ | ------------------- | ----------------------- |
| GET    | /                   | List all rooms          |
| GET    | /:id                | Get room by ID          |
| POST   | /                   | Create new room         |
| PUT    | /:id                | Update room             |
| DELETE | /:id                | Delete room             |
| GET    | /:id/schedule       | Get room schedule       |
| POST   | /check-availability | Check room availability |

#### Courses (`/api/courses`)

| Method | Endpoint              | Description                |
| ------ | --------------------- | -------------------------- |
| GET    | /                     | List all courses           |
| GET    | /:id                  | Get course by ID           |
| POST   | /                     | Create new course          |
| PUT    | /:id                  | Update course              |
| DELETE | /:id                  | Delete course              |
| PUT    | /:id/assign-teacher   | Assign teacher to course   |
| DELETE | /:id/unassign-teacher | Remove teacher from course |

#### Timetables (`/api/timetables`)

| Method | Endpoint     | Description          |
| ------ | ------------ | -------------------- |
| GET    | /            | List all timetables  |
| GET    | /:id         | Get timetable by ID  |
| POST   | /            | Create new timetable |
| PUT    | /:id         | Update timetable     |
| DELETE | /:id         | Delete timetable     |
| POST   | /:id/publish | Publish timetable    |
| POST   | /:id/archive | Archive timetable    |
| POST   | /:id/clone   | Clone timetable      |

#### TimeTable Slots (`/api/slots`)

| Method | Endpoint        | Description                    |
| ------ | --------------- | ------------------------------ |
| GET    | /               | List all slots                 |
| GET    | /:id            | Get slot by ID                 |
| POST   | /               | Create new slot                |
| POST   | /bulk           | Create multiple slots          |
| PUT    | /:id            | Update slot                    |
| DELETE | /:id            | Delete slot                    |
| POST   | /check-conflict | Check for scheduling conflicts |

### Example API Requests

#### Login

```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Response:

```json
{
  "message": "Login successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "admin": {
    "id": 1,
    "username": "admin",
    "email": "admin@university.edu",
    "role": "super_admin"
  }
}
```

#### Get All Departments

```bash
curl -X GET http://127.0.0.1:5000/api/departments \
  -H "Authorization: Bearer <your_token>"
```

#### Create New Course

```bash
curl -X POST http://127.0.0.1:5000/api/courses \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Advanced Algorithms",
    "code": "CS401",
    "department_id": 1,
    "teacher_id": 5,
    "weekly_sessions": 3,
    "semester": "Fall",
    "year": 2024
  }'
```

### Complete API Documentation

For detailed API documentation including all request/response formats, see [API_ROUTES.md](API_ROUTES.md).

---

## Authentication

### JWT Token System

The application uses JSON Web Tokens (JWT) for stateless authentication.

### Token Structure

```json
{
  "admin_id": 1,
  "exp": 1699920000,
  "iat": 1699833600,
  "type": "access"
}
```

### Token Lifecycle

1. **Login**: User submits credentials, receives JWT token
2. **Authorization**: Token included in Authorization header for subsequent requests
3. **Validation**: Server validates token on each request
4. **Expiration**: Token expires after configured duration (default: 24 hours)
5. **Refresh**: Client can request new token before expiration

### Using JWT Tokens

#### In Python/Requests

```python
import requests

# Login
response = requests.post('http://127.0.0.1:5000/api/auth/login', json={
    'username': 'admin',
    'password': 'admin123'
})
token = response.json()['token']

# Use token
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://127.0.0.1:5000/api/departments', headers=headers)
```

#### In JavaScript/Fetch

```javascript
// Login
const loginResponse = await fetch('http://127.0.0.1:5000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' }),
});
const { token } = await loginResponse.json();

// Use token
const response = await fetch('http://127.0.0.1:5000/api/departments', {
  headers: { Authorization: `Bearer ${token}` },
});
```

#### In cURL

```bash
TOKEN="your_token_here"
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/departments
```

### Token Security

- Tokens are signed with JWT_SECRET_KEY
- Tokens have expiration time (configurable)
- Tokens are timezone-aware (UTC)
- Invalid tokens return 401 Unauthorized
- Expired tokens return 401 with specific message

---

## Database Models

### Admin

Administrator users with authentication capabilities.

```python
class Admin(db.Model):
    id: Integer (Primary Key)
    username: String(80), Unique, Not Null
    password_hash: String(255), Not Null
    email: String(120), Unique, Not Null
    role: String(20), Default='admin'
    created_at: DateTime
    updated_at: DateTime
```

**Relationships**:

- One-to-Many with TimeTable (as creator)

### Department

Academic departments organizing courses and teachers.

```python
class Department(db.Model):
    id: Integer (Primary Key)
    name: String(100), Not Null
    code: String(10), Unique
    head: String(100)
    contact_email: String(120)
    created_at: DateTime
    updated_at: DateTime
```

**Relationships**:

- One-to-Many with Teacher
- One-to-Many with Course
- One-to-Many with TimeTable

### Teacher

Faculty members teaching courses.

```python
class Teacher(db.Model):
    id: Integer (Primary Key)
    name: String(100), Not Null
    email: String(120), Unique, Not Null
    phone: String(20)
    department_id: Integer (Foreign Key)
    specialization: String(100)
    is_active: Boolean, Default=True
    created_at: DateTime
    updated_at: DateTime
```

**Relationships**:

- Many-to-One with Department
- One-to-Many with Course

### Room

Physical spaces for classes (classrooms, labs, lecture halls).

```python
class Room(db.Model):
    id: Integer (Primary Key)
    name: String(50), Unique, Not Null
    room_type: String(30), Not Null  # classroom, lab, lecture_hall
    capacity: Integer, Not Null
    is_available: Boolean, Default=True
    created_at: DateTime
    updated_at: DateTime
```

**Relationships**:

- One-to-Many with TimeTableSlot

### Course

Academic courses with scheduling requirements.

```python
class Course(db.Model):
    id: Integer (Primary Key)
    name: String(100), Not Null
    code: String(20), Unique, Not Null
    department_id: Integer (Foreign Key), Not Null
    teacher_id: Integer (Foreign Key)
    weekly_sessions: Integer, Default=1
    semester: String(20)  # Fall, Spring, Summer
    year: Integer
    is_active: Boolean, Default=True
    created_at: DateTime
    updated_at: DateTime
```

**Relationships**:

- Many-to-One with Department
- Many-to-One with Teacher
- One-to-Many with TimeTableSlot

### TimeTable

Container for weekly schedules.

```python
class TimeTable(db.Model):
    id: Integer (Primary Key)
    name: String(100), Not Null
    department_id: Integer (Foreign Key), Not Null
    week_start: Date, Not Null
    week_end: Date
    academic_year: String(20)  # 2024-2025
    semester: String(20)  # Fall, Spring, Summer
    status: String(20), Default='draft'  # draft, published, archived
    created_by: Integer (Foreign Key)
    created_at: DateTime
    updated_at: DateTime
```

**Relationships**:

- Many-to-One with Department
- Many-to-One with Admin (creator)
- One-to-Many with TimeTableSlot (cascade delete)

### TimeTableSlot

Individual scheduled time slots.

```python
class TimeTableSlot(db.Model):
    id: Integer (Primary Key)
    timetable_id: Integer (Foreign Key), Not Null
    course_id: Integer (Foreign Key), Not Null
    room_id: Integer (Foreign Key), Not Null
    day_of_week: Integer, Not Null  # 0=Monday, 6=Sunday
    start_time: Time, Not Null
    end_time: Time, Not Null
    notes: Text
    created_at: DateTime
    updated_at: DateTime

    Constraint: start_time < end_time
```

**Relationships**:

- Many-to-One with TimeTable
- Many-to-One with Course
- Many-to-One with Room

**Properties**:

- `day_name`: Returns human-readable day name

---

## Testing

### Manual Testing

#### Test Authentication

```bash
# Register new admin
curl -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "email": "test@test.com", "password": "test123"}'

# Login
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}'
```

#### Test CRUD Operations

```bash
# Get all departments
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/departments

# Create department
curl -X POST http://127.0.0.1:5000/api/departments \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Dept", "code": "TEST"}'

# Update department
curl -X PUT http://127.0.0.1:5000/api/departments/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Name"}'

# Delete department
curl -X DELETE http://127.0.0.1:5000/api/departments/1 \
  -H "Authorization: Bearer $TOKEN"
```

### Testing with Postman

1. Import API endpoints from API_ROUTES.md
2. Set up environment variables for base URL and token
3. Create test collections for each resource
4. Use Postman tests for automated validation

### Testing with Python

Create a test script:

```python
import requests

BASE_URL = 'http://127.0.0.1:5000/api'

# Login
response = requests.post(f'{BASE_URL}/auth/login', json={
    'username': 'admin',
    'password': 'admin123'
})
token = response.json()['token']
headers = {'Authorization': f'Bearer {token}'}

# Test departments
response = requests.get(f'{BASE_URL}/departments', headers=headers)
print(f'Departments: {len(response.json())}')

# Test courses
response = requests.get(f'{BASE_URL}/courses', headers=headers)
print(f'Courses: {len(response.json())}')
```

### Database Testing

```bash
# Check record counts
psql -d timetable_manager -c "
  SELECT
    'admin' as table_name, COUNT(*) FROM admin
  UNION ALL
  SELECT 'department', COUNT(*) FROM department
  UNION ALL
  SELECT 'teacher', COUNT(*) FROM teacher
  UNION ALL
  SELECT 'room', COUNT(*) FROM room
  UNION ALL
  SELECT 'course', COUNT(*) FROM course
  UNION ALL
  SELECT 'time_table', COUNT(*) FROM time_table
  UNION ALL
  SELECT 'timetable_slot', COUNT(*) FROM timetable_slot;
"
```

---

## Development

### Development Workflow

1. **Create Feature Branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes**

   - Edit code in `src/` directory
   - Follow existing code structure and patterns

3. **Test Changes**

   ```bash
   flask run
   # Test endpoints manually or with scripts
   ```

4. **Create Migration (if database changes)**

   ```bash
   flask db migrate -m "Description of changes"
   flask db upgrade
   ```

5. **Commit Changes**

   ```bash
   git add .
   git commit -m "Description of changes"
   ```

6. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Style Guidelines

- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused
- Use type hints where appropriate

### Adding New Features

#### Adding a New Model

1. Create model file in `src/models/`
2. Define SQLAlchemy model class
3. Add to `src/models/__init__.py` exports
4. Create migration: `flask db migrate -m "Add new model"`
5. Apply migration: `flask db upgrade`

#### Adding New Routes

1. Create route file in `src/routes/`
2. Define Flask Blueprint
3. Add CRUD endpoints with `@token_required` decorator
4. Register blueprint in `src/routes/__init__.py`
5. Document endpoints in API_ROUTES.md

#### Adding New Service

1. Create service file in `src/services/`
2. Implement business logic functions
3. Export from `src/services/__init__.py`
4. Import and use in routes

### Database Migrations

#### Create Migration

```bash
flask db migrate -m "Description of changes"
```

#### Apply Migration

```bash
flask db upgrade
```

#### Rollback Migration

```bash
flask db downgrade
```

#### View Migration History

```bash
flask db history
```

#### View Current Version

```bash
flask db current
```

### Debugging

#### Enable Debug Mode

Debug mode is enabled by default in development:

```bash
FLASK_DEBUG=1
```

#### View Logs

```bash
# Flask logs to stdout by default
flask run

# Redirect to file
flask run > app.log 2>&1
```

#### Interactive Debugging

Use Flask shell for interactive debugging:

```bash
flask shell
```

```python
>>> from src.models import Department, Teacher
>>> departments = Department.query.all()
>>> print(len(departments))
```

#### Database Inspection

```bash
# Connect to database
psql -d timetable_manager

# List tables
\dt

# Describe table
\d department

# Query data
SELECT * FROM department;
```

---

## Deployment

### Production Checklist

- [ ] Change SECRET_KEY and JWT_SECRET_KEY to strong random values
- [ ] Set FLASK_ENV=production
- [ ] Set FLASK_DEBUG=0
- [ ] Configure proper CORS_ORIGINS
- [ ] Use production database with backups
- [ ] Use WSGI server (Gunicorn/uWSGI)
- [ ] Set up reverse proxy (Nginx/Apache)
- [ ] Enable HTTPS with SSL certificate
- [ ] Configure proper logging
- [ ] Set up monitoring and error tracking
- [ ] Implement rate limiting
- [ ] Configure database connection pooling

### Deployment with Gunicorn

1. **Install Gunicorn**

   ```bash
   pip install gunicorn
   ```

2. **Create Gunicorn Configuration**

   ```python
   # gunicorn.conf.py
   bind = "0.0.0.0:8000"
   workers = 4
   worker_class = "sync"
   timeout = 120
   accesslog = "access.log"
   errorlog = "error.log"
   loglevel = "info"
   ```

3. **Run with Gunicorn**
   ```bash
   gunicorn -c gunicorn.conf.py app:app
   ```

### Deployment with Docker

The project includes a complete Docker setup with `Dockerfile` and `docker-compose.yml`.

1. **Configure Environment Variables**

   Copy `.env.example` to `.env` and update with production values:

   ```bash
   cp .env.example .env
   # Edit .env with production credentials
   ```

2. **Build and Deploy**

   ```bash
   # Build and start services
   docker compose up --build -d

   # View logs
   docker compose logs -f

   # Check status
   docker compose ps
   ```

3. **Production Configuration**

   For production, update `docker-compose.yml`:

   ```yaml
   services:
     web:
       # ... existing config ...
       environment:
         FLASK_ENV: production
         SECRET_KEY: ${SECRET_KEY} # Use strong secret from .env
       command: >
         bash -c "
           flask db upgrade || true;
           exec gunicorn -w 4 -b 0.0.0.0:5000 app:app;
         "
   ```

4. **Using Docker Compose**

   The included `docker-compose.yml` already configures:

   - PostgreSQL database service
   - Flask web application service
   - Volume persistence for database
   - Health checks and dependencies
   - Automatic migrations on startup

### Environment-Specific Configuration

Create separate .env files:

- `.env.development` - Development settings
- `.env.production` - Production settings
- `.env.test` - Test environment settings

Load appropriate file based on environment:

```python
from dotenv import load_dotenv
import os

env = os.getenv('FLASK_ENV', 'development')
load_dotenv(f'.env.{env}')
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Troubleshooting

### Common Issues

#### 1. "ModuleNotFoundError: No module named 'src'"

**Solution**: Ensure you're in the project root directory and virtual environment is activated.

```bash
source venv/bin/activate
cd /path/to/timetable_manager_backend
```

#### 2. "FATAL: database 'timetable_manager' does not exist"

**Solution**: Create the database.

```bash
psql -U postgres -c "CREATE DATABASE timetable_manager;"
```

#### 3. "psycopg2.OperationalError: FATAL: password authentication failed"

**Solution**: Check your DATABASE_URL in .env file. Ensure username/password are correct.

```bash
# Test connection
psql -d "postgresql://username:password@localhost:5432/timetable_manager"

# For Docker: Reset database volume if credentials changed
docker compose down -v
docker compose up --build
```

#### 4. "ImportError: cannot import name 'create_app'"

**Solution**: Check that `src/config/flask.py` exists and contains `create_app` function.

#### 5. "flask: command not found"

**Solution**: Install Flask and activate virtual environment.

```bash
source venv/bin/activate
pip install Flask
```

#### 6. "SQLAlchemy IntegrityError: duplicate key value"

**Solution**: Trying to create record with duplicate unique field. Check unique constraints.

#### 7. "401 Unauthorized" on API requests

**Solution**: Include valid JWT token in Authorization header.

```bash
# Get token first
TOKEN=$(curl -s -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.token')

# Use token
curl -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/departments
```

#### 8. Migration conflicts

**Solution**: Reset migrations if in development.

```bash
# Backup data first!
flask db downgrade base
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Database Issues

#### Reset Database Completely

```bash
# WARNING: This deletes all data!
psql -U postgres -c "DROP DATABASE timetable_manager;"
psql -U postgres -c "CREATE DATABASE timetable_manager;"
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
python3 seed_db.py
```

#### Check Database Connection

```python
python3 -c "
from src.config.flask import create_app
from src.config.db import db

app = create_app()
with app.app_context():
    try:
        db.session.execute('SELECT 1')
        print('Database connection successful')
    except Exception as e:
        print(f'Database connection failed: {e}')
"
```

### Performance Issues

#### Slow Queries

Enable SQL query logging:

```python
# In config/db.py
app.config['SQLALCHEMY_ECHO'] = True
```

#### Database Connection Pool

Configure connection pooling:

```python
# In config/db.py
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

---

## Contributing

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Guidelines

- Follow existing code style and structure
- Add tests for new features
- Update documentation (README, API_ROUTES.md)
- Create database migrations for schema changes
- Ensure all tests pass before submitting PR
- Write clear commit messages

### Code Review Process

1. Automated checks run on PR
2. Code review by maintainers
3. Address feedback
4. Approval and merge

---

## License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2024 ALHADJI OUMATE

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## Appendix

### Useful Commands Reference

```bash
# Virtual Environment
python3 -m venv venv
source venv/bin/activate
deactivate

# Dependencies
pip install -r requirements.txt
pip freeze > requirements.txt

# Flask Commands
flask run
flask shell
flask routes

# Database Migrations
flask db init
flask db migrate -m "message"
flask db upgrade
flask db downgrade
flask db history
flask db current

# Database Management
python3 seed_db.py
psql -d timetable_manager

# Git Commands
git status
git add .
git commit -m "message"
git push origin branch-name

# Testing
curl -X GET http://127.0.0.1:5000/api/departments
psql -d timetable_manager -c "SELECT COUNT(*) FROM department;"
```

### Project Resources

- **API Documentation**: [API_ROUTES.md](API_ROUTES.md)
- **Migration Guide**: [MIGRATIONS_GUIDE.md](MIGRATIONS_GUIDE.md)
- **Project Evaluation**: [PROJECT_EVALUATION.md](PROJECT_EVALUATION.md)
- **Seeding Guide**: SEEDING_GUIDE.md (if created)

### Contact

**Author**: ALHADJI OUMATE
**Student ID**: 22U2033
**Email**: Contact through repository issues

### Acknowledgments

- Flask documentation and community
- SQLAlchemy documentation
- PostgreSQL documentation
- All contributors and users of this project

---

**Last Updated**: December 17, 2025
**Version**: 1.0.0

---

## Docker Quick Start

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+

### Quick Start Commands

```bash
# 1. Clone repository
git clone <repository-url>
cd timetable_manager_backend

# 2. Copy environment file
cp .env.example .env

# 3. (Optional) Edit .env with your preferences

# 4. Start services
docker compose up --build

# 5. Access application
# API: http://localhost:5000
# Database: localhost:5433
```

### Common Docker Operations

```bash
# View logs
docker compose logs -f web

# Access database
docker compose exec db psql -U oumate -d timetableDB

# Run migrations manually
docker compose exec web flask db upgrade

# Seed database
docker compose exec web python3 scripts/seed_database.py

# Stop services
docker compose down

# Reset everything (WARNING: deletes data)
docker compose down -v
docker compose up --build
```
