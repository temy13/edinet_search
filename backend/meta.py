import db
import pandas as pd
import os
import traceback
import re
import etl
import sys

z_digit = ["０", "１", "２", "３", "４","５", "６", "７", "８", "９", "１０"]
m_digit = ["⓪", "①", "②", "③", "④","⑤", "⑥", "⑦", "⑧", "⑨", "⑩"]
h_digit = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
zh_digit = {z:h for z, h in zip(z_digit, h_digit)}
mh_digit = {m:h for m, h in zip(m_digit, h_digit)}
term_words = ["第", "期"]

def zh_convert(s):
    for z in z_digit:
        s = s.replace(z, zh_digit[z])
    for m in m_digit:
        s = s.replace(m, mh_digit[m])
    return s

def h_convert(s):
    i = int(re.sub(r'\D','',s))
    if i <= 30:
      return str(1988 + int(re.sub(r'\D','',s)))
    else:
      return i

def convert(s):
    ss = s.split("/")
    return "%s/%s/%s" % (h_convert(ss[0]), ss[1], ss[2])


def space_split(t):
    t = etl.parse(t)
    t = re.sub("[^\s\d１２３４５６７８９０年月第期]", " ", t)
    t = re.sub("\s+", " ", t)
    t = t.replace("年","/")
    t = t.replace("月","/")
    t = zh_convert(t)
    x = re.split(r'\s', t)
    return [w for w in x if w]

def save_meta(fn):
    try:
        publishers = db.get_items(filename=fn, key="jpsps_cor:IssuerNameCoverPage".lower())
        if not publishers:
            print(fn)
            return
        publisher = publishers[0]
        t = db.get_items(filename=fn, key="jpsps_cor:AccountingPeriodCoverPage".lower())
        if not t:
            print("t", fn)
            return
        splited_t = space_split(t[0])
        term=splited_t[0]
        term_from = convert(splited_t[1])
        term_to = convert(splited_t[2])
        db.insert_meta(fn, publisher, term, term_from, term_to)
    except:
        print(fn)
        print(traceback.format_exc())
        sys.exit()

def get_codes():
    df = pd.read_csv(os.getcwd() + "/backend/codes.csv")
    return df
