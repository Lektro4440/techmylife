import sqlite3

# Initialize the database or connect to an existing one
def initialize_database():
    conn = sqlite3.connect('leaderboard.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY,
            username TEXT,
            score INTEGER
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_database()
    print("Database initialized.")
