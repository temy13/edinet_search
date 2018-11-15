import db
import pandas as pd
import os
import traceback
import re

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
    #s = s.replace("平成","")
    s = s.replace("）","")
    s = s.replace("日","")
    s = s.replace("年","/")
    s = s.replace("月","/")
    for z in z_digit:
        s = s.replace(z, zh_digit[z])
    allowed = ["/"] + h_digit
    for w in [w for w in s if w not in allowed]:
        s = s.replace(w, "")
    ss = s.split("/")
    return "%s/%s/%s" % (h_convert(ss[0]), ss[1], ss[2])

def term_convert(s):
    allowed = term_words + z_digit + h_digit
    for w in [w for w in s if w not in allowed]:
        s = s.replace(w, "")
    return s

def space_split(t):
    x = re.split(r'\s', t)
    allowed = term_words + z_digit + h_digit + ["年","月","日","/"]
    for s in x:
        for w in [w for w in s if w not in allowed]:
            s = s.replace(w, "")
    return [w for w in x if w]

def save_meta(fn):
    try:
        publishers = db.get_items(filename=fn, key="jpsps_cor:IssuerNameCoverPage".lower())
        if not publishers:
            print(fn)
            return
        publisher = publishers[0]
        t = db.get_items(filename=fn, key="jpsps_cor:AccountingPeriodCoverPage".lower())
        t = re.sub("\s+", " ", t[0].replace("至",""))
        term = term_convert(re.split("[（\s]", t)[0])
        splited_t = space_split(t)
        term_from = convert(splited_t[1])
        term_to = convert(splited_t[2])
        #print(fn, publisher, term, term_from, term_to)
        db.insert_meta(fn, publisher, term, term_from, term_to)
    except:
        print(fn)
        print(traceback.format_exc())

def get_codes():
    df = pd.read_csv(os.getcwd() + "/backend/codes.csv")
    return df

if __name__ == '__main__':
    df = get_codes()
    for index, item in df[2:3].iterrows():
        code = item["code"]
        print(code)
        filenames = db.get_filenames(code)
        for fn in filenames:
            save_meta(fn)
