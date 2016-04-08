# custom imports
from handlers import Validators, Handler, Hashers
from models import User
from google.appengine.ext import db
import hashlib

###############################################################################
#                        Unit 2
###############################################################################

class Rot13Handler(Handler, Validators):
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
        return self.render( 'rot13form.html', message=self.escape_html(rotted) )

class SignupHandler(Handler, Validators, Hashers):
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

        if not self.valid_username(username):
            status = False
            username_error = "Username is invalid"
        else:
            user = User.all().filter('username =',username).get()
            if user:
                status = False
                username_error = "Username already exists"
            else:
                username_error = ""

        if not self.valid_password(password):
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

        if not self.valid_email(email):
            status = False
            email_error = "Email is invalid"
        else:
            email_error = ""

        if not status:
            return self.write_form( self.escape_html(username), 
                                    self.escape_html(username_error),
                                    self.escape_html(password_error),
                                    self.escape_html(verify_error),
                                    self.escape_html(email),
                                    self.escape_html(email_error),
                                    )
        else:
            pw_hash = self.make_pw_hash(username, password)
            user = User( username = username, password = pw_hash)
            if email:
                user.email = email
            user.put()
            user_id = str(user.key().id())

            self.response.headers['Content-Type'] = 'text/plain'
            new_cookie_val = self.hash_str( user_id, hashlib.sha256 )
            self.response.headers.add_header( 'Set-Cookie','user_id=%s;Path=/' % new_cookie_val )
            self.redirect("/unit2/welcome")

class SignupSuccessHandler(Handler, Validators, Hashers):
    def get(self):
        cookie_str = self.request.cookies.get('user_id')
        if cookie_str:
            cookie_val = self.check_hash_str(cookie_str, hashlib.sha256 )
            if cookie_val and cookie_val.isdigit():
                user = User.get_by_id(int(cookie_val))
                self.render("welcome.html", username=user.username)
            else:
                self.redirect("/unit2/signup")
        else:
            self.redirect("/unit2/signup")

class LoginHandler(Handler, Validators, Hashers):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        user = User.all().filter("username = ", username).get()
        if user:
            if self.check_pw_hash(username, password, user.password):
                self.response.headers['Content-Type'] = 'text/plain'
                new_cookie_val = self.hash_str( str(user.key().id()), hashlib.sha256 )
                self.response.headers.add_header( 'Set-Cookie','user_id=%s;Path=/' % new_cookie_val )
                self.redirect("/unit2/welcome")
            else:
                error = "username and password doesn't match"
                self.render('login.html', username=username, error=error)
        else:
            error = "user does not exist"
            self.render('login.html', username=username, error=error)

class LogoutHandler(Handler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.headers.add_header('Set-Cookie', "user_id='';Path=/")
        self.redirect('/unit2/signup')
