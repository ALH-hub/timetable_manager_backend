# Timetable Manager Backend - API Routes Summary

This document provides an overview of all available API endpoints for the Timetable Manager Backend.

## Base URL

All routes are prefixed with `/api`

## Authentication

Most endpoints require JWT authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Route Groups

### 1. Authentication Routes (`/api/auth`)

#### `POST /api/auth/register`

Register a new admin user.

**Request Body:**

```json
{
  "username": "string (required)",
  "email": "string (required)",
  "password": "string (required)",
  "role": "string (optional, default: 'admin')"
}
```

#### `POST /api/auth/login`

Login admin user.

**Request Body:**

```json
{
  "username": "string (required)",
  "password": "string (required)"
}
```

#### `GET /api/auth/me`

Get current admin information.

**Query Parameters:** None

**Authentication:** Required

#### `PUT /api/auth/change-password`

Change admin password.

**Request Body:**

```json
{
  "current_password": "string (required)",
  "new_password": "string (required)"
}
```

**Authentication:** Required

#### `PUT /api/auth/update-profile`

Update admin profile.

**Request Body:**

```json
{
  "email": "string (optional)",
  "username": "string (optional)"
}
```

**Authentication:** Required

---

### 2. Department Routes (`/api/departments`)

#### `GET /api/departments/`

Get all departments.

**Query Parameters:** None

**Example:** `GET /api/departments/`

#### `POST /api/departments/`

Create a new department.

**Request Body:**

```json
{
  "name": "string (required)",
  "code": "string (optional)",
  "head": "string (optional)",
  "contact_email": "string (optional)"
}
```

**Authentication:** Required

#### `GET /api/departments/<id>`

Get specific department.

**Query Parameters:** None

**Example:** `GET /api/departments/1`

#### `PUT /api/departments/<id>`

Update department.

**Request Body:**

```json
{
  "name": "string (optional)",
  "code": "string (optional)",
  "head": "string (optional)",
  "contact_email": "string (optional)"
}
```

**Authentication:** Required

#### `DELETE /api/departments/<id>`

Delete department.

**Query Parameters:** None

**Authentication:** Required

#### `GET /api/departments/<id>/teachers`

Get department teachers.

**Query Parameters:** None

**Example:** `GET /api/departments/1/teachers`

**Authentication:** Required

#### `GET /api/departments/<id>/courses`

Get department courses.

**Query Parameters:** None

**Example:** `GET /api/departments/1/courses`

---

### 3. Teacher Routes (`/api/teachers`)

#### `GET /api/teachers/`

Get all teachers with optional filtering.

**Query Parameters:**

- `department_id` (integer, optional) - Filter by department ID
- `is_active` (boolean, optional) - Filter by active status

**Examples:**

- `GET /api/teachers/`
- `GET /api/teachers/?department_id=1`
- `GET /api/teachers/?is_active=true`
- `GET /api/teachers/?department_id=1&is_active=true`

**Authentication:** Required

#### `POST /api/teachers/`

Create a new teacher.

**Request Body:**

```json
{
  "name": "string (required)",
  "email": "string (required, unique)",
  "department_id": "integer (required)",
  "phone": "string (optional)",
  "specialization": "string (optional)",
  "is_active": "boolean (optional, default: true)"
}
```

**Authentication:** Required

#### `GET /api/teachers/<id>`

Get specific teacher.

**Query Parameters:** None

**Example:** `GET /api/teachers/1`

**Authentication:** Required

#### `PUT /api/teachers/<id>`

Update teacher.

**Request Body:**

```json
{
  "name": "string (optional)",
  "email": "string (optional)",
  "phone": "string (optional)",
  "department_id": "integer (optional)",
  "specialization": "string (optional)",
  "is_active": "boolean (optional)"
}
```

**Authentication:** Required

#### `DELETE /api/teachers/<id>`

Delete teacher.

**Query Parameters:** None

**Authentication:** Required

#### `GET /api/teachers/<id>/courses`

Get teacher's courses.

**Query Parameters:** None

**Example:** `GET /api/teachers/1/courses`

**Authentication:** Required

#### `GET /api/teachers/<id>/schedule`

Get teacher's schedule.

**Query Parameters:** None

**Example:** `GET /api/teachers/1/schedule`

**Authentication:** Required

---

### 4. Room Routes (`/api/rooms`)

#### `GET /api/rooms/`

Get all rooms with optional filtering.

**Query Parameters:**

- `room_type` (string, optional) - Filter by room type: `classroom`, `lab`, or `lecture_hall`
- `is_available` (boolean, optional) - Filter by availability
- `min_capacity` (integer, optional) - Minimum capacity filter
- `max_capacity` (integer, optional) - Maximum capacity filter

**Examples:**

- `GET /api/rooms/`
- `GET /api/rooms/?room_type=classroom`
- `GET /api/rooms/?is_available=true&min_capacity=30`
- `GET /api/rooms/?room_type=lab&min_capacity=20&max_capacity=50`

**Authentication:** Required

#### `POST /api/rooms/`

Create a new room.

**Request Body:**

```json
{
  "name": "string (required, unique)",
  "room_type": "string (required: 'classroom', 'lab', or 'lecture_hall')",
  "capacity": "integer (required, positive)",
  "is_available": "boolean (optional, default: true)"
}
```

**Authentication:** Required

#### `GET /api/rooms/<id>`

Get specific room.

**Query Parameters:** None

**Example:** `GET /api/rooms/1`

**Authentication:** Required

#### `PUT /api/rooms/<id>`

Update room.

**Request Body:**

```json
{
  "name": "string (optional)",
  "room_type": "string (optional)",
  "capacity": "integer (optional)",
  "is_available": "boolean (optional)"
}
```

**Authentication:** Required

#### `DELETE /api/rooms/<id>`

Delete room.

**Query Parameters:** None

**Authentication:** Required

#### `GET /api/rooms/<id>/schedule`

Get room's schedule.

**Query Parameters:**

- `timetable_id` (integer, optional) - Filter schedule by timetable ID

**Examples:**

- `GET /api/rooms/1/schedule`
- `GET /api/rooms/1/schedule?timetable_id=5`

**Authentication:** Required

#### `POST /api/rooms/availability`

Check room availability for a specific time slot.

**Request Body:**

```json
{
  "day_of_week": "integer (required, 0-6)",
  "start_time": "string (required, HH:MM format)",
  "end_time": "string (required, HH:MM format)",
  "room_type": "string (optional)",
  "min_capacity": "integer (optional)"
}
```

**Authentication:** Required

---

### 5. Course Routes (`/api/courses`)

#### `GET /api/courses/`

Get all courses with optional filtering.

**Query Parameters:**

- `department_id` (integer, optional) - Filter by department ID
- `teacher_id` (integer, optional) - Filter by teacher ID
- `level_id` (integer, optional) - Filter by student level ID
- `semester` (string, optional) - Filter by semester (e.g., "Fall", "Spring")
- `year` (integer, optional) - Filter by academic year
- `is_active` (boolean, optional) - Filter by active status

**Examples:**

- `GET /api/courses/`
- `GET /api/courses/?department_id=1`
- `GET /api/courses/?teacher_id=5&is_active=true`
- `GET /api/courses/?level_id=2&semester=Fall&year=2024`

**Authentication:** Required

#### `POST /api/courses/`

Create a new course.

**Request Body:**

```json
{
  "name": "string (required)",
  "code": "string (required, unique)",
  "department_id": "integer (required)",
  "teacher_id": "integer (optional)",
  "level_id": "integer (optional)",
  "weekly_sessions": "integer (optional, default: 1)",
  "semester": "string (optional)",
  "year": "integer (optional)",
  "is_active": "boolean (optional, default: true)"
}
```

**Authentication:** Required

#### `GET /api/courses/<id>`

Get specific course.

**Query Parameters:** None

**Example:** `GET /api/courses/1`

**Authentication:** Required

#### `PUT /api/courses/<id>`

Update course.

**Request Body:**

```json
{
  "name": "string (optional)",
  "code": "string (optional)",
  "department_id": "integer (optional)",
  "teacher_id": "integer (optional)",
  "level_id": "integer (optional)",
  "weekly_sessions": "integer (optional)",
  "semester": "string (optional)",
  "year": "integer (optional)",
  "is_active": "boolean (optional)"
}
```

**Authentication:** Required

#### `DELETE /api/courses/<id>`

Delete course.

**Query Parameters:** None

**Authentication:** Required

#### `PUT /api/courses/<id>/assign-teacher`

Assign teacher to course.

**Request Body:**

```json
{
  "teacher_id": "integer (required)"
}
```

**Authentication:** Required

#### `PUT /api/courses/<id>/unassign-teacher`

Unassign teacher from course.

**Request Body:** None

**Authentication:** Required

---

### 6. Level Routes (`/api/levels`)

#### `GET /api/levels/`

Get all levels with optional filtering.

**Query Parameters:**

- `active_only` (boolean, optional) - Filter by active status (pass `true` or `false` as string)

**Examples:**

- `GET /api/levels/`
- `GET /api/levels/?active_only=true`

**Authentication:** Required

#### `POST /api/levels/`

Create a new level.

**Request Body:**

```json
{
  "name": "string (required, unique)",
  "code": "string (required, unique)",
  "description": "string (optional)",
  "order": "integer (optional, auto-assigned if not provided)",
  "is_active": "boolean (optional, default: true)"
}
```

**Authentication:** Required

#### `GET /api/levels/<id>`

Get specific level.

**Query Parameters:** None

**Example:** `GET /api/levels/1`

**Authentication:** Required

#### `PUT /api/levels/<id>`

Update level.

**Request Body:**

```json
{
  "name": "string (optional)",
  "code": "string (optional)",
  "description": "string (optional)",
  "order": "integer (optional)",
  "is_active": "boolean (optional)"
}
```

**Authentication:** Required

#### `DELETE /api/levels/<id>`

Delete level.

**Query Parameters:** None

**Authentication:** Required

#### `GET /api/levels/by-code/<code>`

Get level by code.

**Query Parameters:** None

**Example:** `GET /api/levels/by-code/L1`

**Authentication:** Required

#### `POST /api/levels/initialize`

Initialize default levels (Level 1, 2, 3, Master 1, Master 2).

**Request Body:** None

**Authentication:** Required

#### `GET /api/levels/<id>/courses`

Get all courses for a specific level.

**Query Parameters:** None

**Example:** `GET /api/levels/1/courses`

**Authentication:** Required

---

### 7. Timetable Routes (`/api/timetables`)

#### `GET /api/timetables/`

Get all timetables with optional filtering.

**Query Parameters:**

- `department_id` (integer, optional) - Filter by department ID
- `status` (string, optional) - Filter by status: `draft`, `published`, or `archived`
- `academic_year` (string, optional) - Filter by academic year (e.g., "2024-2025")
- `semester` (string, optional) - Filter by semester (e.g., "Fall", "Spring")
- `include_slots` (boolean, optional) - Include slots in response (default: `true`)

**Examples:**

- `GET /api/timetables/`
- `GET /api/timetables/?department_id=1`
- `GET /api/timetables/?status=published&semester=Fall`
- `GET /api/timetables/?include_slots=false`

#### `POST /api/timetables/`

Create a new timetable.

**Request Body:**

```json
{
  "name": "string (required)",
  "department_id": "integer (required)",
  "week_start": "string (required, YYYY-MM-DD format)",
  "week_end": "string (optional, YYYY-MM-DD format)",
  "academic_year": "string (optional)",
  "semester": "string (optional)",
  "status": "string (optional, default: 'draft')"
}
```

**Authentication:** Required

#### `GET /api/timetables/<id>`

Get specific timetable with all slots.

**Query Parameters:**

- `include_slots` (boolean, optional) - Include slots in response (default: `true`)

**Examples:**

- `GET /api/timetables/1`
- `GET /api/timetables/1?include_slots=false`

#### `PUT /api/timetables/<id>`

Update timetable.

**Request Body:**

```json
{
  "name": "string (optional)",
  "department_id": "integer (optional)",
  "week_start": "string (optional, YYYY-MM-DD format)",
  "week_end": "string (optional, YYYY-MM-DD format)",
  "academic_year": "string (optional)",
  "semester": "string (optional)",
  "status": "string (optional)"
}
```

**Query Parameters:**

- `include_slots` (boolean, optional) - Include slots in response (default: `true`)

**Authentication:** Required

#### `DELETE /api/timetables/<id>`

Delete timetable.

**Query Parameters:** None

**Authentication:** Required

#### `PUT /api/timetables/<id>/publish`

Publish timetable (change status to published).

**Request Body:** None

**Query Parameters:** None

**Authentication:** Required

#### `PUT /api/timetables/<id>/archive`

Archive timetable (change status to archived).

**Request Body:** None

**Query Parameters:** None

**Authentication:** Required

#### `POST /api/timetables/<id>/clone`

Clone timetable.

**Request Body:**

```json
{
  "name": "string (required)",
  "week_start": "string (optional, YYYY-MM-DD format)",
  "week_end": "string (optional, YYYY-MM-DD format)",
  "department_id": "integer (optional)",
  "academic_year": "string (optional)",
  "semester": "string (optional)"
}
```

**Authentication:** Required

#### `GET /api/timetables/<id>/stats`

Get timetable statistics.

**Query Parameters:** None

**Example:** `GET /api/timetables/1/stats`

---

### 8. Slot Routes (`/api/timetables/<timetable_id>/slots`)

#### `GET /api/timetables/<timetable_id>/slots/`

Get all timetable slots with optional filtering.

**Query Parameters:**

- `course_id` (integer, optional) - Filter by course ID
- `room_id` (integer, optional) - Filter by room ID
- `day_of_week` (integer, optional) - Filter by day of week (0=Monday, 6=Sunday)

**Examples:**

- `GET /api/timetables/1/slots/`
- `GET /api/timetables/1/slots/?course_id=5`
- `GET /api/timetables/1/slots/?room_id=3&day_of_week=1`
- `GET /api/timetables/1/slots/?course_id=5&day_of_week=2`

#### `POST /api/timetables/<timetable_id>/slots/`

Create a new timetable slot.

**Request Body:**

```json
{
  "course_id": "integer (required)",
  "room_id": "integer (required)",
  "day_of_week": "integer (required, 0-6)",
  "start_time": "string (required, HH:MM format)",
  "end_time": "string (required, HH:MM format)",
  "notes": "string (optional)"
}
```

**Authentication:** Required

#### `GET /api/timetables/<timetable_id>/slots/<id>`

Get specific slot.

**Query Parameters:** None

**Example:** `GET /api/timetables/1/slots/10`

#### `PUT /api/timetables/<timetable_id>/slots/<id>`

Update slot.

**Request Body:**

```json
{
  "course_id": "integer (optional)",
  "room_id": "integer (optional)",
  "day_of_week": "integer (optional, 0-6)",
  "start_time": "string (optional, HH:MM format)",
  "end_time": "string (optional, HH:MM format)",
  "notes": "string (optional)"
}
```

**Authentication:** Required

#### `DELETE /api/timetables/<timetable_id>/slots/<id>`

Delete slot.

**Query Parameters:** None

**Authentication:** Required

#### `POST /api/timetables/<timetable_id>/slots/conflicts`

Check for scheduling conflicts for a proposed time slot.

**Request Body:**

```json
{
  "course_id": "integer (required)",
  "room_id": "integer (required)",
  "day_of_week": "integer (required, 0-6)",
  "start_time": "string (required, HH:MM format)",
  "end_time": "string (required, HH:MM format)"
}
```

**Authentication:** Required

#### `POST /api/timetables/<timetable_id>/slots/bulk-create`

Create multiple slots at once.

**Request Body:**

```json
{
  "slots": [
    {
      "course_id": "integer (required)",
      "room_id": "integer (required)",
      "day_of_week": "integer (required, 0-6)",
      "start_time": "string (required, HH:MM format)",
      "end_time": "string (required, HH:MM format)",
      "notes": "string (optional)"
    }
  ]
}
```

**Authentication:** Required

## Response Format

All responses follow this general format:

### Success Response

```json
{
  "message": "Operation successful",
  "data": {...}
}
```

### Error Response

```json
{
  "error": "Error description"
}
```

## Data Models

### Day of Week

- 0 = Monday
- 1 = Tuesday
- 2 = Wednesday
- 3 = Thursday
- 4 = Friday
- 5 = Saturday
- 6 = Sunday

### Room Types

- `classroom` - Standard classroom
- `lab` - Laboratory
- `lecture_hall` - Large lecture hall

### Timetable Status

- `draft` - Work in progress
- `published` - Active timetable
- `archived` - No longer active

### Student Levels

- `Level 1` (L1) - First year undergraduate level
- `Level 2` (L2) - Second year undergraduate level
- `Level 3` (L3) - Third year undergraduate level
- `Master 1` (M1) - First year master level
- `Master 2` (M2) - Second year master level

### Time Format

All times should be in HH:MM format (24-hour)
Example: "09:00", "13:30", "16:45"

### Date Format

All dates should be in YYYY-MM-DD format
Example: "2025-11-12"

## Error Codes

- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid/missing token)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error
