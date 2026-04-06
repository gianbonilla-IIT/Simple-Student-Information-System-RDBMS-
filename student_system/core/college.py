"""
college.py
CRUDL operations for the college table.
"""

import re
from core.database import get_connection

CODE_PATTERN = re.compile(r"^[A-Za-z0-9\-]+$")
NAME_PATTERN = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ0-9\s\-',\.&]+$")


def _row_to_dict(row) -> dict:
    return {"code": row["code"], "name": row["name"]}


def _validate(code: str, name: str) -> None:
    if not code:
        raise ValueError("College code cannot be empty.")
    if len(code) > 20:
        raise ValueError("College code must be 20 characters or fewer.")
    if not CODE_PATTERN.match(code):
        raise ValueError("College code must contain only letters, numbers, or hyphens.")
    if not name:
        raise ValueError("College name cannot be empty.")
    if len(name) > 100:
        raise ValueError("College name must be 100 characters or fewer.")
    if not NAME_PATTERN.match(name):
        raise ValueError("College name contains invalid characters.")


def create(code: str, name: str) -> dict:
    code, name = code.strip().upper(), name.strip()
    _validate(code, name)
    conn = get_connection()
    try:
        conn.execute("INSERT INTO college (code, name) VALUES (?, ?)", (code, name))
        conn.commit()
        return {"code": code, "name": name}
    except Exception as e:
        conn.rollback()
        if "UNIQUE" in str(e):
            raise ValueError(f"College code '{code}' already exists.")
        raise ValueError(str(e))


def read(code: str) -> dict | None:
    code = code.strip().upper()
    conn = get_connection()
    row = conn.execute("SELECT * FROM college WHERE code = ?", (code,)).fetchone()
    return _row_to_dict(row) if row else None


def update(code: str, name: str) -> dict:
    code, name = code.strip().upper(), name.strip()
    _validate(code, name)
    conn = get_connection()
    try:
        cur = conn.execute("UPDATE college SET name = ? WHERE code = ?", (name, code))
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"College '{code}' not found.")
        return {"code": code, "name": name}
    except ValueError:
        raise
    except Exception as e:
        conn.rollback()
        raise ValueError(str(e))


def delete(code: str) -> None:
    code = code.strip().upper()
    if not code:
        raise ValueError("College code cannot be empty.")
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM college WHERE code = ?", (code,))
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"College '{code}' not found.")
    except Exception as e:
        conn.rollback()
        if "FOREIGN KEY" in str(e):
            raise ValueError(
                f"Cannot delete college '{code}': it is referenced by one or more programs."
            )
        raise ValueError(str(e))


def list_all(sort_by: str = "code", reverse: bool = False,
             search: str = "", page: int = 1, page_size: int = 50
             ) -> tuple[list[dict], int]:
    valid_sort = {"code", "name"}
    if sort_by not in valid_sort:
        sort_by = "code"
    direction = "DESC" if reverse else "ASC"

    conn = get_connection()
    if search:
        like = f"%{search}%"
        total = conn.execute(
            "SELECT COUNT(*) FROM college WHERE code LIKE ? OR name LIKE ?",
            (like, like)
        ).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM college WHERE code LIKE ? OR name LIKE ? "
            f"ORDER BY {sort_by} {direction} LIMIT ? OFFSET ?",
            (like, like, page_size, (page - 1) * page_size)
        ).fetchall()
    else:
        total = conn.execute("SELECT COUNT(*) FROM college").fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM college ORDER BY {sort_by} {direction} LIMIT ? OFFSET ?",
            (page_size, (page - 1) * page_size)
        ).fetchall()

    return [_row_to_dict(r) for r in rows], total
