#!/usr/bin/env python3
"""Run database migrations in production."""

import os
import sys
from alembic.config import Config
from alembic import command

def run_migrations():
    """Run Alembic migrations."""
    try:
        # Get the directory containing this script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        alembic_cfg_path = os.path.join(current_dir, 'alembic.ini')
        
        # Create Alembic configuration
        alembic_cfg = Config(alembic_cfg_path)
        
        # Run migrations
        command.upgrade(alembic_cfg, "head")
        print("✅ Database migrations completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migrations()