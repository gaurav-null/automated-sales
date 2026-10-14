"""
src/init_db.py
Description: Initializes the database schema, seeds dimension tables,
and creates the calculation views.
Run with: python src/init_db.py
"""

import os
import sys
from sqlalchemy import text
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.db import get_engine

load_dotenv()

SQL_FILES = [
    'sql/01_schema.sql',
    'sql/02_seed.sql',
    'sql/03_calculations.sql',
]

def init_database():
    print("[INIT] Connecting to PostgreSQL database...")
    engine = get_engine()

    for rel_path in SQL_FILES:
        full_path = os.path.join(os.path.dirname(__file__), '..', rel_path)
        print(f"  → Executing {rel_path}...")
        with open(full_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        with engine.connect() as conn:
            # PostgreSQL can execute multi-statement SQL script
            conn.execute(text(sql_script))
            conn.commit()
        print(f"    ✓ Applied {rel_path}")

    print("\n[SUCCESS] Database initialization completed! All tables and views created.")

if __name__ == "__main__":
    init_database()
