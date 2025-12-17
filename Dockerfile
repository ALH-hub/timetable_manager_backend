# Dockerfile for Timetable Manager Backend
# Builds a container that runs the Flask app exposed from root-level `app.py` (app:app)

FROM python:3.11-slim

# Prevents Python from writing .pyc files to disc and buffers stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies required for some Python packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev gcc git postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/requirements.txt

# Install Python dependencies and gunicorn
RUN pip3 install --no-cache-dir -r /app/requirements.txt \
    && pip install --no-cache-dir gunicorn

# Copy project files
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Default command: run migrations, optional seed (safe-guarded with || true) and start gunicorn
# NOTE: This runs migrations and seeding on container start (useful for development). Remove seed step for production.
CMD ["sh", "-c", "export FLASK_APP=app.py; flask db upgrade || true; flask db migrate && flask db upgrade || true; exec flask run --host=0.0.0.0 --port=5000"]
