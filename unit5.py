import json
import urllib2
from handlers import Handler
from google.appengine.api import memcache

from reddit_json import reddit_front

class APIHandler(Handler):
    def get(self):
        j = json.loads(reddit_front)
        self.write( reduce( lambda q, p: p+q , [i['data']['ups'] for i in j['data']['children']] ) )

class FlushCache(Handler):
    def get(self):
        memcache.flush_all()
        self.redirect("/blog/")

