import tkinter as tk
from tkinter import messagebox
import auth
import gui_dashboard


def launch_login_window():
    """
    Creates and displays the login window.
    """
    # Create the main window
    window = tk.Tk()
    window.title("SAMS - Login")
    window.geometry("350x250")  # Width x Height
    window.eval('tk::PlaceWindow . center')  # Center on screen
    window.configure(padx=20, pady=20)

    # --- UI Elements ---

    # Title Label
    title_label = tk.Label(window, text="SAMS Login", font=("Arial", 16, "bold"))
    title_label.pack(pady=(0, 20))

    # Username
    tk.Label(window, text="Username:", font=("Arial", 10)).pack(anchor="w")
    username_entry = tk.Entry(window, font=("Arial", 12), width=30)
    username_entry.pack(pady=(0, 10))

    # Password (show="*" hides the typed characters)
    tk.Label(window, text="Password:", font=("Arial", 10)).pack(anchor="w")
    password_entry = tk.Entry(window, font=("Arial", 12), width=30, show="*")
    password_entry.pack(pady=(0, 20))

    # --- Button Action ---
    def handle_login():
        """Triggered when the Login button is clicked."""
        # 1. Get what the user typed
        username = username_entry.get()
        password = password_entry.get()

        # 2. Basic validation (REQ-SAMS-002)
        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter both username and password.")
            return

        # 3. Check credentials using our auth module
        user_data = auth.authenticate_user(username, password)

        if user_data:
            # Login successful!
            messagebox.showinfo("Success", f"Welcome, {user_data['username']}! Role: {user_data['role']}")

            # Close the login window (In the next step, we will open the dashboard here instead)
            window.destroy()

            dashboard_window = tk.Tk()
            gui_dashboard.SAMSDashboard(dashboard_window, user_data)
            dashboard_window.mainloop()
        else:
            # Login failed
            messagebox.showerror("Login Failed", "Invalid username or password.")
            # Clear the password box so they can try again
            password_entry.delete(0, tk.END)

    # Login Button
    login_btn = tk.Button(window, text="Login", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
                          command=handle_login)
    login_btn.pack(fill="x")

    # Start the GUI loop
    window.mainloop()


# --- Run the application ---
if __name__ == "__main__":
    print("Launching SAMS Login Window...")
    launch_login_window()
