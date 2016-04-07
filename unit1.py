# custom imports
from handlers import Validators
from handlers import Handler

###################################################################################################
#                         Unit 1
###################################################################################################

class MainPage(Handler, Validators):
    def write_form(self, error="", month="", day="", year=""):
        self.render( 'form.html', error=error, month=month, day=day, year=year )

    def get(self):
        #self.response.headers['Content-Type'] = 'text/plain'
        self.write_form()

    def post(self):
        user_month = self.request.get('month')
        user_day = self.request.get('day')
        user_year = self.request.get('year')

        month = self.val_month(user_month)
        day = self.val_day(user_day)
        year = self.val_year(user_year)

        if not ( day and month and year ):
            return self.write_form("Something Went Wrong", 
                                    self.escape_html(user_month),
                                    self.escape_html(user_day),
                                    self.escape_html(user_year),
                                    )
        else:
            self.redirect("/thanks")

class ThanksHandler(Handler):
    def get(self):
        self.write("Thanks, that's a totally a valid day")
