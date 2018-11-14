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


def result_filter(result):
    r = []
    check = set([])
    #自分より下が既に存在していたらスルー
    for n in [5, 4, 3, 2, 1]:
        for d in [r for r in result if r["title" + str(n)]]:
            t = False

            k = d["publisher"] + d["term"]
            check.add(k)
            if k not in check:
                t = True

            for i in range(1,6):
                k += d["title" + str(i)]
                if k not in check:
                    t = True
                check.add(k)
            if t:
                r.append(d)
    return r




LIMIT=10

def get_values(query, t_from="", t_to="", offset=0, titles=[]):
    t_from = "1980/01/01" if not t_from else t_from
    t_to = "2030/12/31" if not t_to else t_to
    q_titles = str(tuple(titles)).replace(',)',')')
    offset = int(offset)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT distinct values.value, meta.publisher, meta.term, meta.term_from, meta.term_to, values.title1, values.title2, values.title3, values.title4, values.title5 FROM values LEFT JOIN meta ON values.filename = meta.filename
                WHERE
                    values.value LIKE %s AND
                    meta.term_from >= %s AND
                    meta.term_to <= %s AND
                    (values.title1 in """ + q_titles + """ OR
                    values.title2 in """ + q_titles + """ OR
                    values.title3 in """ + q_titles + """ OR
                    values.title4 in """ + q_titles + """ OR
                    values.title5 in """ + q_titles + """)
                ORDER BY meta.term_to DESC
                """, ("%" + query + "%", t_from, t_to))
            rows = cur.fetchall()
            result = [{"value":row[0], "publisher":row[1], "term":row[2], "term_from":row[3], "term_to":row[4],
                "title1":row[5], "title2":row[6], "title3":row[7], "title4":row[8], "title5":row[9]} for row in rows]
            result = result_filter(result)
            # cur.execute("""
            #     SELECT distinct values.value, meta.publisher, meta.term, meta.term_from, meta.term_to, values.title1, values.title2, values.title3, values.title4, values.title5
            #     FROM values LEFT JOIN meta ON values.filename = meta.filename
            #     WHERE
            #         values.value LIKE %s AND
            #         meta.term_from >= %s AND
            #         meta.term_to <= %s AND
            #         values.title1 in """ + q_titles + """
            #         values.title2 in """ + q_titles + """
            #         values.title3 in """ + q_titles + """
            #         values.title4 in """ + q_titles + """
            #         values.title5 in """ + q_titles + """
            #     ORDER BY values.filename
            #     LIMIT %s
            #     OFFSET %s
            # """, ("%" + query + "%", t_from, t_to, LIMIT, offset))
            # rows = cur.fetchall()
            # result = [{"value":row[0], "filename":row[1], "publisher":row[2], "term":row[3], "term_from":row[4], "term_to":row[5],
            #     "title1":row[6], "title2":row[7], "title3":row[8], "title4":row[9], "title":row[10]
            #     } for row in rows]
            # return count[0], [{"value":row[0], "filename":row[1], "publisher":row[2], "term":row[3], "term_from":row[4], "term_to":row[5] } for row in rows]
            return len(result), result[offset:offset+LIMIT]


# def get_meta(filename):
#     with get_connection() as conn:
#         with conn.cursor() as cur:
#             cur.execute('SELECT publisher, term, term_from, term_to FROM meta where filename =  %s', (filename,))
#             rows = cur.fetchall()
#             return [{"publisher":row[0], "term":row[1], "term_from":row[2], "term_to":row[3]} for row in rows]
