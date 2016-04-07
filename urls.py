import webapp2
import helloworld

###############################################################################
# url handlers
###############################################################################

app = webapp2.WSGIApplication([
    ('/', helloworld.MainPage),
    ('/thanks', helloworld.ThanksHandler),
    ('/unit2/rot13', helloworld.Rot13Handler),
    ('/unit2/signup', helloworld.SignupHandler),
    ('/unit2/welcome', helloworld.SignupSuccessHandler),
    ('/unit3', helloworld.AsciiChanHandler),
    ('/unit3/blog', helloworld.BlogHandler),
    ('/unit3/blog/([0-9]+)', helloworld.PostHandler),
    ('/unit3/blog/newpost', helloworld.NewPostHandler),
], debug=True)
