import webapp2
from datetime import datetime, timedelta
import logging
import cgi
import re
import jinja2
import os
import hashlib
import urllib2
from urllib2 import URLError
import json
from google.appengine.ext import db
from google.appengine.api import memcache

from models import User, Post
from hashes import Hashers


#########################################################################################
#                           Template Setup
#########################################################################################

template_dir = os.path.join( os.path.dirname(__file__), 'templates' )
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                        autoescape = True)


#########################################################################################
#                           Validating User Input
#########################################################################################
class Validators():
    months = ['January',
              'February',
              'March',
              'April',
              'May',
              'June',
              'July',
              'August',
              'September',
              'October',
              'November',
              'December']

    month_abbs = dict( (m[:3].lower(), m ) for m in months )

    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    def valid_username(self, username):
        return username and self.USER_RE.match(username)

    PASS_RE = re.compile(r"^.{3,20}$")
    def valid_password(self, password):
        return password and self.PASS_RE.match(password)

    EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
    def valid_email(self, email):
        return not email or self.EMAIL_RE.match(email)

    # validation functions unit-1
    def val_month(self, month):
        if month:
            short_m = month[:3].lower()
            return self.month_abbs.get( short_m )

    def val_day(self, day):
        if day and day.isdigit():
            day = int(day)
            if day > 0 and day <= 31:
                return day

    def val_year(self, year):
        if year and year.isdigit():
            year = int(year)
            if year > 1900 and year <= 2020:
                return year

    def escape_html(self, s):
        return cgi.escape(s, quote=True)


##################################################################################################
#                       Global Classes and Variables
##################################################################################################

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler, Hashers):
    def age_set(self, key, value):
        save_time = datetime.utcnow()
        memcache.set(key, (value, save_time))

    def age_get(self, key):
        r = memcache.get(key)
        if r:
            val, save_time = r
            age = (datetime.utcnow() - save_time).total_seconds()
        else:
            val, age = None, 0
        return val, age

    def add_post(self, post):
        post.put()
        self.top_posts(update=True)
        return str(post.key().id())
    
    def top_posts(self, update=False):
        key = 'main_page_posts'
        q = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 20")
        posts, age = self.age_get(key)
        if posts is None or update:
            #prevent from running database query multiple times
            posts = list(q)
            self.age_set(key, posts)
        return posts, age

    def age_str(self, age):
        s = "Queried %s seconds ago"
        age = int(age)
        if age == 1:
            s = s.replace("seconds", "second")
        return s % age

    def top_arts(self, update=False):
        key = 'top'
        arts = memcache.get(key)
        if arts is None or update:
            logging.error("DB Query")
            arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC LIMIT 10")
            #prevent from running database query multiple times
            memcache.set(key, arts)
        return arts 
    
    IP_URL = "http://ip-api.com/json/"
    def get_coords(self, ip):
        url = self.IP_URL + ip
        content = None 
        try:
            content = urllib2.urlopen(url).read()
        except URLError:
            return
        if content:
            # parse the json and find coordinates
            js = json.loads(content)
            lat = js['lat']
            lon = js['lon']
            return db.GeoPt(lat, lon)
    
    GMAPS_URL = "http://maps.googleapis.com/maps/api/staticmap?size=380x263&sensor=false&"
    def gmaps_img(self, points):
        markers = '&'.join('markers=%s,%s' % (p.lat, p.lon) for p in points)
        return self.GMAPS_URL + markers

    def render_json(self, d):
        json_txt = json.dumps(d)
        self.response.headers['Content-Type'] = 'application/json; charset=UTF-8'
        self.write(json_txt)

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        self.response.headers['Content-Type'] = 'text/plain'
        new_cookie_val = self.hash_str( val, hashlib.sha256 )
        self.response.headers.add_header( 'Set-Cookie','%s=%s;Path=/' % (name, new_cookie_val) )
    
    def read_secure_cookie(self, name):
        cookie_str = self.request.cookies.get(name)
        return cookie_str and self.check_hash_str(cookie_str, hashlib.sha256)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers.add_header('Set-Cookie', "user_id=;Path=/")

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.get_by_id(int(uid))

        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'
