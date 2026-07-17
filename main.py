
from getpass import getpass 

from app_model.db import conn
from app_model.users import add_user, get_user
from hashing import hash_password, validate_hash

#check if a user already exists in the database
def name_exists(conn, name):
    return get_user(conn, name) is not None

#user registration
def register_user(conn):
    name = input("Create a username: ")

    if name_exists(name):
        print("Username already exists.")
        return

    password = getpass("Create a password: ")
    confirm = getpass("Confirm password: ")

    if password != confirm:
        print("Password does not match.")
        return
    
    role = input("Role (admin/user): ").lower()
    if role not in ("admin", "user"):
        print("Invalid role.")
        return
    
    hashed_password = hash_password(password)
    add_user(conn, name, role, hashed_password)

#user login
def user_login(conn):
    name = input("Username: ")
    password = getpass("Password: ")

    user = get_user(conn, name)

    if user is None:
        return False

    id, user_name, role, user_hash = user

    if validate_hash(password, user_hash):
        print(f"Welcome {user_name}!")
        return role

    return False

#view users
def view_users(conn):
    cur = conn.cursor()

    cur.execute(
        """
        SELECT username, role
        FROM users
        """
    )
    users = cur.fetchall()
    print("\n=== REGISTERED USERS ===")

    if not users:
        print("No users found.")
        return

    for username, role in users:
        print(f"Username: {username} | Role: {role}")

#admin menu
def admin_menu(conn):
    while True:
        print("\n=== ADMIN MENU ===")
        print("1. View Users")
        print("2. Logout")

        choice = input("> ")

        if choice == "1":
            view_users(conn)

        elif choice == "2":
            print("Logging out...")
            break

        else:
            print("Invalid option.")

#user menu
def user_menu():
    while True:
        print("\n=== USER MENU ===")
        print("1. View Profile")
        print("2. Logout")

        choice = input("> ")

        if choice == "1":
            print("Welcome to your profile!")

        elif choice == "2":
            print("Logging out...")
            break

        else:
            print("Invalid option.")

def main():
    while True:
        print("\nWelcome to the system!!")
        print("Choose from the following options:")
        print("1. Register")
        print("2. Log in")
        print("3. Exit")

        choice = input(": > ")

        if choice == "1":
            register_user(conn)

        elif choice == "2":
            role = user_login(conn)

            if role == "admin":
                print("Admin Login Successful!")
                admin_menu(conn)

            elif role == "user":
                print("User Login Successful!")
                user_menu()

            else:
                print("Incorrect username or password.")

        elif choice == "3":
            print("Good bye!!")
            break

        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()





