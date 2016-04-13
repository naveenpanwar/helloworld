from google.appengine.ext import db
import time
from google.appengine.api import memcache

# custom imports
from handlers import Handler
from models import Art, Post

###############################################################################
#                        Unit 3
###############################################################################
class AsciiChanHandler(Handler):
    def render_ascii(self, title="", art="", error=""):
        arts = self.top_arts()
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
            self.top_arts(True)
            self.redirect('/unit3')
        else:
            error = "we need both title and art"
            self.render_ascii(title, art, error )

class BlogHandler(Handler):
    def get(self):
        posts, time_ago = self.top_posts()
        if self.format == 'html':
            self.render('blog_front.html', posts = posts, time_ago = self.age_str(time_ago) )
        else:
            self.render_json([p.as_dict() for p in posts])

class PostHandler(Handler):
    def get(self, post_id):
        post_key = post_id
        post, query_time = self.age_get( post_key )
        
        if not post:
            key = db.Key.from_path('Post', int(post_id))
            post = db.get(key)
            self.age_set(post_key, post)
            query_time = 0
        
        if not post:
            self.error(404)
            return

        if self.format == 'html':
            self.render( 'post_permalink.html', post=post, query_time=self.age_str(query_time) )
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
            p_id = self.add_post(p)
            self.redirect( '/blog/%s' % p_id )
        else:
            error = "we need both subject and content"
            self.render_new_post(subject, content, error )
