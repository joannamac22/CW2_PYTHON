#this function migrates users from users.txt into this database.
def migrate_users(conn):
    with open("DATA/users.txt", "r") as f:
        users = f.readlines()
    for user in users:
        name, role, password_hash = user.strip().split(",")
        add_user(conn, name, role, password_hash)

#this function is used to add a new user to the database. It checks for empty username,
#  valid role, and existing username before inserting the new user into the users table. 
#  It returns a tuple indicating success or failure along with a message.
def add_user(conn, name: str, role: str, password_hash: str) -> tuple[bool, str]:
    """Returns (success, message)."""
    if not name.strip():
        return False, "Username cannot be empty."
    if role not in ("user", "admin"):
        return False, "Role must be 'user' or 'admin'."

    existing = get_user(conn, name.strip())
    if existing:
        return False, f"Username '{name}' already exists."

    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, role, password_hash) VALUES (?, ?, ?)",
            (name.strip(), role, password_hash),
        )
        conn.commit()
        return True, f"User '{name}' created successfully."
    except Exception as e:
        return False, f"Database error: {e}"

#this function is used to retrieve a user from the database by their username.
#  It returns a dictionary containing the user's details or None if the user does not exist.
def row_to_dict(row, cursor) -> dict:
    """Safely convert a DB row (tuple or dict) to a dict."""
    if row is None:
        return {}
    if isinstance(row, dict):
        return row
    # Use cursor.description if available
    if cursor.description:
        cols = [d[0] for d in cursor.description]
        return dict(zip(cols, row))
    # Final fallback — assume column order: id, username, role, password_hash
    keys = ["id", "username", "role", "password_hash"]
    return dict(zip(keys, row))

#this function retrieves all users from the database and returns them as a list of dictionaries.
def get_all_users(conn) -> list[dict]:
    """Returns all users as a list of dicts. Never raises — returns [] on any error."""
    def _row_to_dict(row, cursor) -> dict:
        if isinstance(row, dict):
            return row
        if cursor.description:
            cols = [d[0] for d in cursor.description]
            return dict(zip(cols, row))
        #fallback assume order: id, username, role, password_hash
        return dict(zip(["id", "username", "role", "password_hash"], row))

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users")
        rows = cur.fetchall()
        if not rows:
            return []
        return [_row_to_dict(row, cur) for row in rows]
    except Exception:
        return []

#this function retrieves a user from the database by their username
#  and returns their details as a dictionary.
def get_user(conn, name):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (name,))
    row = cur.fetchone()
    if not row:
        return None
    if isinstance(row, dict):
        return row
    if cur.description:
        cols = [d[0] for d in cur.description]
        return dict(zip(cols, row))
    return dict(zip(["id", "username", "role", "password_hash"], row))

#this function updates a user's role in the database. It checks for valid
#  role input and returns a tuple indicating success or failure along with a message.
def update_user_role(conn, name: str, new_role: str) -> tuple[bool, str]:
    """Change a user's role. Returns (success, message)."""
    if new_role not in ("user", "admin"):
        return False, "Role must be 'user' or 'admin'."
    try:
        cur = conn.cursor()
        cur.execute("UPDATE users SET role = ? WHERE username = ?", (new_role, name))
        conn.commit()
        if cur.rowcount == 0:
            return False, f"User '{name}' not found."
        return True, f"Role updated to '{new_role}'."
    except Exception as e:
        return False, f"Database error: {e}"

#this function deletes a user from the database by their username. It prevents 
# self-deletion and returns a tuple indicating success or failure along with a message.
def delete_user(conn, name: str, current_username: str) -> tuple[bool, str]:
    """Delete a user by username. Prevents self-deletion. Returns (success, message)."""
    if name == current_username:
        return False, "You cannot delete your own account."
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE username = ?", (name,))
        conn.commit()
        if cur.rowcount == 0:
            return False, f"User '{name}' not found."
        return True, f"User '{name}' deleted successfully."
    except Exception as e:
        return False, f"Database error: {e}"