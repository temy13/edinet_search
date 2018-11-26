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
from helper import *
import re
r = re.compile('[\d\-]+T[\d:]+')

def dt_convert(tdatetime):

    if type(tdatetime) is dt:
    	return tdatetime.strftime('%Y/%m/%d')
    if r.match(tdatetime) is not None:
        return dt.strptime(tdatetime, '%Y-%m-%dT%H:%M:%S').strftime('%Y/%m/%d')
    return tdatetime

app_log = logging.getLogger("tornado.application")
def search(query, offset=0, length=300, t_from="", t_to="", titles=[]):
    titles = title_filter(titles)
    count, data = es.search(query, offset=offset, t_from=t_from, t_to=t_to, titles=titles)
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
            titles = []#[title_normalize(k) for k in TITLES]
            q_titles = [{"name":k, "value":title_normalize(k), "checked":None} for k in TITLES]
            if 'titles' in self.request.arguments:
                titles = [x.decode('utf-8') for x in self.request.arguments['titles']]
                q_titles = [{"name":k, "value":title_normalize(k), "checked":("checked" if title_normalize(k) in titles else None)} for k in TITLES]
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
            self.render('index.html', count=0, data=[], query="",offset=0, t_from_month="", t_to_month="",t_from_year="", t_to_year="", length=300, candidates=[{"name":k, "value":title_normalize(k), "checked":None} for k in TITLES])

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
