-- Quick SQL fix to add is_active column to admin table
-- Run this SQL command directly in your PostgreSQL database if migrations don't work

-- For PostgreSQL:
ALTER TABLE admin ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT true;

-- Update all existing admins to be active (if needed):
UPDATE admin SET is_active = true WHERE is_active IS NULL;

