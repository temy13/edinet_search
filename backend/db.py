# coding=utf-8
import os
import psycopg2
from os.path import join, dirname
from dotenv import load_dotenv
import traceback
import etl
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

def insert_value(code, filename, value, part):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                c_value = etl.parse(value)
                cur.execute('INSERT INTO values (code, filename, value, origin_value, part) VALUES (%s, %s, %s, %s, %s)', (code, filename, c_value, value, part))
            conn.commit()
    except:
        print(filename)
        print(traceback.format_exc())

def insert_fn(code, filename):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO filenames (code, filename) VALUES (%s,%s)', (code, filename))
        conn.commit()

def save_values(fn, code, ds):
    for d in ds:
       insert_value(code, fn, d["value"], d["part"])
    insert_fn(code, fn)

def insert_item(code, filename, key, value, ishtml):
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('INSERT INTO items (code, filename, key, value, ishtml) VALUES (%s, %s, %s, %s, %s)', (code, filename, key, value, ishtml))
            conn.commit()
    except:
        print(filename)
        print(traceback.format_exc())

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
