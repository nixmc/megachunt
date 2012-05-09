# Standard library imports
import datetime
import logging

# Flask imports
from flask import Flask, abort, jsonify, make_response, redirect, render_template, request
from werkzeug.contrib.cache import GAEMemcachedCache
cache = GAEMemcachedCache()

# App Engine imports
from google.appengine.api import memcache, users
# from google.appengine.api.urlfetch import fetch

# Other non-standard lib imports
try:
    import json
except ImportError:
    import simplejson as json

# Application imports
from flaskapp import app
import settings
import utils

@app.route('/')
def index():
    user = users.get_current_user()
    user_nickname = user.nickname()
    user_email = user.email()
    user_hash = utils.md5hash(user_email)
    logout_url = users.create_logout_url("/")
    
    logging.info('Visited by user %s', repr((user_email, user_nickname)))
    
    return render_template('index.html', 
        user=user, user_nickname=user_nickname, user_email=user_email, user_hash=user_hash, logout_url=logout_url)
