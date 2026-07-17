import sqlite3
#this is the database connection function
def get_connection():
    conn = sqlite3.connect("DATA/project_data.db", check_same_thread=False)
    return conn