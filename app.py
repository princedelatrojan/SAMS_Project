from flask import Flask, render_template_string, request, redirect, url_for, session, flash, Response
import auth
import logic
import datetime
import csv
import io

app = Flask(__name__)
app.secret_key = "sams_super_secret_key_2024"

# ==========================================
# HTML TEMPLATES (Using Tailwind CSS)
# ==========================================

BASE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAMS Web Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen flex flex-col">
    <!-- Navigation Bar -->
    {% if session.username %}
    <nav class="bg-indigo-600 text-white shadow-lg">
        <div class="max-w-7xl mx-auto px-4 flex justify-between h-16 items-center">
            <div class="font-bold text-xl tracking-wider">SAMS</div>
            <div class="flex space-x-4">
                <a href="{{ url_for('dashboard') }}" class="hover:bg-indigo-500 px-3 py-2 rounded">Home</a>
                <a href="{{ url_for('attendance') }}" class="hover:bg-indigo-500 px-3 py-2 rounded">Mark Attendance</a>
                <a href="{{ url_for('view_reports') }}" class="hover:bg-indigo-500 px-3 py-2 rounded">View Reports</a>
                {% if session.role == 'Admin' %}
                <a href="{{ url_for('manage_students') }}" class="hover:bg-indigo-500 px-3 py-2 rounded text-yellow-300 font-semibold">Manage Students</a>
                {% endif %}
                <a href="{{ url_for('logout') }}" class="bg-red-500 hover:bg-red-600 px-3 py-2 rounded font-semibold ml-4">Logout</a>
            </div>
        </div>
    </nav>
    {% endif %}

    <!-- Flash Messages -->
    <div class="max-w-6xl mx-auto mt-4 w-full px-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="p-4 mb-4 rounded shadow-sm text-white font-semibold {% if category == 'error' %}bg-red-500{% else %}bg-green-500{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
    </div>

    <main class="flex-grow flex justify-center p-4">
        {% block content %}{% endblock %}
    </main>
</body>
</html>
"""

LOGIN_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", """
<div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-md mt-10 h-fit">
    <h2 class="text-3xl font-bold text-center text-gray-800 mb-8">SAMS Login</h2>
    <form action="{{ url_for('login') }}" method="POST" class="space-y-6">
        <div>
            <label class="block text-sm font-medium text-gray-700">Username</label>
            <input type="text" name="username" required class="mt-1 block w-full px-4 py-2 border rounded-md">
        </div>
        <div>
            <label class="block text-sm font-medium text-gray-700">Password</label>
            <input type="password" name="password" required class="mt-1 block w-full px-4 py-2 border rounded-md">
        </div>
        <button type="submit" class="w-full bg-indigo-600 text-white font-bold py-3 px-4 rounded-md hover:bg-indigo-700 transition">Log In</button>
    </form>
</div>
""")

DASHBOARD_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", """
<div class="text-center w-full max-w-4xl mt-10">
    <h1 class="text-5xl font-extrabold text-gray-800 mb-4">Welcome to SAMS</h1>
    <p class="text-xl text-gray-600 mb-8">Logged in as: <span class="font-bold text-indigo-600">{{ session.username }}</span> ({{ session.role }})</p>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <a href="{{ url_for('attendance') }}" class="bg-white p-6 rounded-lg shadow-md border-t-4 border-indigo-500 hover:shadow-lg transition">
            <h3 class="text-xl font-bold text-gray-800 mb-2">Mark Attendance</h3>
            <p class="text-gray-600 text-sm">Start a daily attendance session.</p>
        </a>
        <a href="{{ url_for('view_reports') }}" class="bg-white p-6 rounded-lg shadow-md border-t-4 border-blue-500 hover:shadow-lg transition">
            <h3 class="text-xl font-bold text-gray-800 mb-2">View Reports</h3>
            <p class="text-gray-600 text-sm">See past records & Export to CSV.</p>
        </a>
        {% if session.role == 'Admin' %}
        <a href="{{ url_for('manage_students') }}" class="bg-white p-6 rounded-lg shadow-md border-t-4 border-green-500 hover:shadow-lg transition">
            <h3 class="text-xl font-bold text-gray-800 mb-2">Manage Students</h3>
            <p class="text-gray-600 text-sm">View, Add, or Edit students.</p>
        </a>
        {% endif %}
    </div>
</div>
""")

MANAGE_STUDENTS_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", """
<div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-5xl h-fit mt-6">
    <div class="flex justify-between items-center border-b pb-4 mb-6">
        <h2 class="text-3xl font-bold text-gray-800">Student Database</h2>
        <a href="{{ url_for('add_student') }}" class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition">
            + Register New Student
        </a>
    </div>

    <div class="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 rounded-lg">
        <table class="min-w-full divide-y divide-gray-300">
            <thead class="bg-gray-100">
                <tr>
                    <th class="py-3 px-4 text-left text-sm font-semibold text-gray-900">Roll No</th>
                    <th class="py-3 px-4 text-left text-sm font-semibold text-gray-900">Name</th>
                    <th class="py-3 px-4 text-left text-sm font-semibold text-gray-900">Class</th>
                    <th class="py-3 px-4 text-left text-sm font-semibold text-gray-900">Contact</th>
                    <th class="py-3 px-4 text-center text-sm font-semibold text-gray-900">Actions</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 bg-white">
                {% for stu in students %}
                <tr class="hover:bg-gray-50">
                    <td class="whitespace-nowrap py-3 px-4 text-sm font-medium text-gray-900">{{ stu.roll_no }}</td>
                    <td class="whitespace-nowrap py-3 px-4 text-sm text-gray-700">{{ stu.name }}</td>
                    <td class="whitespace-nowrap py-3 px-4 text-sm text-gray-500">{{ stu.class_id }}</td>
                    <td class="whitespace-nowrap py-3 px-4 text-sm text-gray-500">{{ stu.contact_info }}</td>
                    <td class="whitespace-nowrap py-3 px-4 text-sm text-center">
                        <a href="{{ url_for('edit_student', student_id=stu.student_id) }}" class="text-indigo-600 hover:text-indigo-900 font-semibold bg-indigo-50 px-3 py-1 rounded">Edit</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% if not students %}
        <p class="p-6 text-center text-gray-500">No students found. Add a student to get started.</p>
        {% endif %}
    </div>
</div>
""")

STUDENT_FORM_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", """
<div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-2xl h-fit mt-10">
    <h2 class="text-3xl font-bold text-gray-800 mb-6 border-b pb-2">
        {% if student %}Edit Student{% else %}Register New Student{% endif %}
    </h2>
    <form action="{% if student %}{{ url_for('edit_student', student_id=student.student_id) }}{% else %}{{ url_for('add_student') }}{% endif %}" method="POST" class="space-y-6">
        <div class="grid grid-cols-2 gap-6">
            <div>
                <label class="block text-sm font-medium text-gray-700">Roll Number</label>
                <input type="text" name="roll_no" value="{{ student.roll_no if student else '' }}" required class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md">
            </div>
            <div>
                <label class="block text-sm font-medium text-gray-700">Class/Section</label>
                <input type="text" name="class_id" value="{{ student.class_id if student else '' }}" required class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md">
            </div>
            <div class="col-span-2">
                <label class="block text-sm font-medium text-gray-700">Full Name</label>
                <input type="text" name="name" value="{{ student.name if student else '' }}" required class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md">
            </div>
            <div class="col-span-2">
                <label class="block text-sm font-medium text-gray-700">Contact Email</label>
                <input type="email" name="contact_info" value="{{ student.contact_info if student else '' }}" class="mt-1 block w-full px-4 py-2 border border-gray-300 rounded-md">
            </div>
        </div>
        <div class="flex gap-4">
            <a href="{{ url_for('manage_students') }}" class="w-1/3 text-center bg-gray-200 text-gray-800 font-bold py-3 px-4 rounded-md hover:bg-gray-300 transition">Cancel</a>
            <button type="submit" class="w-2/3 bg-green-600 text-white font-bold py-3 px-4 rounded-md hover:bg-green-700 transition">Save Student</button>
        </div>
    </form>
</div>
""")

ATTENDANCE_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", """
<div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-4xl h-fit mt-6">
    <h2 class="text-3xl font-bold text-gray-800 mb-6 border-b pb-2">Mark Daily Attendance</h2>

    <form action="{{ url_for('attendance') }}" method="POST" class="flex gap-4 items-end mb-8 bg-indigo-50 p-6 rounded-lg border border-indigo-100 shadow-sm">
        <div class="flex-1">
            <label class="block text-sm font-semibold text-indigo-900 mb-1">Select Class</label>
            <select name="class_id" required class="block w-full px-4 py-2 border border-gray-300 rounded-md bg-white">
                <option value="" disabled {% if not selected_class %}selected{% endif %}>-- Choose a class --</option>
                {% for c in classes %}
                <option value="{{ c }}" {% if c == selected_class %}selected{% endif %}>{{ c }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="flex-1">
            <label class="block text-sm font-semibold text-indigo-900 mb-1">Select Date</label>
            <input type="date" name="date" value="{{ selected_date }}" required class="block w-full px-4 py-2 border border-gray-300 rounded-md">
        </div>
        <button type="submit" class="bg-indigo-600 text-white font-bold py-2 px-6 rounded-md hover:bg-indigo-700 h-[42px] shadow">Load Students</button>
    </form>

    {% if students %}
    <form action="{{ url_for('submit_attendance') }}" method="POST">
        <input type="hidden" name="date" value="{{ selected_date }}">
        <div class="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 rounded-lg mb-6">
            <table class="min-w-full divide-y divide-gray-300">
                <thead class="bg-gray-100">
                    <tr>
                        <th class="py-3 pl-4 text-left text-sm font-semibold text-gray-900">Roll No</th>
                        <th class="py-3 px-3 text-left text-sm font-semibold text-gray-900">Student Name</th>
                        <th class="py-3 px-3 text-center text-sm font-semibold text-gray-900">Status</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-200 bg-white">
                    {% for stu in students %}
                    <tr class="hover:bg-gray-50">
                        <td class="whitespace-nowrap py-3 pl-4 text-sm font-medium text-gray-900">{{ stu.roll_no }}</td>
                        <td class="whitespace-nowrap py-3 px-3 text-sm text-gray-700">{{ stu.name }}</td>
                        <td class="whitespace-nowrap py-3 px-3 text-center">
                            <select name="status_{{ stu.student_id }}" class="border-gray-300 rounded-md text-sm font-semibold p-2 
                                {% if stu.status == 'Absent' %}bg-red-100 text-red-800{% elif stu.status == 'Excused' %}bg-yellow-100 text-yellow-800{% else %}bg-green-100 text-green-800{% endif %}">
                                <option value="Present" {% if stu.status == 'Present' or not stu.status %}selected{% endif %}>Present</option>
                                <option value="Absent" {% if stu.status == 'Absent' %}selected{% endif %}>Absent</option>
                                <option value="Excused" {% if stu.status == 'Excused' %}selected{% endif %}>Excused</option>
                            </select>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <button type="submit" class="w-full bg-green-600 text-white font-bold py-3 px-4 rounded-md hover:bg-green-700 shadow-lg text-lg">Save Attendance</button>
    </form>
    {% endif %}
</div>
""")

VIEW_REPORTS_HTML = BASE_HTML.replace("{% block content %}{% endblock %}", """
<div class="bg-white p-8 rounded-lg shadow-xl w-full max-w-4xl h-fit mt-6">
    <h2 class="text-3xl font-bold text-gray-800 mb-6 border-b pb-2">Attendance Reports</h2>

    <form action="{{ url_for('view_reports') }}" method="POST" class="flex gap-4 items-end mb-8 bg-gray-50 p-4 rounded border">
        <div class="flex-1">
            <label class="block text-sm font-medium text-gray-700">Class</label>
            <select name="class_id" required class="mt-1 block w-full px-4 py-2 border rounded-md bg-white">
                <option value="" disabled {% if not selected_class %}selected{% endif %}>-- Choose --</option>
                {% for c in classes %}
                <option value="{{ c }}" {% if c == selected_class %}selected{% endif %}>{{ c }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="flex-1">
            <label class="block text-sm font-medium text-gray-700">Date</label>
            <input type="date" name="date" value="{{ selected_date }}" required class="mt-1 block w-full px-4 py-2 border rounded-md">
        </div>
        <button type="submit" class="bg-blue-600 text-white font-bold py-2 px-6 rounded-md hover:bg-blue-700 h-[42px]">View Report</button>
    </form>

    {% if records != None %}
        {% if records|length > 0 %}
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-xl font-bold text-gray-700">Results for {{ selected_class }} on {{ selected_date }}</h3>
                <a href="{{ url_for('export_csv', class_id=selected_class, date=selected_date) }}" class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded shadow flex items-center gap-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                    Export to CSV
                </a>
            </div>
            <div class="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 rounded-lg">
                <table class="min-w-full divide-y divide-gray-300">
                    <thead class="bg-gray-100">
                        <tr>
                            <th class="py-3 px-4 text-left text-sm font-semibold text-gray-900">Roll No</th>
                            <th class="py-3 px-4 text-left text-sm font-semibold text-gray-900">Name</th>
                            <th class="py-3 px-4 text-left text-sm font-semibold text-gray-900">Status</th>
                        </tr>
                    </thead>
                    <tbody class="divide-y divide-gray-200 bg-white">
                        {% for row in records %}
                        <tr>
                            <td class="whitespace-nowrap py-3 px-4 text-sm text-gray-900">{{ row.roll_no }}</td>
                            <td class="whitespace-nowrap py-3 px-4 text-sm text-gray-700">{{ row.name }}</td>
                            <td class="whitespace-nowrap py-3 px-4 text-sm font-bold 
                                {% if row.status == 'Absent' %}text-red-600{% elif row.status == 'Excused' %}text-yellow-600{% else %}text-green-600{% endif %}">
                                {{ row.status }}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        {% else %}
            <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                <p class="text-yellow-700">No attendance records found for this class on this date.</p>
            </div>
        {% endif %}
    {% endif %}
</div>
""")


# ==========================================
# FLASK ROUTES
# ==========================================

@app.route("/")
def index():
    if "username" in session: return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = auth.authenticate_user(request.form.get("username"), request.form.get("password"))
        if user:
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password.", "error")
    return render_template_string(LOGIN_HTML)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))


@app.route("/dashboard")
def dashboard():
    if "username" not in session: return redirect(url_for('login'))
    return render_template_string(DASHBOARD_HTML)


# --- NEW: Manage Students Route ---
@app.route("/manage_students")
def manage_students():
    if "username" not in session or session.get("role") != "Admin":
        flash("Admin access required.", "error")
        return redirect(url_for('dashboard'))

    students = logic.get_all_students()
    return render_template_string(MANAGE_STUDENTS_HTML, students=students)


# --- UPDATED: Add Student Route ---
@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if "username" not in session or session.get("role") != "Admin": return redirect(url_for('dashboard'))
    if request.method == "POST":
        success, msg = logic.add_student(
            request.form.get("roll_no"), request.form.get("name"),
            request.form.get("class_id"), request.form.get("contact_info")
        )
        if success:
            flash(msg, "success")
            return redirect(url_for('manage_students'))
        else:
            flash(msg, "error")
    return render_template_string(STUDENT_FORM_HTML, student=None)


# --- NEW: Edit Student Route ---
@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):
    if "username" not in session or session.get("role") != "Admin": return redirect(url_for('dashboard'))

    if request.method == "POST":
        success, msg = logic.update_student(
            student_id, request.form.get("roll_no"), request.form.get("name"),
            request.form.get("class_id"), request.form.get("contact_info")
        )
        if success:
            flash(msg, "success")
            return redirect(url_for('manage_students'))
        else:
            flash(msg, "error")

    student = logic.get_student_by_id(student_id)
    return render_template_string(STUDENT_FORM_HTML, student=student)


# --- UPDATED: Attendance Route ---
@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if "username" not in session: return redirect(url_for('login'))

    classes = logic.get_all_classes()
    selected_date = datetime.date.today().strftime("%Y-%m-%d")
    selected_class = None
    students = None

    if request.method == "POST":
        selected_class = request.form.get("class_id")
        selected_date = request.form.get("date")

        # We fetch attendance reports too, so if attendance was already marked, it shows the saved statuses!
        saved_attendance = {row['roll_no']: row['status'] for row in
                            logic.get_attendance_report(selected_class, selected_date)}
        students = logic.get_students_by_class(selected_class)

        # Inject saved statuses into the student dicts
        for stu in students:
            stu['status'] = saved_attendance.get(stu['roll_no'], 'Present')

        if not students:
            flash(f"No students found in '{selected_class}'.", "error")

    return render_template_string(ATTENDANCE_HTML, classes=classes, students=students,
                                  selected_date=selected_date, selected_class=selected_class)


@app.route("/submit_attendance", methods=["POST"])
def submit_attendance():
    if "username" not in session: return redirect(url_for('login'))

    date = request.form.get("date")
    attendance_list = []

    for key, value in request.form.items():
        if key.startswith("status_"):
            student_id = int(key.split("_")[1])
            attendance_list.append({"student_id": student_id, "status": value})

    success, msg = logic.submit_attendance(attendance_list, date)
    if success:
        flash(msg, "success")
    else:
        flash(msg, "error")
    return redirect(url_for('attendance'))


# --- NEW: View Reports Route ---
@app.route("/view_reports", methods=["GET", "POST"])
def view_reports():
    if "username" not in session: return redirect(url_for('login'))

    classes = logic.get_all_classes()
    selected_date = datetime.date.today().strftime("%Y-%m-%d")
    selected_class = None
    records = None

    if request.method == "POST":
        selected_class = request.form.get("class_id")
        selected_date = request.form.get("date")
        records = logic.get_attendance_report(selected_class, selected_date)

    return render_template_string(VIEW_REPORTS_HTML, classes=classes, records=records,
                                  selected_date=selected_date, selected_class=selected_class)


# --- NEW: Export CSV Route (REQ-SAMS-013) ---
@app.route("/export_csv/<class_id>/<date>")
def export_csv(class_id, date):
    if "username" not in session: return redirect(url_for('login'))

    records = logic.get_attendance_report(class_id, date)

    # Create the CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Roll Number', 'Student Name', 'Attendance Status'])  # Headers
    for row in records:
        writer.writerow([row['roll_no'], row['name'], row['status']])

    # Send the file to the user's browser for download
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=Attendance_{class_id}_{date}.csv"}
    )


if __name__ == "__main__":
    app.run(debug=True)