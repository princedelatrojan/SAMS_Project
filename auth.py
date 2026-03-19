import hashlib
import database


def hash_password(password):
    """
    Takes a plain text password and returns its SHA-256 hash.
    """
    return hashlib.sha256(password.encode()).hexdigest()




def authenticate_user(username, password):
    """
    Checks if the provided username and password match a record in the database.
    """
    # 1. Hash password the user just typed in
    hashed_input_password = hash_password(password)

    # 2. Connect to the database
    conn = database.get_connection()
    cursor = conn.cursor()

    # 3. Look up the user by their username
    cursor.execute(
        "SELECT username, password_hash, role FROM users WHERE username = ?",
        (username,)
    )

    # Fetch the first matching row
    user_record = cursor.fetchone()
    conn.close()

    # 4. Check if the user exists AND if the passwords match
    if user_record:
        if user_record['password_hash'] == hashed_input_password:
            return {
                "username": user_record["username"],
                "role": user_record["role"]
            }
    return None


# --- Testing Block ---
if __name__ == "__main__":
    print("Testing Authentication Module...")

    # Test 1: Correct credentials (using the admin)
    print("\nTest 1: Trying correct login...")
    result = authenticate_user("admin", "password123")
    if result:
        print(f"SUCCESS! Logged in as: {result['username']} with role {result['role']}")
    else:
        print("FAILED: Could not log in.")

    # Test 2: Incorrect credentials
    print("\nTest 2: Trying incorrect password...")
    bad_result = authenticate_user("admin", "wrongpassword")
    if bad_result is None:
        print("SUCCESS! System correctly blocked the bad password.")
    else:
        print("FAILED: System allowed a bad password!")