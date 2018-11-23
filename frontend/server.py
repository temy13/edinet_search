import os
import tornado.ioloop
import tornado.web
import tornado.options
import json
from bs4 import BeautifulSoup
import traceback
import datetime
from datetime import datetime as dt
import re
import tornado.log
import logging
import es
import db
import re
r = re.compile('[\d\-]+T[\d:]+')
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

def dt_convert(tdatetime):
    
    if type(tdatetime) is dt:
    	return tdatetime.strftime('%Y/%m/%d')
    if r.match(tdatetime) is not None:
        return dt.strptime(tdatetime, '%Y-%m-%dT%H:%M:%S').strftime('%Y/%m/%d')
    return tdatetime

app_log = logging.getLogger("tornado.application")
def search(query, offset=0, length=300, t_from="", t_to="", titles=[]):
    #count, data = db.get_values(query, offset=offset, t_from=t_from, t_to=t_to, titles=titles)
    titles = title_filter(titles)
    count, data = es.search(query, offset=offset, t_from=t_from, t_to=t_to, titles=titles)
    #if count == 0:
    #    count, data = db.get_targets(query, offset=offset, t_from=t_from, t_to=t_to, titles=titles)
    print(count, len(data))   
    rdata = []
    for d in data:
        dx = {}
        content = d["value"]
        soup = BeautifulSoup(content, "lxml")
        content = soup.getText()
        content = content.replace("\n","").replace("\u3000","")
        pos = content.find(query)
        s = pos - length if pos > length else 0
        dx["value"] = content[s:s+(length*2)]
        if len(content) > (length*2):
            dx["value"] += "..."

        dx["publisher"] = d["publisher"]
        dx["term"] = d["term"]
        dx["term_from"] = dt_convert(d["term_from"])
        dx["term_to"] = dt_convert(d["term_to"])
        rdata.append(dx)

    return count, rdata


def dt_query_convert(year, month, isfirst):
    if not year or not month:
        return ""
    if isfirst:
        return "%s/%s/01" % (str(year), str(month))
    if int(month) == 12:
      _dt = datetime.date(int(year), 12, 31)
    else:
      _dt = datetime.date(int(year), int(month)+1, 1) - datetime.timedelta(days=1)
    return dt_convert(_dt)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            query = self.get_argument("query", "")
            offset = self.get_argument("offset", 0)
            length = self.get_argument("length", 300)
            t_from_year = self.get_argument("t_from_year", "")
            t_from_month = self.get_argument("t_from_month", "")
            t_to_year = self.get_argument("t_to_year", "")
            t_to_month = self.get_argument("t_to_month", "")

            t_from = dt_query_convert(t_from_year, t_from_month, True)
            t_to = dt_query_convert(t_to_year, t_to_month, False)
            titles = []#[key_value(k) for k in KEYS]
            q_titles = [{"name":k, "value":key_value(k), "checked":None} for k in KEYS]
            if 'titles' in self.request.arguments:
                titles = [x.decode('utf-8') for x in self.request.arguments['titles']]
                q_titles = [{"name":k, "value":key_value(k), "checked":("checked" if key_value(k) in titles else None)} for k in KEYS]
            if query or t_from or t_to:
                count, data = search(query, offset=offset, length=int(length), t_from=t_from, t_to=t_to, titles=titles)
            else:
                count = 0
                data = []
            self.render('index.html',
                count=count,
                data=data,
                query=query,
                offset=int(offset),
                t_from_month=t_from_month,
                t_to_month=t_to_month,
                t_from_year=t_from_year,
                t_to_year=t_to_year,
                length=int(length),
                candidates=q_titles
            )
        except:
            print(traceback.format_exc())
            self.render('index.html', count=0, data=[], query="",offset=0, t_from_month="", t_to_month="",t_from_year="", t_to_year="", length=300, candidates=[{"name":k, "value":key_value(k), "checked":None} for k in KEYS])

    # def post(self):
    #     try:
    #         query = self.get_argument("query", "")
    #         count, data = search(query)
    #         self.render('index.html', count=count, data=data, query=query, offset=self.get_argument("offset", 0))
    #     except:
    #         print(traceback.format_exc())
    #         self.render('index.html', couunt=0, data=[], query="",offset=0)


BASE_DIR = os.path.dirname(__file__)

application = tornado.web.Application([
        (r'/', MainHandler),
        ],
        template_path=os.path.join(BASE_DIR, 'templates'),
        static_path=os.path.join(BASE_DIR, 'static'),
)

if __name__ == '__main__':
    tornado.options.parse_command_line()
    application.listen(8888)
    print("Server on port 8888...")
    tornado.ioloop.IOLoop.current().start()
