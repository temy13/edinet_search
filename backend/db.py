# coding=utf-8
import os
import psycopg2
from os.path import join, dirname
from dotenv import load_dotenv
import traceback
import etl
import re
from copy import copy
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
#postgresql://[user[:password]@][netloc][:port][/dbname]
import meta

def get_connection():
    dsn = os.environ.get("DATABASE_URL")
    return psycopg2.connect(dsn)


def get_filenames(code):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT filename FROM filenames where code = %s', (code, ))
            rows = cur.fetchall()
            return [row[0] for row in rows]

#def c_ts(a, n):
#    t = ""
#    if len(a) > n:
#        # t = a[n].replace("【","").replace("】","")
#        t = re.sub("[ -/:-@\[-~\s【】、。．（）]", "", a[n])
#        t = meta.zh_convert(t)
#
#    return t

def insert_value(code, filename, value, ts):
    if not ts:
        return
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                parsed_value = etl.parse(value)
                #cur.execute('INSERT INTO values (code, filename, value, origin_value, title1, title2, title3, title4, title5) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                #    (code, filename, parsed_value, value, c_ts(ts, 0), c_ts(ts, 1), c_ts(ts, 2), c_ts(ts, 3), c_ts(ts, 4))
                #)
                cur.execute('INSERT INTO values (code, filename, value, origin_value, title1) VALUES (%s, %s, %s, %s, %s)',
                    (code, filename, parsed_value, value, ts[0])
                )
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
    if not ds:
        print(fn, code)
        return
    ds = sorted(ds, key=lambda x:x['part'])
    html = "".join([x["value"] for x in ds])
    insert_value(code, fn, html, ["ALL"])
    return

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

def get_all_values(limit=100, offset=0, title=""):
    with get_connection() as conn:
        with conn.cursor() as cur:
             cur.execute("""
                   SELECT values.value, meta.publisher, meta.term, meta.term_from, meta.term_to, values.title1, values.title2, values.title3, values.title4, values.title5,values.id 
                   FROM values LEFT JOIN meta ON values.filename = meta.filename WHERE title1 = %s
                 ORDER BY values.id LIMIT %s OFFSET %s""", (title, limit, offset))
             rows = cur.fetchall()
             result = [{"value":row[0], "publisher":row[1], "term":row[2], "term_from":row[3], "term_to":row[4],
                "title1":row[5], "title2":row[6], "title3":row[7], "title4":row[8], "title5":row[9], "id":row[10]} for row in rows]
             return result

def get_data_by_fn(fn):
    with get_connection() as conn:
        with conn.cursor() as cur:
             cur.execute("""
                   SELECT values.origin_value, meta.publisher, meta.term, meta.term_from, meta.term_to, values.id, values.title1 
                   FROM values LEFT JOIN meta ON values.filename = meta.filename WHERE meta.filename = %s and values.title1 = 'ALL'
                 """, (fn,))
             rows = cur.fetchall()
             result = [{"origin":row[0], "publisher":row[1], "term":row[2], "term_from":row[3], "term_to":row[4], "id":row[5], "title":row[6]} for row in rows]
             return result

def get_meta(filename):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT publisher, term, term_from, term_to FROM meta where filename =  %s', (filename,))
            rows = cur.fetchall()
            return [{"publisher":row[0], "term":row[1], "term_from":row[2], "term_to":row[3]} for row in rows][0]


def insert_target(code, filename, value, key, publisher, term, term_from, term_to):
    p = publisher.replace("'","\'")
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO targets (code, value, key, filename, publisher, term, term_from, term_to) VALUES (%s,%s,%s, %s,%s,%s,%s,%s)', (code, value, key, filename, p, term, term_from, term_to))
        conn.commit()


