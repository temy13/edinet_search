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

def get_values(query, t_from="", t_to="", offset=0, parts=[]):
    t_from = "1980/01/01" if not t_from else t_from
    t_to = "2030/12/31" if not t_to else t_to
    parts = parts if parts else [0,1,2,3,-1]
    q_part = str(tuple(parts)).replace(',)',')')
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT count(distinct(values.value, values.filename, meta.publisher, meta.term, meta.term_from, meta.term_to)) FROM values LEFT JOIN meta ON values.filename = meta.filename
                WHERE
                    values.value LIKE %s AND
                    meta.term_from >= %s AND
                    meta.term_to <= %s AND
                    values.part in """ + q_part
                , ("%" + query + "%", t_from, t_to))
            count = cur.fetchone()
            cur.execute("""
                SELECT distinct values.value, values.filename, meta.publisher, meta.term, meta.term_from, meta.term_to
                FROM values LEFT JOIN meta ON values.filename = meta.filename
                WHERE
                    values.value LIKE %s AND
                    meta.term_from >= %s AND
                    meta.term_to <= %s AND
                    values.part in """ + q_part + """
                ORDER BY values.filename
                LIMIT %s
                OFFSET %s
            """, ("%" + query + "%", t_from, t_to, LIMIT, offset))
            rows = cur.fetchall()
            return count[0], [{"value":row[0], "filename":row[1], "publisher":row[2], "term":row[3], "term_from":row[4], "term_to":row[5] } for row in rows]


# def get_meta(filename):
#     with get_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute('SELECT publisher, term, term_from, term_to FROM meta where filename =  %s', (filename,))
#             rows = cur.fetchall()
#             return [{"publisher":row[0], "term":row[1], "term_from":row[2], "term_to":row[3]} for row in rows]
