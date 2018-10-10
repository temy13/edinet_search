import os
import psycopg2

DATABASE_URL= ""

def get_connection():
    dsn = os.environ.get(DATABASE_URL)
    return psycopg2.connect(dsn)


def get_all():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM users')
            rows = cur.fetchall()

def insert():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO users (name) VALUES (%s)', ('foo',))
        conn.commit()
