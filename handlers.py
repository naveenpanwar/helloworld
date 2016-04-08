import webapp2
import cgi
import re
import jinja2
import os
import hashlib
import hmac
import random
import string

SECRET = "TORSO"

#########################################################################################
#                           Template Setup
#########################################################################################

template_dir = os.path.join( os.path.dirname(__file__), 'templates' )
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                        autoescape = True)

##################################################################################################
#                       Global Classes and Variables
##################################################################################################

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        return render_str(template, **params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

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

#########################################################################################
#                           hashing functions
#########################################################################################
class Hashers():
    def hash_digest(self, string, algo):
        return hmac.new(SECRET, string, algo).hexdigest()

    def hash_str(self, string, algo):
        return "%s|%s"%( string, self.hash_digest(string, algo) )

    def check_hash_str(self, string, algo):
        value = string.split('|')[0]
        if string == self.hash_str(value, algo):
            return value

    def make_salt(self):
        return "".join(random.choice(string.letters) for x in xrange(10))

    def make_pw_hash(self, name, pw, salt=None):
        if not salt:
            salt = self.make_salt()
        return "%s|%s" % (salt, hashlib.sha256(name+pw+salt).hexdigest())
    
    def check_pw_hash(self, name, pw, pw_hash):
        salt = pw_hash.split('|')[0]
        return pw_hash == self.make_pw_hash(name, pw, salt)

