import os
import sys
from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade, downgrade, current, history
from config.db import db
from config.flask import create_app

# Import all models to ensure they're registered with SQLAlchemy
import models

class MigrationManager:
    def __init__(self):
        self.app = create_app()
        self.migrate = Migrate(self.app, db)

    def init_migrations(self):
        """Initialize migration repository"""
        with self.app.app_context():
            try:
                init()
                print("✅ Migration repository initialized successfully!")
                return True
            except Exception as e:
                print(f"❌ Error initializing migrations: {e}")
                return False

    def create_migration(self, message="Auto migration"):
        """Create a new migration"""
        with self.app.app_context():
            try:
                migrate(message=message)
                print(f"✅ Migration created: {message}")
                return True
            except Exception as e:
                print(f"❌ Error creating migration: {e}")
                return False

    def apply_migrations(self):
        """Apply all pending migrations"""
        with self.app.app_context():
            try:
                upgrade()
                print("✅ All migrations applied successfully!")
                return True
            except Exception as e:
                print(f"❌ Error applying migrations: {e}")
                return False

    def rollback_migration(self):
        """Rollback one migration"""
        with self.app.app_context():
            try:
                downgrade()
                print("✅ Migration rolled back successfully!")
                return True
            except Exception as e:
                print(f"❌ Error rolling back migration: {e}")
                return False

    def get_current_revision(self):
        """Get current migration revision"""
        with self.app.app_context():
            try:
                revision = current()
                print(f"📍 Current revision: {revision}")
                return revision
            except Exception as e:
                print(f"❌ Error getting current revision: {e}")
                return None

    def get_migration_history(self):
        """Get migration history"""
        with self.app.app_context():
            try:
                hist = history()
                print("📜 Migration History:")
                for rev in hist:
                    print(f"  - {rev}")
                return hist
            except Exception as e:
                print(f"❌ Error getting migration history: {e}")
                return None

    def create_all_tables(self):
        """Create all tables without migrations (for development)"""
        with self.app.app_context():
            try:
                db.create_all()
                print("✅ All tables created successfully!")
                return True
            except Exception as e:
                print(f"❌ Error creating tables: {e}")
                return False

    def drop_all_tables(self):
        """Drop all tables"""
        with self.app.app_context():
            try:
                db.drop_all()
                print("✅ All tables dropped successfully!")
                return True
            except Exception as e:
                print(f"❌ Error dropping tables: {e}")
                return False

    def reset_database(self):
        """Complete database reset"""
        print("🔄 Resetting database...")
        success = True

        # Drop all tables
        if not self.drop_all_tables():
            success = False

        # Remove migrations folder if it exists
        migrations_path = os.path.join(os.path.dirname(__file__), 'migrations')
        if os.path.exists(migrations_path):
            import shutil
            shutil.rmtree(migrations_path)
            print("✅ Migrations folder removed!")

        return success

    def setup_fresh_database(self):
        """Set up a fresh database with migrations"""
        print("🚀 Setting up fresh database with migrations...")

        # Reset everything
        self.reset_database()

        # Initialize migrations
        if not self.init_migrations():
            return False

        # Create initial migration
        if not self.create_migration("Initial migration - create all tables"):
            return False

        # Apply migrations
        if not self.apply_migrations():
            return False

        print("🎉 Fresh database setup complete!")
        return True

def main():
    manager = MigrationManager()

    if len(sys.argv) < 2:
        print("""
Usage: python migrate_db.py <command>

Commands:
  init              - Initialize migration repository
  create <message>  - Create new migration
  upgrade          - Apply all pending migrations
  downgrade        - Rollback one migration
  current          - Show current revision
  history          - Show migration history
  create-tables    - Create tables without migrations
  drop-tables      - Drop all tables
  reset            - Complete database reset
  setup-fresh      - Setup fresh database with migrations
        """)
        return

    command = sys.argv[1].lower()

    if command == 'init':
        manager.init_migrations()

    elif command == 'create':
        message = sys.argv[2] if len(sys.argv) > 2 else "Auto migration"
        manager.create_migration(message)

    elif command == 'upgrade':
        manager.apply_migrations()

    elif command == 'downgrade':
        manager.rollback_migration()

    elif command == 'current':
        manager.get_current_revision()

    elif command == 'history':
        manager.get_migration_history()

    elif command == 'create-tables':
        manager.create_all_tables()

    elif command == 'drop-tables':
        manager.drop_all_tables()

    elif command == 'reset':
        manager.reset_database()

    elif command == 'setup-fresh':
        manager.setup_fresh_database()

    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()