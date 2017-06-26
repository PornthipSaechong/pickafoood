import webapp2
from login import Login, Chatter, CreateMenu
import logging


config = {
  'webapp2_extras.auth': {
    'user_model': 'models.User',
    'user_attributes': ['name']
  },
  'webapp2_extras.sessions': {
    'secret_key': 'YOUR_SECRET_KEY'
  }
}


app = webapp2.WSGIApplication([
  (r'/?$', Chatter),
  (r'/create?$', CreateMenu),



], debug=True, config = config)