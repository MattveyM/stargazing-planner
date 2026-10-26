"""Database connection helper.

Reads the database address from the DATABASE_URL setting in the .env file,
so passwords and settings never get hard-coded or uploaded to GitHub.
"""
import os

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row

load_dotenv()  # reads backend/.env

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/stargazing")


def get_connection():
    """Open a connection that returns each row as a dictionary (column name -> value)."""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)
