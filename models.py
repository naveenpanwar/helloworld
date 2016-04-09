from google.appengine.ext import db

# custom imports
import handlers
from hashes import Hashers


#########################################################################################
#                           Database Classes
#########################################################################################
class Art(db.Model):
    title = db.StringProperty(required=True)
    art = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add = True)

class Post(db.Model):
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.content.replace("\n","<br>")
        return handlers.render_str("post.html", p=self)

class User(db.Model):
    created = db.DateTimeProperty(auto_now_add = True)
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.EmailProperty()

    @classmethod
    def by_id(cls, user_id):
        return User.get_by_id(user_id)

    @classmethod
    def by_name(cls, name):
        u = User.all().filter("username = ", name).get()
        return u
    @classmethod
    def register(cls, name, pw, email = None):
        pw_hash = Hashers.make_pw_hash(name, pw)
        u = User( username = name, password = pw_hash)
        if email:
            u.email = email
        return u

    @classmethod
    def login(cls, name, pw):
        u = cls.by_name(name)
        return Hashers.check_pw_hash( name, pw, u.password) and u
