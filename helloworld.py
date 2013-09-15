#                       Global Declarations
#------------------------------------------------------------------------
#------------------------------------------------------------------------

import webapp2
import jinja2
import os
import re

from google.appengine.ext import db

temp_dir = os.path.join(os.path.dirname(__file__), 'templates')

j_e = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(temp_dir))

#this method checks if username is valid or not
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

#this method checks if password matches or not
PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

#this method checks for valid email
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")
def valid_email(email):
    return not email or EMAIL_RE.match(email)


params = {'e_username':'', 'e_password':'', 'e_verify':'',
          'e_email':''}

#                 Handlers
#-----------------------------------------------------------------------
#-----------------------------------------------------------------------

#****************  BaseHandler  ****************************************

# function renders the given templates with the 0 or more key-value pairs
def renderer(template, **params):
    ret_temp = j_e.get_template(template)
    return ret_temp.render(params)

class Basehandler(webapp2.RequestHandler):
    def render(self, template, **kwargs):
        self.response.out.write(renderer(template, **kwargs))

#********************** Signup Handler *********************************

class Signup(Basehandler):
    def get(self):
        self.render('signup.html')

    def post(self):
        have_error = False
        username = self.request.get('username') 
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        if not valid_username(username):
            params['e_username']="That's not a valid username"
            have_error = True
        if not valid_password(password):
            params['e_password']="That's not a valid password"
            have_error = True
        elif password != verify:
            params['e_verify']="Your password didn't match"
            have_error = True
        if not valid_email(email):
            params['e_email']="That's not a valid email"
            have_error = True

        if have_error:
            self.render('signup.html',**params)
        else:
            self.redirect('/welcome?username=%s' % username)

class Welcome(Basehandler):
    def get(self):
        username = self.request.get('username')
        self.render('welcome.html',username = username)

#********************** DataBase Manager ****************************
class Posts(db.Model):
    title = db.StringProperty(required = True)
    post = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

#********************** Blog Class ***********************************
class Blog(Basehandler):
    def get(self):
        self.render("blog.html")


#********************* New Post Class ********************************
class NewPost(Basehandler):
    def grender(self, title="",error="",post=""):
        self.render('newpost.html',error=error, title=title, post=post)

    def get(self):
        self.grender()

    def post(Basehandler):
        title = self.request.get('title')
        post = self.request.get('post')

        if title and post:
            np = Posts(title = title, post = post)
            current = np.put()
            self.redirect("/blog/%s" %current.id())
        else:
            error = "Please submit all given fields before submitting"
            self.grender(title, post, error)

#******************** Permalink Class ********************************
class Permalink(Basehandler):
    def get(self):
        posted = db.GqlQuery("SELECT * FROM Posts")
        title = posted.title
        post = posted.post




#                  URL Handlers
#----------------------------------------------------------------------
#----------------------------------------------------------------------

app = webapp2.WSGIApplication([('/signup',Signup)
                              ,('/welcome',Welcome)
                              ,('/blog',Blog)
                              ,('/blog/newpost',NewPost)
                              ,('/blog/(\d+)',Permalink)
                               ],debug=True)
