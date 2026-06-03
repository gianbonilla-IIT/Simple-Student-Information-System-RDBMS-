import re
from core.database import get_connection

ID_PATTERN   = re.compile(r"^\d{4}-\d{4}$")
# Allows letters (including accented/Filipino), spaces, hyphens, apostrophes, periods
NAME_PATTERN = re.compile(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s\-'\.]+$")
VALID_GENDERS = {"Male", "Female", "Other"}


def _row_to_dict(row) -> dict:
    return {
        "id": row["id"],
        "firstname": row["firstname"],
        "lastname": row["lastname"],
        "course": row["course"],
        "year": str(row["year"]),
        "gender": row["gender"],
    }


def _validate(student_id: str, firstname: str, lastname: str,
              course: str, year: str, gender: str) -> None:
    # ID
    if not student_id:
        raise ValueError("Student ID cannot be empty.")
    if not ID_PATTERN.match(student_id):
        raise ValueError("Student ID must follow YYYY-NNNN format (e.g. 2024-0001).")
    year_part = int(student_id[:4])
    if year_part < 1900 or year_part > 2100:
        raise ValueError("Student ID year must be between 1900 and 2100.")

    # Names
    if not firstname:
        raise ValueError("First name cannot be empty.")
    if len(firstname) > 50:
        raise ValueError("First name must be 50 characters or fewer.")
    if not NAME_PATTERN.match(firstname):
        raise ValueError("First name must contain letters only (hyphens and apostrophes allowed).")

    if not lastname:
        raise ValueError("Last name cannot be empty.")
    if len(lastname) > 50:
        raise ValueError("Last name must be 50 characters or fewer.")
    if not NAME_PATTERN.match(lastname):
        raise ValueError("Last name must contain letters only (hyphens and apostrophes allowed).")

    # Course
    # Course is now optional (can be NULL after program deletion)
    if course and len(course) > 20:
        raise ValueError("Course code is too long.")

    # Year level
    if not year:
        raise ValueError("Year level cannot be empty.")
    if not year.isdigit():
        raise ValueError("Year level must be a number.")
    if int(year) < 1 or int(year) > 10:
        raise ValueError("Year level must be between 1 and 10.")

    # Gender
    if not gender:
        raise ValueError("Gender cannot be empty.")
    if gender not in VALID_GENDERS:
        raise ValueError(f"Gender must be one of: {', '.join(sorted(VALID_GENDERS))}.")


def create(student_id: str, firstname: str, lastname: str,
           course: str | None = None, year: str = "", gender: str = "") -> dict:
    student_id = student_id.strip()
    firstname, lastname = firstname.strip(), lastname.strip()
    course = course.strip().upper() if course else None
    year, gender = year.strip(), gender.strip()

    _validate(student_id, firstname, lastname, course, year, gender)
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO student (id, firstname, lastname, course, year, gender) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (student_id, firstname, lastname, course, int(year), gender)
        )
        conn.commit()
        return _row_to_dict(conn.execute(
            "SELECT * FROM student WHERE id = ?", (student_id,)
        ).fetchone())
    except Exception as e:
        conn.rollback()
        if "UNIQUE" in str(e):
            raise ValueError(f"Student ID '{student_id}' already exists.")
        if "FOREIGN KEY" in str(e):
            raise ValueError(f"Program '{course}' does not exist.")
        if "CHECK" in str(e):
            raise ValueError("Invalid data: check ID format, year, or gender.")
        raise ValueError(str(e))


def read(student_id: str) -> dict | None:
    student_id = student_id.strip()
    conn = get_connection()
    row = conn.execute("SELECT * FROM student WHERE id = ?", (student_id,)).fetchone()
    return _row_to_dict(row) if row else None


def update(student_id: str, firstname: str, lastname: str,
           course: str | None = None, year: str = "", gender: str = "") -> dict:
    student_id = student_id.strip()
    firstname, lastname = firstname.strip(), lastname.strip()
    course = course.strip().upper() if course else None
    year, gender = year.strip(), gender.strip()

    _validate(student_id, firstname, lastname, course, year, gender)
    conn = get_connection()
    try:
        cur = conn.execute(
            "UPDATE student SET firstname=?, lastname=?, course=?, year=?, gender=? "
            "WHERE id=?",
            (firstname, lastname, course, int(year), gender, student_id)
        )
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"Student '{student_id}' not found.")
        return read(student_id)
    except ValueError:
        raise
    except Exception as e:
        conn.rollback()
        if "FOREIGN KEY" in str(e):
            raise ValueError(f"Program '{course}' does not exist.")
        raise ValueError(str(e))


def delete(student_id: str) -> None:
    student_id = student_id.strip()
    conn = get_connection()
    try:
        cur = conn.execute("DELETE FROM student WHERE id = ?", (student_id,))
        conn.commit()
        if cur.rowcount == 0:
            raise ValueError(f"Student '{student_id}' not found.")
    except ValueError:
        raise
    except Exception as e:
        conn.rollback()
        raise ValueError(str(e))


VALID_SORT = {"id", "firstname", "lastname", "course", "year", "gender"}


def list_all(sort_by: str = "id", reverse: bool = False,
             search: str = "", page: int = 1, page_size: int = 50
             ) -> tuple[list[dict], int]:
    if sort_by not in VALID_SORT:
        sort_by = "id"
    direction = "DESC" if reverse else "ASC"

    conn = get_connection()
    if search:
        like = f"%{search}%"
        where = (
            "WHERE id LIKE ? OR firstname LIKE ? OR lastname LIKE ? "
            "OR course LIKE ? OR CAST(year AS TEXT) LIKE ? OR gender LIKE ?"
        )
        params = (like,) * 6
        total = conn.execute(f"SELECT COUNT(*) FROM student {where}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM student {where} "
            f"ORDER BY {sort_by} {direction} LIMIT ? OFFSET ?",
            params + (page_size, (page - 1) * page_size)
        ).fetchall()
    else:
        total = conn.execute("SELECT COUNT(*) FROM student").fetchone()[0]
        rows = conn.execute(
            f"SELECT * FROM student ORDER BY {sort_by} {direction} LIMIT ? OFFSET ?",
            (page_size, (page - 1) * page_size)
        ).fetchall()

    return [_row_to_dict(r) for r in rows], total
