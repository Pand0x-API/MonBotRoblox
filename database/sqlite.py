import sqlite3
from pathlib import Path

DATABASE = Path("database/monbotroblox.db")


def get_connection():
    DATABASE.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DATABASE)


def init_database():
    with get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = ON")
