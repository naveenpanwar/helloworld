import json
import urllib2
from handlers import Handler

from reddit_json import reddit_front

class APIHandler(Handler):
    def get(self):
        j = json.loads(reddit_front)
        self.write( reduce( lambda q, p: p+q , [i['data']['ups'] for i in j['data']['children']] ) )
