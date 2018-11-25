import psycopg2
import db

def truncate():
    with db.get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('TRUNCATE filenames')
            cur.execute('TRUNCATE items')
            cur.execute('TRUNCATE values')
            cur.execute('TRUNCATE meta')
            cur.execute('TRUNCATE targets')

truncate()
