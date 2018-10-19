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


def get_filenames(code):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT filename FROM filenames where code = %s', (code, ))
            rows = cur.fetchall()
            return [row[0] for row in rows]

def insert_item(code, filename, key, value, ishtml):
    #print(type(code), type(filename), type(value), type(ishtml))
    #print(code,filename, key, str(value), ishtml, type(str(value)))
    v = str(value).replace("'","\'")
    with get_connection() as conn:
        with conn.cursor() as cur:
            sql = """INSERT INTO items (code, filename, key, value, ishtml) VALUES ('%s', '%s', '%s', '%s', %s)""" % (code, filename, key, v, ishtml)
            #print(sql)
            cur.execute(sql)
        conn.commit()

def insert_fn(code, filename):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO filenames (code, filename) VALUES (%s,%s)', (code, filename))
        conn.commit()

def save_items(fn, code, ds):
    for d in ds:
        insert_item(code, fn, d["key"], d["value"], d["ishtml"])
    insert_fn(code, fn)


def get_items(key, filename):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT value FROM items where key = %s and filename = %s', (key, filename))
            rows = cur.fetchall()
            return [row[0] for row in rows]


def insert_meta(filename, publisher, term, term_from, term_to):
    p = publisher.replace("'","\'")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO meta (filename, publisher, term, term_from, term_to) VALUES (%s,%s,%s,%s,%s)', (filename, p, term, term_from, term_to))
        conn.commit()
