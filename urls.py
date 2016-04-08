import webapp2
import unit1
import unit2
import unit3
import unit4

###############################################################################
# url handlers
###############################################################################

app = webapp2.WSGIApplication([
    ('/', unit1.MainPage),
    ('/thanks', unit1.ThanksHandler),
    ('/unit2/rot13', unit2.Rot13Handler),
    ('/unit2/signup', unit2.SignupHandler),
    ('/unit2/login', unit2.LoginHandler),
    ('/unit2/welcome', unit2.SignupSuccessHandler),
    ('/unit3', unit3.AsciiChanHandler),
    ('/unit3/blog', unit3.BlogHandler),
    ('/unit3/blog/([0-9]+)', unit3.PostHandler),
    ('/unit3/blog/newpost', unit3.NewPostHandler),
    ('/unit4', unit4.CookieHandler),
], debug=True)
