#!/usr/bin/env python3
"""Check what's in the database."""

import os
import psycopg2
from urllib.parse import urlparse

def check_database():
    """Check database contents."""
    db_url = "postgresql://smart_bookmark_db_user:ZKhFRlrOd3vA5yDVsUdupKPQ9iRHlRUn@dpg-d4m420ogjchc73b1hlg0-a.oregon-postgres.render.com/smart_bookmark_db"
    
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
        
        cursor = conn.cursor()
        
        print("✅ Connected to database successfully!")
        
        # Check tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        print(f"\n📋 Tables found: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Check data in each main table
        main_tables = ['users', 'tags', 'collections', 'bookmarks']
        
        for table in main_tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"\n📊 {table}: {count} records")
                
                if count > 0:
                    # Show first few records
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                    records = cursor.fetchall()
                    
                    # Get column names
                    cursor.execute(f"""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = '{table}'
                        ORDER BY ordinal_position
                    """)
                    columns = [col[0] for col in cursor.fetchall()]
                    
                    print(f"  Columns: {', '.join(columns)}")
                    for i, record in enumerate(records, 1):
                        print(f"  Record {i}: {record}")
                        
            except Exception as e:
                print(f"❌ Error checking {table}: {e}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

if __name__ == "__main__":
    check_database()