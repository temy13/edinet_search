# coding=utf-8
import os
import psycopg2
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#postgresql://[user[:password]@][netloc][:port][/dbname]

def get_connection():
    dsn = os.environ.get("DATABASE_URL")
    return psycopg2.connect(dsn)


LIMIT=10

def get_values(query, t_from="", t_to="", offset=0):
    t_from = "1980/01/01" if not t_from else t_from
    t_to = "2030/12/31" if not t_to else t_to
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT count(distinct(values.id, values.value, values.filename)) FROM values LEFT JOIN meta ON values.filename = meta.filename
                WHERE
                    values.value LIKE %s AND
                    meta.term_from >= %s AND
                    meta.term_to <= %s
                """, ("%" + query + "%", t_from, t_to))
            count = cur.fetchone()
            cur.execute("""
                SELECT distinct values.value, values.filename, values.id FROM values LEFT JOIN meta ON values.filename = meta.filename
                WHERE
                    values.value LIKE %s AND
                    meta.term_from >= %s AND
                    meta.term_to <= %s
                ORDER BY values.id
                LIMIT %s
                OFFSET %s
            """, ("%" + query + "%", t_from, t_to, LIMIT, offset))
            rows = cur.fetchall()
            return count[0], [{"value":row[0], "filename":row[1] } for row in rows]


def get_meta(filename):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT publisher, term, term_from, term_to FROM meta where filename =  %s', (filename,))
            rows = cur.fetchall()
            return [{"publisher":row[0], "term":row[1], "term_from":row[2], "term_to":row[3]} for row in rows]
