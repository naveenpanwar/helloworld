import webapp2
import cgi
import re
import jinja2
import os

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
        return username and USER_RE.match(username)

    PASS_RE = re.compile(r"^.{3,20}$")
    def valid_password(self, password):
        return password and PASS_RE.match(password)

    EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
    def valid_email(self, email):
        return not email or EMAIL_RE.match(email)

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
