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


def _migrate_schema() -> None:
    """Migrate schema from old constraints (RESTRICT) to new (SET NULL)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Try to add college column to program if needed (allows NULL)
        cursor.execute("PRAGMA table_info(program)")
        columns = cursor.fetchall()
        college_nullable = False
        
        for col in columns:
            if col[1] == "college":
                # col[3] is not_null flag
                college_nullable = col[3] == 0
                break
        
        # If college is NOT NULL, we need to migrate
        if not college_nullable:
            # Start transaction
            cursor.execute("BEGIN IMMEDIATE")
            
            try:
                # Create temporary tables with new schema
                cursor.executescript("""
                    CREATE TABLE program_new (
                        code    TEXT PRIMARY KEY,
                        name    TEXT NOT NULL,
                        college TEXT,
                        FOREIGN KEY (college) REFERENCES college(code)
                            ON UPDATE CASCADE
                            ON DELETE SET NULL
                    );

                    CREATE TABLE student_new (
                        id        TEXT PRIMARY KEY CHECK(id GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'),
                        firstname TEXT NOT NULL,
                        lastname  TEXT NOT NULL,
                        course    TEXT,
                        year      INTEGER NOT NULL CHECK(year >= 1),
                        gender    TEXT NOT NULL CHECK(gender IN ('Male','Female','Other')),
                        FOREIGN KEY (course) REFERENCES program(code)
                            ON UPDATE CASCADE
                            ON DELETE SET NULL
                    );
                """)
                
                # Copy data
                cursor.execute("INSERT INTO program_new SELECT * FROM program")
                cursor.execute("INSERT INTO student_new SELECT * FROM student")
                
                # Drop old tables
                cursor.execute("DROP TABLE student")
                cursor.execute("DROP TABLE program")
                
                # Rename new tables
                cursor.execute("ALTER TABLE program_new RENAME TO program")
                cursor.execute("ALTER TABLE student_new RENAME TO student")
                
                # Recreate indices
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_course ON student(course)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_lastname ON student(lastname)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_program_college ON program(college)")
                
                conn.commit()
            except Exception:
                conn.rollback()
                raise
    except Exception:
        # Silently fail - database might already be up to date
        pass


def initialize_schema() -> None:
    """Create tables if they don't already exist, or migrate if needed."""
    conn = get_connection()
    
    # First try to migrate if needed
    _migrate_schema()
    
    # Now create tables if they don't exist
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS college (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS program (
            code    TEXT PRIMARY KEY,
            name    TEXT NOT NULL,
            college TEXT,
            FOREIGN KEY (college) REFERENCES college(code)
                ON UPDATE CASCADE
                ON DELETE SET NULL
        );

        CREATE TABLE IF NOT EXISTS student (
            id        TEXT PRIMARY KEY CHECK(id GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]'),
            firstname TEXT NOT NULL,
            lastname  TEXT NOT NULL,
            course    TEXT,
            year      INTEGER NOT NULL CHECK(year >= 1),
            gender    TEXT NOT NULL CHECK(gender IN ('Male','Female','Other')),
            FOREIGN KEY (course) REFERENCES program(code)
                ON UPDATE CASCADE
                ON DELETE SET NULL
        );

        CREATE INDEX IF NOT EXISTS idx_student_course    ON student(course);
        CREATE INDEX IF NOT EXISTS idx_student_lastname  ON student(lastname);
        CREATE INDEX IF NOT EXISTS idx_program_college   ON program(college);
    """)
    conn.commit()
