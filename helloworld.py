import webapp2
import cgi
import re
import jinja2
import os
from google.appengine.ext import db

# custom imports
import handlers
from handlers import Handler
from models import Art, Post

###################################################################################################
#                         Request Handlers
###################################################################################################

class MainPage(Handler):
    def write_form(self, error="", month="", day="", year=""):
        self.render( 'form.html', error=error, month=month, day=day, year=year )

    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        self.write_form()

    def post(self):
        user_month = self.request.get('month')
        user_day = self.request.get('day')
        user_year = self.request.get('year')

        month = handlers.val_month(user_month)
        day = handlers.val_day(user_day)
        year = handlers.val_year(user_year)

        if not ( day and month and year ):
            return self.write_form("Something Went Wrong", 
                                    escape_html(user_month),
                                    escape_html(user_day),
                                    escape_html(user_year),
                                    )
        else:
            self.redirect("/thanks")

class ThanksHandler(Handler):
    def get(self):
        self.write("Thanks, that's a totally a valid day")


###############################################################################
#                        Unit 2
###############################################################################

class Rot13Handler(Handler):
    def get(self):
        return self.render( 'rot13form.html', message="" )

    def post(self):
        smalla = ord('a')
        smallz = ord('z')
        capA = ord('A')
        capZ = ord('Z')
        user_message = self.request.get('text')
        rotted = ""

        for l in user_message:
            lord = ord(l)
            rotord = lord + 13
            small_thresh = rotord - smallz
            cap_thresh = rotord - capZ
            if lord >= smalla and lord <= smallz or lord >= capA and lord <= capZ:
                if rotord > smallz:
                    rotted+=chr(smalla + small_thresh -1 )
                elif rotord > capZ and lord < capZ:
                    rotted+=chr(capA + cap_thresh -1)
                else:
                    rotted+=chr(rotord)
            else:
                rotted+=l
        return self.render( 'rot13form.html', message=escape_html(rotted) )

class SignupHandler(Handler):
    def write_form(self, 
                   username = "",
                   username_error = "", 
                   password_error = "", 
                   verify_error = "", 
                   email = "",
                   email_error = "", 
                   ):
        self.render( 'signup_form.html', 
                username= username, 
                username_error= username_error, 
                password_error= password_error, 
                verify_error= verify_error, 
                email= email, 
                email_error= email_error, 
                )

    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        self.write_form()

    def post(self):
        status = True

        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        if not handlers.valid_username(username):
            status = False
            username_error = "Username is invalid"
        else:
            username_error = ""

        if not handlers.valid_password(password):
            status = False
            password_error = "Password is invalid"
            verify_error = ""
        elif verify != password:
            verify_error = "Passwords does not match"
            password_error = ""
            status = False
        else:
            password_error = ""
            verify_error = ""

        if not handlers.valid_email(email):
            status = False
            email_error = "Email is invalid"
        else:
            email_error = ""

        if not status:
            return self.write_form( escape_html(username), 
                                    escape_html(username_error),
                                    escape_html(password_error),
                                    escape_html(verify_error),
                                    escape_html(email),
                                    escape_html(email_error),
                                    )
        else:
            self.redirect("/unit2/welcome?username=" + username)

class SignupSuccessHandler(Handler):
    def get(self):
        username = self.request.get('username')
        if handlers.valid_username(username):
            self.write("Welcome! "+username+ "! ")
        else:
            self.redirect("/unit2/signup")

###############################################################################
#                        Unit 3
###############################################################################
class AsciiChanHandler(Handler):
    def render_ascii(self, title="", art="", error=""):
        arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC")
        self.render('asciichan.html', title=title, art=art, error=error, arts=arts)

    def get(self):
        self.render_ascii()

    def post(self):
        title = self.request.get('title')
        art = self.request.get('art')

        if title and art:
            a = Art( title=title, art=art )
            a.put()
            self.redirect('/unit3')
        else:
            error = "we need both title and art"
            self.render_ascii(title, art, error )

class BlogHandler(Handler):
    def get(self):
        posts = Post.all().order('-created').run(limit=10)
        self.render('blog_front.html', posts = posts )

class PostHandler(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id))
        post = db.get(key)

        if not post:
            self.error(404)
            return
        self.render('post_permalink.html', post=post)

class NewPostHandler(Handler):
    def render_new_post(self, subject="", content="", error=""):
        self.render('new_blog_post.html', subject=subject, content=content, error=error )

    def get(self):
        self.render_new_post()

    def post(self):
        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post( subject=subject, content=content )
            p.put()
            self.redirect( '/unit3/blog/%s' % str(p.key().id()) )
        else:
            error = "we need both subject and content"
            self.render_new_post(subject, content, error )
