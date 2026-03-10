import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import logic


class SAMSDashboard:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data

        self.root.title(f"SAMS Dashboard - Logged in as: {user_data['username']} ({user_data['role']})")
        self.root.geometry("800x500")
        self.root.eval('tk::PlaceWindow . center')

        # --- Layout setup (Left Menu, Right Content) ---
        self.menu_frame = tk.Frame(self.root, width=200, bg="#2C3E50")
        self.menu_frame.pack(side="left", fill="y")

        self.content_frame = tk.Frame(self.root, bg="#ECF0F1")
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.setup_menu()
        self.show_home()  # Show home screen by default

    def clear_content(self):
        """Removes all widgets from the content frame so we can load a new page."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def setup_menu(self):
        """Creates navigation buttons based on user role (REQ-SAMS-006)."""
        tk.Label(self.menu_frame, text="Navigation Menu", font=("Arial", 14, "bold"), bg="#2C3E50", fg="white").pack(
            pady=20)

        # Everyone gets Home and Mark Attendance
        tk.Button(self.menu_frame, text="Home", font=("Arial", 12), command=self.show_home).pack(fill="x", pady=5,
                                                                                                 padx=10)
        tk.Button(self.menu_frame, text="Mark Attendance", font=("Arial", 12), command=self.show_attendance).pack(
            fill="x", pady=5, padx=10)

        # ONLY Admins get the Add Student button
        if self.user_data['role'] == 'Admin':
            tk.Button(self.menu_frame, text="Add Student", font=("Arial", 12), command=self.show_add_student).pack(
                fill="x", pady=5, padx=10)

        tk.Button(self.menu_frame, text="Exit", font=("Arial", 12), command=self.root.destroy).pack(fill="x",
                                                                                                    side="bottom",
                                                                                                    pady=20, padx=10)

    # ===================== PAGES =====================

    def show_home(self):
        self.clear_content()
        tk.Label(self.content_frame, text=f"Welcome to SAMS, {self.user_data['username']}!", font=("Arial", 20, "bold"),
                 bg="#ECF0F1").pack(pady=50)
        tk.Label(self.content_frame, text="Select an option from the menu to begin.", font=("Arial", 14),
                 bg="#ECF0F1").pack()

    def show_add_student(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Add New Student", font=("Arial", 18, "bold"), bg="#ECF0F1").pack(pady=20)

        # Form fields
        form_frame = tk.Frame(self.content_frame, bg="#ECF0F1")
        form_frame.pack()

        tk.Label(form_frame, text="Roll Number:", font=("Arial", 12), bg="#ECF0F1").grid(row=0, column=0, pady=10,
                                                                                         sticky="e")
        roll_entry = tk.Entry(form_frame, font=("Arial", 12))
        roll_entry.grid(row=0, column=1, pady=10, padx=10)

        tk.Label(form_frame, text="Full Name:", font=("Arial", 12), bg="#ECF0F1").grid(row=1, column=0, pady=10,
                                                                                       sticky="e")
        name_entry = tk.Entry(form_frame, font=("Arial", 12))
        name_entry.grid(row=1, column=1, pady=10, padx=10)

        tk.Label(form_frame, text="Class/Section:", font=("Arial", 12), bg="#ECF0F1").grid(row=2, column=0, pady=10,
                                                                                           sticky="e")
        class_entry = tk.Entry(form_frame, font=("Arial", 12))
        class_entry.grid(row=2, column=1, pady=10, padx=10)

        tk.Label(form_frame, text="Contact Email:", font=("Arial", 12), bg="#ECF0F1").grid(row=3, column=0, pady=10,
                                                                                           sticky="e")
        contact_entry = tk.Entry(form_frame, font=("Arial", 12))
        contact_entry.grid(row=3, column=1, pady=10, padx=10)

        def submit():
            # Call logic.py to save the student
            success, msg = logic.add_student(roll_entry.get(), name_entry.get(), class_entry.get(), contact_entry.get())
            if success:
                messagebox.showinfo("Success", msg)
                self.show_add_student()  # Refresh form
            else:
                messagebox.showerror("Error", msg)

        tk.Button(form_frame, text="Save Student", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
                  command=submit).grid(row=4, column=0, columnspan=2, pady=20)

    def show_attendance(self):
        self.clear_content()
        tk.Label(self.content_frame, text="Mark Daily Attendance", font=("Arial", 18, "bold"), bg="#ECF0F1").pack(
            pady=10)

        # Top Controls (Class and Date)
        top_frame = tk.Frame(self.content_frame, bg="#ECF0F1")
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="Class:", font=("Arial", 12), bg="#ECF0F1").grid(row=0, column=0, padx=5)
        class_entry = tk.Entry(top_frame, font=("Arial", 12), width=15)
        class_entry.grid(row=0, column=1, padx=5)
        # Default it to the class we created in the test earlier for convenience
        class_entry.insert(0, "Computer Science 1")

        tk.Label(top_frame, text="Date:", font=("Arial", 12), bg="#ECF0F1").grid(row=0, column=2, padx=5)
        date_entry = tk.Entry(top_frame, font=("Arial", 12), width=15)
        date_entry.grid(row=0, column=3, padx=5)
        date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

        # Treeview (Table) to display students
        columns = ("ID", "Roll No", "Name", "Status")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=10)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor="center")
        tree.pack(pady=10)

        def load_students():
            # Clear existing rows
            for row in tree.get_children():
                tree.delete(row)

            # Fetch from logic module
            students = logic.get_students_by_class(class_entry.get())
            if not students:
                messagebox.showinfo("Info", "No students found for this class.")
                return

            # Insert into table (Defaulting to Present per REQ-SAMS-010)
            for stu in students:
                tree.insert("", "end", values=(stu['student_id'], stu['roll_no'], stu['name'], "Present"))

        def toggle_status():
            """Changes selected student's status between Present and Absent."""
            selected_item = tree.selection()
            if not selected_item:
                messagebox.showwarning("Select", "Please select a student to toggle status.")
                return

            for item in selected_item:
                values = list(tree.item(item, "values"))
                # Toggle logic
                values[3] = "Absent" if values[3] == "Present" else "Present"
                tree.item(item, values=values)

        def save_attendance():
            attendance_list = []
            for item in tree.get_children():
                values = tree.item(item, "values")
                # Build the dictionary logic.py expects
                attendance_list.append({"student_id": values[0], "status": values[3]})

            if not attendance_list:
                messagebox.showerror("Error", "No students loaded.")
                return

            success, msg = logic.submit_attendance(attendance_list, date_entry.get())
            if success:
                messagebox.showinfo("Success", msg)
                self.show_home()
            else:
                messagebox.showerror("Error", msg)

        tk.Button(top_frame, text="Load Students", font=("Arial", 10, "bold"), command=load_students).grid(row=0,
                                                                                                           column=4,
                                                                                                           padx=10)

        btn_frame = tk.Frame(self.content_frame, bg="#ECF0F1")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Toggle Present/Absent", font=("Arial", 10), command=toggle_status, bg="#f39c12",
                  fg="white").pack(side="left", padx=10)
        tk.Button(btn_frame, text="Submit Attendance to Database", font=("Arial", 12, "bold"), command=save_attendance,
                  bg="#4CAF50", fg="white").pack(side="left", padx=10)


# --- Testing Block ---
if __name__ == "__main__":
    print("Launching SAMS Dashboard Test...")
    root = tk.Tk()
    # Simulating a successful Admin login for testing purposes
    mock_user_data = {"username": "admin", "role": "Admin"}
    app = SAMSDashboard(root, mock_user_data)
    root.mainloop()