"""
program.py
CRUDL operations for the program table.
"""

import re
from core.database import get_connection

CODE_PATTERN = re.compile(r"^[A-Za-z0-9\-]+$")
NAME_PATTERN = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ0-9\s\-',\.&]+$")


def _row_to_dict(row) -> dict:
    return {"code": row["code"], "name": row["name"], "college": row["college"]}


def _validate(code: str, name: str, college_code: str) -> None:
    if not code:
        raise ValueError("Program code cannot be empty.")
    if len(code) > 20:
        raise ValueError("Program code must be 20 characters or fewer.")
    if not CODE_PATTERN.match(code):
        raise ValueError("Program code must contain only letters, numbers, or hyphens.")
    if not name:
        raise ValueError("Program name cannot be empty.")
    if len(name) > 150:
        raise ValueError("Program name must be 150 characters or fewer.")
    if not NAME_PATTERN.match(name):
        raise ValueError("Program name contains invalid characters.")
    if not college_code:
        raise ValueError("College code cannot be empty.")
    if len(college_code) > 20:
        raise ValueError("College code must be 20 characters or fewer.")


def create(code: str, name: str, college_code: str) -> dict:
    code, name = code.strip().upper(), name.strip()
    college_code = college_code.strip().upper()
    _validate(code, name, college_code)
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO program (code, name, college) VALUES (?, ?, ?)",
            (code, name, college_code)
        )
        conn.commit()
        return {"code": code, "name": name, "college": college_code}
    except Exception as e:
        conn.rollback()
        if "UNIQUE" in str(e):
            raise ValueError(f"Program code '{code}' already exists.")
        if "FOREIGN KEY" in str(e):
            raise ValueError(f"College '{college_code}' does not exist.")
        raise ValueError(str(e))


def read(code: str) -> dict | None:
    code = code.strip().upper()
    conn = get_connection()
    row = conn.execute("SELECT * FROM program WHERE code = ?", (code,)).fetchone()
    return _row_to_dict(row) if row else None


def update(code: str, name: str, college_code: str) -> dict:
    code, name = code.strip().upper(), name.strip()
    college_code = college_code.strip().upper()
    _validate(code, name, college_code)
    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE program SET name = ?, college = ? WHERE code = ?",
            (name, college_code, code)
        )
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"Program '{code}' not found.")
        return {"code": code, "name": name, "college": college_code}
    except ValueError:
        raise
    except Exception as e:
        conn.rollback()
        if "FOREIGN KEY" in str(e):
            raise ValueError(f"College '{college_code}' does not exist.")
        raise ValueError(str(e))


def delete(code: str) -> None:
    code = code.strip().upper()
    if not code:
        raise ValueError("Program code cannot be empty.")
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM program WHERE code = ?", (code,))
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"Program '{code}' not found.")
    except Exception as e:
        conn.rollback()
        if "FOREIGN KEY" in str(e):
            raise ValueError(
                f"Cannot delete program '{code}': it is referenced by one or more students."
            )
        raise ValueError(str(e))


def list_all(sort_by: str = "code", reverse: bool = False,
             search: str = "", page: int = 1, page_size: int = 50
             ) -> tuple[list[dict], int]:
    valid_sort = {"code", "name", "college"}
    if sort_by not in valid_sort:
        sort_by = "code"
    direction = "DESC" if reverse else "ASC"

    conn = get_connection()
    if search:
        like = f"%{search}%"
        total = conn.execute(
            "SELECT COUNT(*) FROM program WHERE code LIKE ? OR name LIKE ? OR college LIKE ?",
            (like, like, like)
        ).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM program WHERE code LIKE ? OR name LIKE ? OR college LIKE ? "
            f"ORDER BY {sort_by} {direction} LIMIT ? OFFSET ?",
            (like, like, like, page_size, (page - 1) * page_size)
        ).fetchall()
    else:
        total = conn.execute("SELECT COUNT(*) FROM program").fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM program ORDER BY {sort_by} {direction} LIMIT ? OFFSET ?",
            (page_size, (page - 1) * page_size)
        ).fetchall()

    return [_row_to_dict(r) for r in rows], total


def get_all_codes() -> list[str]:
    """Return all program codes for dropdowns."""
    conn = get_connection()
    rows = conn.execute("SELECT code FROM program ORDER BY code").fetchall()
    return [r["code"] for r in rows]
