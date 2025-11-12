#!/usr/bin/env python3
"""
Quick Seed Script - Wrapper
This script is a convenience wrapper that calls the main seeding script.

For the full-featured seeding script with conflict detection, use:
    python3 scripts/seed_database.py

This wrapper is kept in the root for backward compatibility.
"""

import sys
import os

# Add notice
print("=" * 70)
print("NOTICE: Using advanced seeding script from scripts/seed_database.py")
print("=" * 70)
print()

# Import and run the main seeding script
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))

try:
    from scripts.seed_database import main
    sys.exit(main())
except ImportError as e:
    print(f"Error importing seed_database: {e}")
    print("\nPlease run the script directly:")
    print("  python3 scripts/seed_database.py")
    sys.exit(1)
