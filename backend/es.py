from elasticsearch import Elasticsearch, helpers
from pprint import pprint
import db
import sys
import scrape
import re
conf = {"host": "127.0.0.1", "port": 9200,
         "index": "edinet", "doc_type": "edinet"}
import etl 
es = Elasticsearch("{}:{}".format(conf["host"], conf["port"]))
n = 0
LIMIT = 1000

z_digit = ["０", "１", "２", "３", "４","５", "６", "７", "８", "９", "１０"]
m_digit = ["⓪", "①", "②", "③", "④","⑤", "⑥", "⑦", "⑧", "⑨", "⑩"]
h_digit = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

zh_digit = {z:h for z, h in zip(z_digit, h_digit)}
mh_digit = {m:h for m, h in zip(m_digit, h_digit)}

def zh_convert(s):
    for z in z_digit:
        s = s.replace(z, zh_digit[z])
    for m in m_digit:
        s = s.replace(m, mh_digit[m])
    return s

def key_value(t):
    t = re.sub("[ -/:-@\[-~\s【】、。．（）]", "", t)
    t = zh_convert(t)
    return t

KEYS = [
"表紙",
"第一部 ファンド情報",
"第１ ファンドの状況",
"１ 投資法人の概況",
"(1) 主要な経営指標等の推移",
"(2) 投資法人の目的及び基本的性格",
"(3) 投資法人の仕組み",
"(4) 投資法人の機構",
"(5) 投資法人の出資総額",
"(6) 主要な投資主の状況",
"(7) 資産運用会社従業員等投資口所有制度の内容",
"２ 投資方針",
"(1) 投資方針",
"(2) 投資対象",
"(3) 分配方針",
"(4) 投資制限",
"３ 投資リスク",
"４ 手数料等及び税金",
"(1) 申込手数料",
"(2) 買戻し手数料",
"(3) 管理報酬等",
"(4) その他の手数料等",
"(5) 課税上の取扱い",
"５ 運用状況",
"(1) 投資状況",
"(2) 投資資産",
"① 投資有価証券の主要銘柄",
"② 投資不動産物件",
"③ その他投資資産の主要なもの",
"(3) 運用実績",
"① 純資産等の推移",
"② 分配の推移",
"③ 自己資本利益率（収益率）の推移",
"第二部 投資法人の詳細情報",
"第１ 投資法人の追加情報",
"１ 投資法人の沿革",
"２ 役員の状況",
"３ その他",
"第２ 手続等",
"１ 申込（販売）手続等",
"２ 買戻し手続等",
"第３ 管理及び運営",
"１ 資産管理等の概要",
"(1) 資産の評価",
"(2) 保管",
"(3) 存続期間",
"(4) 計算期間",
"(5) その他",
"２ 利害関係人との取引制限",
"３ 投資主・投資法人債権者の権利",
"第４ 関係法人の状況",
"１ 資産運用会社の概況",
"(1) 名称、資本金の額及び事業の内容",
"(2) 運用体制",
"(3) 大株主の状況",
"(4) 役員の状況",
"(5) 事業の内容及び営業の概況",
"２ その他の関係法人の概況",
"(1) 名称、資本金の額及び事業の内容",
"(2) 関係業務の概要",
"(3) 資本関係",
"第５ 投資法人の経理状況",
"１ 財務諸表",
"(1) 貸借対照表",
"(2) 損益計算書",
"(3) 投資主資本等変動計算書",
"(4) 金銭の分配に係る計算書",
"(5) キャッシュ・フロー計算書",
"(6) 注記表",
"(7) 附属明細表",
"２ 投資法人の現況",
"純資産額計算書",
"第６ 販売及び買戻しの実績",
"第７ 参考情報",
"監査報告書"
]


KEYS_SUB = {
"表紙":["表紙"],
"第一部 ファンド情報":["第一部 ファンド情報","第１ ファンドの状況","１ 投資法人の概況","(1) 主要な経営指標等の推移","(2) 投資法人の目的及び基本的性格","(3) 投資法人の仕組み","(4) 投資法人の機構","(5) 投資法人の出資総額","(6) 主要な投資主の状況",],
"第１ ファンドの状況":[],
"１ 投資法人の概況":[],
"(1) 主要な経営指標等の推移":[],
"(2) 投資法人の目的及び基本的性格":[],
"(3) 投資法人の仕組み":[],
"(4) 投資法人の機構":[],
"(5) 投資法人の出資総額":[],
"(6) 主要な投資主の状況":[],
"(7) 資産運用会社従業員等投資口所有制度の内容":[],
"２ 投資方針":[],
"(1) 投資方針":[],
"(2) 投資対象":[],
"(3) 分配方針":[],
"(4) 投資制限":[],
"３ 投資リスク":[],
"４ 手数料等及び税金":[],
"(1) 申込手数料":[],
"(2) 買戻し手数料":[],
"(3) 管理報酬等":[],
"(4) その他の手数料等":[],
"(5) 課税上の取扱い":[],
"５ 運用状況":[],
"(1) 投資状況":[],
"(2) 投資資産":[],
"① 投資有価証券の主要銘柄":[],
"② 投資不動産物件":[],
"③ その他投資資産の主要なもの":[],
"(3) 運用実績":[],
"① 純資産等の推移":[],
"② 分配の推移":[],
"③ 自己資本利益率（収益率）の推移":[],
"第二部 投資法人の詳細情報":[],
"第１ 投資法人の追加情報":[],
"１ 投資法人の沿革":[],
"２ 役員の状況":[],
"３ その他":[],
"第２ 手続等":[],
"１ 申込（販売）手続等":[],
"２ 買戻し手続等":[],
"第３ 管理及び運営":[],
"１ 資産管理等の概要":[],
"(1) 資産の評価":[],
"(2) 保管":[],
"(3) 存続期間":[],
"(4) 計算期間":[],
"(5) その他":[],
"２ 利害関係人との取引制限":[],
"３ 投資主・投資法人債権者の権利":[],
"第４ 関係法人の状況":[],
"１ 資産運用会社の概況":[],
"(1) 名称、資本金の額及び事業の内容":[],
"(2) 運用体制":[],
"(3) 大株主の状況":[],
"(4) 役員の状況":[],
"(5) 事業の内容及び営業の概況":[],
"２ その他の関係法人の概況":[],
"(1) 名称、資本金の額及び事業の内容":[],
"(2) 関係業務の概要":[],
"(3) 資本関係":[],
"第５ 投資法人の経理状況":[],
"１ 財務諸表":[],
"(1) 貸借対照表":[],
"(2) 損益計算書":[],
"(3) 投資主資本等変動計算書":[],
"(4) 金銭の分配に係る計算書":[],
"(5) キャッシュ・フロー計算書":[],
"(6) 注記表":[],
"(7) 附属明細表":[],
"２ 投資法人の現況":[],
"純資産額計算書":[],
"第６ 販売及び買戻しの実績":[],
"第７ 参考情報":[],
"監査報告書":[]
}





keys = [key_value(k) for k in KEYS]
def ex_parse(html, fn):
    #titles = re.findall("<h\d[\s\S]*?>.*?<\/h\d>", html)
    #titles = [x for x in re.findall("<h1(.|\s)*?>(.|\s)*?<\/h1>", html)]
    divs = [x for x in re.split("<h\d(.|\s)*?>", html) if x and "</h" in x]
    titles = []
    for div in divs:
        t_idx = div.find("</h")
        t = div[:t_idx]
        t_v = key_value(t)
        if t_v in keys:
            titles.append(t)
    titles.append("監査報告書") 
    html = etl.extract_html(html) 
    text = etl.parse(html) 
    d = {}
    for n in range(len(titles)-1):
        f_idx = text.find(titles[n]) 
        t_idx = text.find(titles[n+1])
        subtext = text[f_idx:t_idx]
        d[key_value(titles[n])] = subtext
    f_idx = text.find(titles[-1]) 
    subtext = text[f_idx:-1]
    d[key_value(titles[-1])] = subtext
    insert_es(d, fn)

def main():
    df = scrape.get_codes()

    for index, item in df.iterrows():
        code = item["code"]
        filenames = db.get_filenames(code)
        for fn in filenames[:1]:
            data = db.get_data_by_fn(fn)
            if not data:
                continue
            ex_parse(data[0]["origin"], fn)
    print("----")

def insert_es(d, fn):
    datas = []
    for k,v in d.items():
        v = connection(d, k)
        row = get_meta(fn)
        d = {
	   "value":d["value"],
	   "key":key,	
	   "term":row["term"],
	   "publisher":row["publisher"],
	   "term_date_range": {
	     "gte":row["term_from"],
	     "lte":row["term_to"]
	   }
        }
        datas.append({'_id':row["id"], '_op_type':'create','_index':conf["index"],'_type':conf["doc_type"],'_source':d})
     
    helpers.bulk(client=es,actions=datas,refresh=True,chunk_size=1000,request_timeout=150)
    print("inserted", n, n*LIMIT+len(datas) )
    n += 1