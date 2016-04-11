import webapp2
import unit1
import unit2
import unit3
import unit4
import unit5

###############################################################################
# url handlers
###############################################################################

app = webapp2.WSGIApplication([
    ('/', unit1.MainPage),
    ('/thanks', unit1.ThanksHandler),
    ('/rot13', unit2.Rot13Handler),
    ('/blog/signup', unit2.SignupHandler),
    ('/blog/login', unit2.LoginHandler),
    ('/blog/logout', unit2.LogoutHandler),
    ('/blog/welcome', unit2.SignupSuccessHandler),
    ('/unit3', unit3.AsciiChanHandler),
    ('/blog/?(?:.json)?', unit3.BlogHandler),
    ('/blog/([0-9]+)(?:.json)?', unit3.PostHandler),
    ('/blog/newpost', unit3.NewPostHandler),
    ('/unit4', unit4.CookieHandler),
    ('/unit5', unit5.APIHandler),
], debug=True)
