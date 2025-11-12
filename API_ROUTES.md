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

- `POST /api/auth/register` - Register a new admin user
- `POST /api/auth/login` - Login admin user
- `GET /api/auth/me` - Get current admin information
- `PUT /api/auth/change-password` - Change admin password
- `PUT /api/auth/update-profile` - Update admin profile

### 2. Department Routes (`/api/departments`)

- `GET /api/departments/` - Get all departments (with optional filtering)
- `POST /api/departments/` - Create a new department
- `GET /api/departments/<id>` - Get specific department
- `PUT /api/departments/<id>` - Update department
- `DELETE /api/departments/<id>` - Delete department
- `GET /api/departments/<id>/teachers` - Get department teachers
- `GET /api/departments/<id>/courses` - Get department courses

### 3. Teacher Routes (`/api/teachers`)

- `GET /api/teachers/` - Get all teachers (with optional filtering)
- `POST /api/teachers/` - Create a new teacher
- `GET /api/teachers/<id>` - Get specific teacher
- `PUT /api/teachers/<id>` - Update teacher
- `DELETE /api/teachers/<id>` - Delete teacher
- `GET /api/teachers/<id>/courses` - Get teacher's courses
- `GET /api/teachers/<id>/schedule` - Get teacher's schedule

### 4. Room Routes (`/api/rooms`)

- `GET /api/rooms/` - Get all rooms (with optional filtering)
- `POST /api/rooms/` - Create a new room
- `GET /api/rooms/<id>` - Get specific room
- `PUT /api/rooms/<id>` - Update room
- `DELETE /api/rooms/<id>` - Delete room
- `GET /api/rooms/<id>/schedule` - Get room's schedule
- `POST /api/rooms/availability` - Check room availability

### 5. Course Routes (`/api/courses`)

- `GET /api/courses/` - Get all courses (with optional filtering)
- `POST /api/courses/` - Create a new course
- `GET /api/courses/<id>` - Get specific course
- `PUT /api/courses/<id>` - Update course
- `DELETE /api/courses/<id>` - Delete course
- `PUT /api/courses/<id>/assign-teacher` - Assign teacher to course
- `PUT /api/courses/<id>/unassign-teacher` - Unassign teacher from course

### 6. Timetable Routes (`/api/timetables`)

- `GET /api/timetables/` - Get all timetables (with optional filtering)
- `POST /api/timetables/` - Create a new timetable
- `GET /api/timetables/<id>` - Get specific timetable with all slots
- `PUT /api/timetables/<id>` - Update timetable
- `DELETE /api/timetables/<id>` - Delete timetable
- `PUT /api/timetables/<id>/publish` - Publish timetable
- `PUT /api/timetables/<id>/archive` - Archive timetable
- `POST /api/timetables/<id>/clone` - Clone timetable

### 7. Slot Routes (`/api/slots`)

- `GET /api/slots/` - Get all timetable slots (with optional filtering)
- `POST /api/slots/` - Create a new timetable slot
- `GET /api/slots/<id>` - Get specific slot
- `PUT /api/slots/<id>` - Update slot
- `DELETE /api/slots/<id>` - Delete slot
- `POST /api/slots/conflicts` - Check for scheduling conflicts
- `POST /api/slots/bulk-create` - Create multiple slots at once

## Common Query Parameters

### Departments

- `None` (no specific filters)

### Teachers

- `department_id` - Filter by department
- `is_active` - Filter by active status

### Rooms

- `room_type` - Filter by room type (classroom, lab, lecture_hall)
- `is_available` - Filter by availability
- `min_capacity` - Minimum capacity filter
- `max_capacity` - Maximum capacity filter

### Courses

- `department_id` - Filter by department
- `teacher_id` - Filter by teacher
- `semester` - Filter by semester
- `year` - Filter by year
- `is_active` - Filter by active status

### Timetables

- `department_id` - Filter by department
- `status` - Filter by status (draft, published, archived)
- `academic_year` - Filter by academic year
- `semester` - Filter by semester

### Slots

- `timetable_id` - Filter by timetable
- `course_id` - Filter by course
- `room_id` - Filter by room
- `day_of_week` - Filter by day (0=Monday, 6=Sunday)

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
