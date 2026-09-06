import sqlite3

DB_NAME = "urls.db"


def init_db():
    """Initialize the database and create the urls table if it doesnt exist"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        # We will primarly use uuid as the primary key so it can scale better for now i am using
        # Integer just for small scale
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS urls(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_code TEXT UNIQUE NOT NULL,
            original_url TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            click_count INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()


def get_db_connection():
    """return a connection to the sqlite database"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def insert_url(short_code, original_url, created_at, expires_at):
    """Inserts a url with  its  short code"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO urls (short_code,original_url , created_at, expires_at)
            VALUES (?, ?,?,?)
            """,
            (short_code, original_url, created_at, expires_at),
        )
        conn.commit()
    finally:
        conn.close()


def get_url_by_code(short_code):
    """Gets the original url for the short url"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM urls WHERE short_code = ?", (short_code,))
        row = cursor.fetchone()
    finally:
        conn.close()
    return row


def increment_click(short_code):
    """Increments the count when the url is redirected"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE urls SET click_count = click_count + 1 where short_code = ?",
            (short_code,),
        )
        conn.commit()
    finally:
        conn.close()
