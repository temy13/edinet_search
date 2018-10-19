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

def search(query):
    data = db.get_items(query)
    for d in data:
        content = d["value"]
        if d["ishtml"]:
            soup = BeautifulSoup(content, "lxml")
            content = soup.getText()
        meta = db.get_meta(d["filename"])
        d.update(meta[0])

        d["term_from"] = dt_convert(d["term_from"])
        d["term_to"] = dt_convert(d["term_to"])

        pos = content.find(query)
        s = pos - 300 if pos > 300 else 0
        d["value"] = content[s:s+600]
        if len(content) > 600:
            d["value"] += "..."
    return data


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html', data=[], query="",offset=0)

    def post(self):
        try:
            query = self.get_argument("query", "")
            data = search(query)
            self.render('index.html', data=data, query=query, offset=self.get_argument("offset", 0))
        except:
            print(traceback.format_exc())
            self.render('index.html', data=[], query="",offset=0)


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
