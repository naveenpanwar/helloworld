# custom imports
from handlers import Validators, Handler, Hashers
import hashlib

###################################################################################################
#                         Unit 4
###################################################################################################

class CookieHandler(Handler, Validators, Hashers):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        visits = 0
        
        visits_cookie_str = self.request.cookies.get('visits')
        if visits_cookie_str:
            cookie_val = self.check_hash_str(visits_cookie_str, hashlib.md5 )
            if cookie_val:
                visits = int(cookie_val)
        visits += 1
        
        new_cookie_val = self.hash_str( str(visits), hashlib.md5 )
        self.response.headers.add_header( 'Set-Cookie','visits=%s' % new_cookie_val )
        if visits > 10:
            self.write("You are the best ever!")
        else:
            self.write("You've been here %s times!" % str(visits) )
