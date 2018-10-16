import os
import tornado.ioloop
import tornado.web
import json
import db

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html', data=[], query="",offset=0)

    def post(self):
        query = self.get_argument("query", "")
        data = db.get_items(query)
        self.render('index.html', data=data, query=query, offset=self.get_argument("offset", 0))


class SampleHandler(tornado.web.RequestHandler):
    def get(self):
        data = {
            "test":1,
            "sample":2
        }
        my_json = json.dumps(data)
        self.write(my_json)


BASE_DIR = os.path.dirname(__file__)

application = tornado.web.Application([
        (r'/', MainHandler),
        (r'/sample', SampleHandler),
        ],
        template_path=os.path.join(BASE_DIR, 'templates'),
        static_path=os.path.join(BASE_DIR, 'static'),
)

if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
