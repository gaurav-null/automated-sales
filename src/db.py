"""
src/db.py
Description: Database connection utility.
Uses psycopg2 to connect to PostgreSQL.
Environment Variable: DATABASE_URL
"""

import os
from sqlalchemy import create_engine

def get_engine():
    """
    Returns a SQLAlchemy engine configured to connect to the database.
    The connection URL is taken from the DATABASE_URL environment variable.
    """
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    engine = create_engine(db_url)
    return engine