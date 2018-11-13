import os
import tornado.ioloop
import tornado.web
import json
import db
from bs4 import BeautifulSoup
import traceback
import datetime
from datetime import datetime as dt

def dt_convert(tdatetime):
    return tdatetime.strftime('%Y/%m/%d')

def search(query, offset=0, length=300, t_from="", t_to="", parts=[]):
    count, data = db.get_values(query, offset=offset, t_from=t_from, t_to=t_to, parts=parts)
    rdata = []
    for d in data:
        dx = {}
        content = d["value"]
        # if d["ishtml"]:
        soup = BeautifulSoup(content, "lxml")
        content = soup.getText()
        content = content.replace("\n","").replace("\u3000","")
        pos = content.find(query)
        s = pos - length if pos > length else 0
        dx["value"] = content[s:s+(length*2)]
        if len(content) > (length*2):
            dx["value"] += "..."

        meta = db.get_meta(d["filename"])
        if not meta:
          dx["publisher"] = dx["term_from"] = dx["term_to"] = dx["term"] = ""
          continue

        dx.update(meta[0])

        dx["term_from"] = dt_convert(dx["term_from"])
        dx["term_to"] = dt_convert(dx["term_to"])
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

            parts = []
            q_part = [None, None, None]
            if 'parts' in self.request.arguments:
                parts = [int(x) for x in self.request.arguments['parts']]
                q_part = [
                    "checked" if x in parts else None
                    for x in [1,2,3]
                ]

            if query or t_from or t_to:
                count, data = search(query, offset=offset, length=int(length), t_from=t_from, t_to=t_to, parts=parts)
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
                part=q_part
            )
        except:
            print(traceback.format_exc())
            self.render('index.html', count=0, data=[], query="",offset=0, t_from_month="", t_to_month="",t_from_year="", t_to_year="", length=300, part=
            [None,None,None])
#        self.render('index.html', count=0, data=[], query="",offset=0)

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
    application.listen(8888)
    print("Server on port 8888...")
    tornado.ioloop.IOLoop.current().start()
