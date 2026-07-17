#creating a database
def create_user_table(conn):
    cur = conn.cursor()
    sql = '''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    role TEXT NOT NULL,
    password_hash TEXT NOT NULL);
    '''
    cur.execute(sql)
    conn.commit()