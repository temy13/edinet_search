import db
import pandas as pd
import os
import traceback
import re

z_digit = ["０", "１", "２", "３", "４","５", "６", "７", "８", "９"]
h_digit = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
zh_digit = {z:h for z, h in zip(z_digit, h_digit)}

def h_convert(s):
    return str(1988 + int(re.sub(r'\D','',s)))

def convert(s):
    #s = s.replace("平成","")
    s = s.replace("）","")
    s = s.replace("日","")
    s = s.replace("年","/")
    s = s.replace("月","/")
    for z in z_digit:
        s = s.replace(z, zh_digit[z])
    print(s)
    ss = s.split("/")
    print(ss)

    return "%s/%s/%s" % (h_convert(ss[0]), ss[1], ss[2])


def save_meta(fn):
    try:
        publishers = db.get_items(filename=fn, key="jpsps_cor:IssuerNameCoverPage".lower())
        publisher = publishers[0]
        t = db.get_items(filename=fn, key="jpsps_cor:AccountingPeriodCoverPage".lower())
        t = t[0]
        term = t.split("（")[0]
        term_from = convert(t.split("　")[1])
        term_to = convert(t.split("　")[3])
        print(term)
        print(term_from)
        print(term_to)
        db.insert_meta(fn, publisher, term, term_from, term_to)
    except:
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
