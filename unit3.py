from google.appengine.ext import db

# custom imports
from handlers import Handler
from models import Art, Post

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
