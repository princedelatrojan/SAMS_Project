import sqlite3
import hashlib
import os

# Define the database file name
DB_NAME = "sams_data.db"


def get_connection():
    """
    Creates and returns a connection to the SQLite database.
    """
    conn = sqlite3.connect(DB_NAME)
    # access columns by name
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    """
    Initializes the database
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Create USERS table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS users
                   (
                       user_id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       username
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       password_hash
                       TEXT
                       NOT
                       NULL,
                       role
                       TEXT
                       NOT
                       NULL
                       CHECK (
                       role
                       IN
                   (
                       'Admin',
                       'Teacher'
                   ))
                       )
                   """)

    # Create STUDENTS table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS students
                   (
                       student_id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       roll_no
                       TEXT
                       UNIQUE
                       NOT
                       NULL,
                       name
                       TEXT
                       NOT
                       NULL,
                       class_id
                       TEXT
                       NOT
                       NULL,
                       contact_info
                       TEXT
                   )
                   """)

    # Create ATTENDANCE table
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS attendance
                   (
                       record_id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       student_id
                       INTEGER
                       NOT
                       NULL,
                       attendance_date
                       DATE
                       NOT
                       NULL,
                       status
                       TEXT
                       NOT
                       NULL
                       CHECK (
                       status
                       IN
                   (
                       'Present',
                       'Absent',
                       'Excused'
                   )),
                       FOREIGN KEY
                   (
                       student_id
                   ) REFERENCES students
                   (
                       student_id
                   )
                       )
                   """)

    conn.commit()
    conn.close()
    print("Database tables verified/created successfully.")


def create_default_admin():
    """
    Creates a default administrator account
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check if any user exists
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # No users exist, create default Admin
        default_username = "admin"
        default_password = "password123"

        # Hash the password using SHA-256 (REQ-SAMS-019)
        hashed_pw = hashlib.sha256(default_password.encode()).hexdigest()

        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (default_username, hashed_pw, 'Admin')
        )
        conn.commit()
        print(f"Default Admin created. Username: '{default_username}', Password: '{default_password}'")
    else:
        print("Users already exist. Skipping default admin creation.")

    conn.close()


if __name__ == "__main__":
    # If this file is run directly,
    print("Initializing Student Attendance Management System Database...")
    setup_database()
    create_default_admin()
    print("Database initialization complete.")