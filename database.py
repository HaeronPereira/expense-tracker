import sqlite3


DATABASE = "expense_tracker.db"


def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


def create_tables():

    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            description TEXT NOT NULL,

            amount REAL NOT NULL,

            expense_date TEXT NOT NULL,

            category_id INTEGER,

            payment_method TEXT,

            notes TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (category_id)
                REFERENCES categories(id)
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            amount REAL NOT NULL,

            due_date TEXT NOT NULL,

            category_id INTEGER,

            status TEXT NOT NULL DEFAULT 'Unpaid',

            notes TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (category_id)
                REFERENCES categories(id)
        )
    """)

    connection.commit()

    connection.close()


if __name__ == "__main__":

    create_tables()

    print("Database created successfully.")