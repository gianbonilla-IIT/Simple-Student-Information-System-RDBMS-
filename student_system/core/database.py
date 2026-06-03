import sqlite3
import threading
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "student_system.db"

# Thread-local storage so each thread gets its own connection
_local = threading.local()


def get_connection() -> sqlite3.Connection:
    """Return a thread-local SQLite connection with foreign keys enabled."""
    if not hasattr(_local, "conn") or _local.conn is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        conn.row_factory = sqlite3.Row          # rows behave like dicts
        conn.execute("PRAGMA foreign_keys = ON")  # enforce FK constraints
        conn.execute("PRAGMA journal_mode = WAL")  # better concurrency
        _local.conn = conn
    return _local.conn


def initialize_schema() -> None:
    """Create tables if they don't already exist."""
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS college (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS program (
            code    TEXT PRIMARY KEY,
            name    TEXT NOT NULL,
            college TEXT NOT NULL,
            FOREIGN KEY (college) REFERENCES college(code)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
        );

        CREATE TABLE IF NOT EXISTS student (
            id        TEXT PRIMARY KEY CHECK(id GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'),
            firstname TEXT NOT NULL,
            lastname  TEXT NOT NULL,
            course    TEXT NOT NULL,
            year      INTEGER NOT NULL CHECK(year >= 1),
            gender    TEXT NOT NULL CHECK(gender IN ('Male','Female','Other')),
            FOREIGN KEY (course) REFERENCES program(code)
                ON UPDATE CASCADE
                ON DELETE RESTRICT
        );

        CREATE INDEX IF NOT EXISTS idx_student_course    ON student(course);
        CREATE INDEX IF NOT EXISTS idx_student_lastname  ON student(lastname);
        CREATE INDEX IF NOT EXISTS idx_program_college   ON program(college);
    """)
    conn.commit()
