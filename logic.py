import database
import sqlite3


def add_student(roll_no, name, class_id, contact_info):
    conn = database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
                       INSERT INTO students (roll_no, name, class_id, contact_info)
                       VALUES (?, ?, ?, ?)
                       ''', (roll_no, name, class_id, contact_info))
        conn.commit()
        return True, f"Student {name} added successfully."
    except sqlite3.IntegrityError:
        return False, f"Error: Roll Number '{roll_no}' already exists!"
    finally:
        conn.close()


def update_student(student_id, roll_no, name, class_id, contact_info):
    """Updates an existing student's information."""
    conn = database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
                       UPDATE students
                       SET roll_no      = ?,
                           name         = ?,
                           class_id     = ?,
                           contact_info = ?
                       WHERE student_id = ?
                       ''', (roll_no, name, class_id, contact_info, student_id))
        conn.commit()
        return True, f"Student {name} updated successfully."
    except sqlite3.IntegrityError:
        return False, f"Error: Roll Number '{roll_no}' is already used by another student!"
    finally:
        conn.close()


def get_all_classes():
    """Returns a list of all unique classes currently in the database."""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT class_id FROM students ORDER BY class_id")
    rows = cursor.fetchall()
    conn.close()
    return [row['class_id'] for row in rows]


def get_all_students():
    """Returns a list of all students for the management dashboard."""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students ORDER BY class_id, name")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_student_by_id(student_id):
    """Fetches a single student's details for editing."""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_students_by_class(class_id):
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, roll_no, name FROM students WHERE class_id = ?", (class_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def submit_attendance(attendance_list, date):
    conn = database.get_connection()
    cursor = conn.cursor()
    try:
        for record in attendance_list:
            # Check if record already exists for this date to prevent duplicates
            cursor.execute("SELECT record_id FROM attendance WHERE student_id = ? AND attendance_date = ?",
                           (record['student_id'], date))
            exists = cursor.fetchone()

            if exists:
                # Update existing record
                cursor.execute("UPDATE attendance SET status = ? WHERE record_id = ?",
                               (record['status'], exists['record_id']))
            else:
                # Insert new record
                cursor.execute("INSERT INTO attendance (student_id, attendance_date, status) VALUES (?, ?, ?)",
                               (record['student_id'], date, record['status']))
        conn.commit()
        return True, "Attendance saved successfully."
    except Exception as e:
        conn.rollback()
        return False, f"Failed to save attendance: {str(e)}"
    finally:
        conn.close()


def get_attendance_report(class_id, date):
    """Fetches past attendance records to view or export."""
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
                   SELECT s.roll_no, s.name, a.status
                   FROM attendance a
                            JOIN students s ON a.student_id = s.student_id
                   WHERE s.class_id = ?
                     AND a.attendance_date = ?
                   ORDER BY s.name
                   ''', (class_id, date))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]