from google.appengine.ext import db

# custom imports
from handlers import Handler
from models import Art, Post

###############################################################################
#                        Unit 3
###############################################################################
class AsciiChanHandler(Handler):
    def render_ascii(self, title="", art="", error=""):
        arts = db.GqlQuery("SELECT * FROM Art ORDER BY created DESC LIMIT 10")
        
        #prevent from running database query multiple times
        arts = list(arts)
        
        # generate a list of points
        points = filter(None, (a.coords for a in arts))

        #generate an image url
        img_url = None
        if points:
            img_url = self.gmaps_img(points)

        self.render('asciichan.html', title=title, art=art, error=error, arts=arts, img_url=img_url )

    def get(self):
        self.render_ascii()

    def post(self):
        title = self.request.get('title')
        art = self.request.get('art')

        if title and art:
            a = Art( title=title, art=art )
            # lookup coordinates from import
            # if they have coordinates add them to the mapping
            # to get the ip self.request.remote_addr
            geopt = self.get_coords('4.2.2.2')
            if geopt:
                a.coords = geopt
            a.put()
            self.redirect('/unit3')
        else:
            error = "we need both title and art"
            self.render_ascii(title, art, error )

class BlogHandler(Handler):
    def get(self):
        posts = Post.all().order('-created').run(limit=10)
        if self.format == 'html':
            self.render('blog_front.html', posts = posts )
        else:
            self.render_json([p.as_dict() for p in posts])

class PostHandler(Handler):
    def get(self, post_id):
        post = Post.get_by_id( int(post_id))
        
        if not post:
            self.error(404)
            return

        if self.format == 'html':
            self.render('post_permalink.html', post=post)
        else:
            self.render_json(post.as_dict())

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
            self.redirect( '/blog/%s' % str(p.key().id()) )
        else:
            error = "we need both subject and content"
            self.render_new_post(subject, content, error )
