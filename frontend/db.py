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
            cur.execute('SELECT code, value FROM items where value LIKE %s limit %s', ("%" + query + "%", LIMIT))
            rows = cur.fetchall()
            return [{"code":row[0],"value":row[1]} for row in rows]
