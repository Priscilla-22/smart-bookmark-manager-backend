#!/usr/bin/env python3
"""Test database connection."""

import os
import psycopg2
from urllib.parse import urlparse

def test_connection():
    """Test PostgreSQL connection."""
    db_url = "postgresql://smart_bookmark_db_user:ZKhFRlrOd3vA5yDVsUdupKPQ9iRHlRUn@dpg-d4m420ogjchc73b1hlg0-a/smart_bookmark_db"
    
    try:
        # Parse the DATABASE_URL
        parsed = urlparse(db_url)
        
        # Connect to database
        conn = psycopg2.connect(
            host=parsed.hostname,
            database=parsed.path[1:],  # Remove leading '/'
            user=parsed.username,
            password=parsed.password,
            port=parsed.port or 5432
        )
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print("✅ Database connection successful!")
        print(f"PostgreSQL version: {version[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    test_connection()