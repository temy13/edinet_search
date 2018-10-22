import os
import tornado.ioloop
import tornado.web
import json
import db
from bs4 import BeautifulSoup
import traceback
from datetime import datetime as dt

def dt_convert(tdatetime):
    return tdatetime.strftime('%Y/%m/%d')

def search(query, offset=0):
    count, data = db.get_items(query, offset)
    rdata = []
    for d in data:
        dx = {}
        content = d["value"] 
        if d["ishtml"]:
            soup = BeautifulSoup(content, "lxml")
            content = soup.getText()
        content = content.replace("\n","").replace("\u3000","")
        pos = content.find(query)
        s = pos - 300 if pos > 300 else 0
        dx["value"] = content[s:s+600]
        if len(content) > 600:
            dx["value"] += "..."

        meta = db.get_meta(d["filename"])
        if not meta:
          dx["publisher"] = dx["term_from"] = dx["term_to"] = dx["term"] = ""
          continue

        dx.update(meta[0])

        dx["term_from"] = dt_convert(dx["term_from"])
        dx["term_to"] = dt_convert(dx["term_to"])
        rdata.append(dx)
    #print(vexist)
    return count, rdata


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            query = self.get_argument("query", "")
            offset = self.get_argument("offset", 0)
            if query:
                count, data = search(query, offset)
            else:
                count = 0
                data = []
            self.render('index.html', count=count, data=data, query=query, offset=int(offset))
        except:
            print(traceback.format_exc())
            self.render('index.html', count=0, data=[], query="",offset=0)
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
