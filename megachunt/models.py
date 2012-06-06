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

import logging
import random

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
    
    def update_access_token(self, access_token):
        logging.info("Updating access token for %s to %s" % (str(self), access_token))
        
        self.access_token = access_token

        return self.put()

    def __unicode__(self):
        return self.email()
    
    def __str__(self):
        return unicode(self).encode('utf-8')
    

class CommonWordMethods():
    @classmethod
    def get_random_word(cls):
        word = cls.gql("""WHERE rand > :rand 
                          ORDER BY rand 
                          LIMIT 1""", 
                          rand=random.random()).get()
        
        logging.info("Returning random word, '%s'", (word))
        return word
    

class Adjective(db.Model, CommonWordMethods):
    word = db.StringProperty(required=True)
    slug = db.StringProperty(required=True)
    length = db.IntegerProperty(required=True, indexed=True)
    rand = db.FloatProperty(required=True, indexed=True)    
    
    def __unicode__(self):
        return self.word
    
    def __str__(self):
        return unicode(self).encode('utf-8')
    

class Noun(db.Model, CommonWordMethods):
    word = db.StringProperty(required=True)
    slug = db.StringProperty(required=True)
    length = db.IntegerProperty(required=True, indexed=True)
    rand = db.FloatProperty(required=True, indexed=True)
    
    def __unicode__(self):
        return self.word
    
    def __str__(self):
        return unicode(self).encode('utf-8')
    

class EmailHandle(db.Model):
    """
    Unique email handle identifying a user.
    """
    
    handle = db.StringProperty(required=True, indexed=True)
    created_at = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)
    
    @classmethod
    def create_handle_for_user(cls, user):
        hdl = cls.generate_unique_handle()
        row = cls(parent=user, key_name=hdl, handle=hdl)
        row.put()
        
        return hdl
    
    @classmethod
    def generate_unique_handle(cls):
        while True:
            adjective = Adjective.get_random_word()
            noun = Noun.get_random_word()
            
            hdl = "-".join((str(adjective), str(noun), str(random.randint(100, 999))))
            
            if cls.all().filter("handle", hdl).get() != None:
                # Handle is not unique, try again...
                continue
                
            return hdl
    
    @classmethod
    def get_handle_for_user(cls, user):
        hdl = cls.all().ancestor(user).order("-created_at").get()
        
        return hdl.handle if hdl else None
    
    @classmethod
    def get_user_from_handle(cls, hdl):
        hdl = cls.all().filter("handle", hdl).get()
        # hdl = cls.get_by_key_name(hdl)
        
        return hdl.parent() if hdl else None
    

class Chunt(db.Expando):
    # Don't have user as a property, instead have the user as the parent
    # E.g. chunt = Chunt(parent=user, ...)
    # See: https://developers.google.com/appengine/docs/python/datastore/entities#Ancestor_Paths
    # user = db.UserProperty(required=True, indexed=True)
    content = db.TextProperty(required=True)
    created_At = db.DateTimeProperty(auto_now_add=True)
    updated_at = db.DateTimeProperty(auto_now=True)

