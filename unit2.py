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
            user = User.by_name(username)
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
            user = User.register(username, password, email)
            user.put()
            self.set_secure_cookie('user_id', str(user.key().id()) )
            self.redirect("/unit2/welcome")

class SignupSuccessHandler(Handler, Validators, Hashers):
    def get(self):
        if self.user:
            self.render("welcome.html", username=self.user.username)
        else:
            self.redirect("/unit2/signup")

class LoginHandler(Handler, Validators, Hashers):
    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        user = User.login(username, password)
        if user:
            self.login(user)
            self.redirect("/unit2/welcome")
        else:
            error = "username and password doesn't match"
            self.render('login.html', username=username, error=error)

class LogoutHandler(Handler):
    def get(self):
        self.logout()
        self.redirect('/unit2/signup')
