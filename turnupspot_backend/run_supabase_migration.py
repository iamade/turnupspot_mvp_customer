#!/usr/bin/env python3Script to run Alembic migrations on Supabase database""
import os
import subprocess
import sys
from pathlib import Path

def run_migration_on_supabase():
 Alembic migration on Supabase database"""
    # Get the database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set)     print("Please set your Supabase database URL in DATABASE_URL")
        sys.exit(1)
    
    print(f🔗 Using database: {database_url.split('@')[1] if '@' in database_url else Unknown'}")
    
    # Set environment variable for Alembic
    env = os.environ.copy()
    env['DATABASE_URL'] = database_url
    
    try:
        # Run the migration
        print("🚀 Running migration on Supabase...")
        result = subprocess.run(
            ['alembic', 'upgrade', 'head'],
            env=env,
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Migration completed successfully!")
            if result.stdout:
                print("Output:, result.stdout)
        else:
            print("❌ Migration failed!")
            if result.stderr:
                print("Error:, result.stderr)
            if result.stdout:
                print("Output:, result.stdout)
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error running migration: {e}")
        sys.exit(1if __name__ == "__main__":
    run_migration_on_supabase() 