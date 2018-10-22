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

def get_items(query, offset=0):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT count(*) FROM items where ishtml = true AND value LIKE %s ', ("%" + query + "%", ))
            count = cur.fetchone()
            cur.execute('SELECT value, filename, ishtml, key FROM items where ishtml = true AND value LIKE %s ORDER BY id LIMIT %s OFFSET %s', ("%" + query + "%", LIMIT, offset))
            rows = cur.fetchall()
            return count[0], [{"value":row[0], "filename":row[1], "ishtml":row[2], "key":row[3]} for row in rows]


def get_meta(filename):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT publisher, term, term_from, term_to FROM meta where filename =  %s', (filename,))
            rows = cur.fetchall()
            return [{"publisher":row[0], "term":row[1], "term_from":row[2], "term_to":row[3]} for row in rows]
