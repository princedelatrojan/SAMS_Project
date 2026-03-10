Student Attendance Management System (SAMS)

A modern, web-based intranet application designed to eliminate the inefficiencies of manual, paper-based attendance tracking in educational institutions.

About The Project

The Student Attendance Management System (SAMS) was developed as a comprehensive Software Engineering project adhering to IEEE Std 830-1998 documentation standards.

Designed for a single educational department, SAMS replaces traditional paper registers with a fast, secure, and intuitive digital solution. The system is built with a strict Modular Architecture, separating the User Interface, Core Application Logic, Authentication, and Database layers to ensure maximum maintainability and scalability.

Key Features

Role-Based Access Control (RBAC): Distinct permissions for Administrators (full access) and Teachers (attendance marking and reporting).

Secure Authentication: Industry-standard SHA-256 password hashing ensures user credentials are computationally secure.

Student Management: Full CRUD operations for student records, including duplicate roll-number prevention and real-time editing.

Streamlined Attendance Marking: An intuitive, responsive dashboard that defaults students to "Present" for rapid submission, equipped with database transaction safety (COMMIT/ROLLBACK) to prevent data loss.

Automated Reporting & Export: Instantly generate attendance reports by class and date, with one-click CSV data exporting for academic records.

System Architecture

SAMS is built using Python and the Flask web framework, styled with Tailwind CSS. It follows a clean separation of concerns:

database.py (Data Layer): Handles the SQLite connection, table schemas (Users, Students, Attendance), and initialization.

auth.py (Security Layer): Manages secure login validation and cryptographic hashing.

logic.py (Business Logic): The core engine handling data retrieval, attendance logic, and database transactions.

app.py (Presentation Layer): The Flask web server that routes requests and renders the dynamic, responsive UI.

Getting Started

Follow these instructions to get a local copy of the project up and running on your machine.

Prerequisites

Python 3.8 or higher installed on your system.

Installation & Setup

Clone the repository:

git clone [https://github.com/yourusername/SAMS.git](https://github.com/yourusername/SAMS.git)
cd SAMS


Create a virtual environment (Recommended):

python -m venv .venv

# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate


Install the required packages:

pip install flask


Initialize the Database:
Run the database script to create the tables and generate the default Administrator account.

python database.py


(You should see a success message indicating the database was initialized).

Start the Web Server:

python app.py


Access the Application:
Open your web browser and navigate to: http://127.0.0.1:5000

Default Credentials

Upon initializing the database for the first time, the system generates a default Admin account for testing purposes:

Username: admin

Password: password123

(Note: It is highly recommended to add a new admin and delete these default credentials in a production environment).

Screenshots

(Hint: Take some screenshots of your running app and put them in a folder called assets, then uncomment these lines!)

<!--
-->

Project Team

This system was designed, documented, and developed by:

Paul Karanja

Anita Alice

Agnes Wambui Njeri

Cecilia Adol

Developed as a Software Engineering Academic Project.
