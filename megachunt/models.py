#!/usr/bin/env python

"""
import pprint

from google.appengine.api import users
from google.appengine.ext import db

from megachunt.models import User

# Read from datastore using filter method...
# u = User.all().filter("user", users.get_current_user()).order("user").fetch(1)
# print u[0]

# Read from datastore using GQL...
# u = db.GqlQuery("SELECT * FROM User WHERE user = :1", users.get_current_user())
# for user in u:
  #   print user.user

# Insert a new user with email as key_name...
current_user = users.get_current_user()
current_user_email = current_user.email()
u = User.get_or_insert(current_user_email, user=current_user)
print u.key(), u.user

# Get user by key name (email)...
u = User.get_by_key_name(current_user_email)
print u.key(), u.user

# Documentation...
print User.get_by_key_name.__doc__
pprint.pprint(dir(User))
"""

from google.appengine.api import users
from google.appengine.ext import db

import utils

class User(db.Expando):
    user = db.UserProperty(required=True, indexed=True)
    access_token = db.TextProperty()
    refresh_token = db.TextProperty()
    instance_url = db.StringProperty()
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)
    
    @classmethod
    def get_current_user(cls):
        current_user = users.get_current_user()
        current_user_email = current_user.email()
        return cls.get_or_insert(current_user_email, user=current_user)
    
    @classmethod
    def create_logout_url(cls, path="/"):
        users.create_logout_url(path)
    
    def nickname(self):
        return self.user.nickname()
    
    def email(self):
        return self.user.email()
    
    def md5hash(self):
        return utils.md5hash(self.email())
    
    def __unicode__(self):
        return self.email()
    
    def __str__(self):
        return unicode(self).encode('utf-8')
    

class Chunt(db.Expando):
    user = db.UserProperty(required=True, indexed=True)
    content = db.TextProperty(required=True)
    created_At = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)

