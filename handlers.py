import webapp2
import cgi
import re
import jinja2
import os
import hashlib

from models import User
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
