# Standard library imports
import datetime
import logging

# Flask imports
from flask import Flask, abort, jsonify, make_response, redirect, render_template, request
from werkzeug.contrib.cache import GAEMemcachedCache
cache = GAEMemcachedCache()

# App Engine imports
from google.appengine.api import memcache
# from google.appengine.api.urlfetch import fetch

# Other non-standard lib imports
try:
    import json
except ImportError:
    import simplejson as json

import urllib3

# Application imports
from flaskapp import app
from models import *
import settings
import utils

@app.route('/')
def index():
    user = User.get_current_user()
    user_nickname = user.nickname()
    user_email = user.email()
    user_hash = user.md5hash()
    logout_url = User.create_logout_url("/")
    
    logging.info('Visited by user %s', repr((user_email, user_nickname)))
    
    return render_template('index.html', 
        user=user, user_nickname=user_nickname, user_email=user_email, 
        user_hash=user_hash, logout_url=logout_url)

@app.route('/authenticate')
def authenticate():
    """
    Direct the client's web browser to the page 
    https://login.instance_name/services/oauth2/authorize, with the following 
    request parameters:
    
        response_type   Must be code for this authentication flow
        client_id       The Consumer Key value from the remote access application defined for this application
        redirect_uri    The Callback URL value from the remote access application defined for this application
    """
    return redirect(utils.chatter_authorize_url())

@app.route('/authenticate/_callback')
def authenticate_callback():
    """
    Once Salesforce has confirmed that the client application is authorized, 
    the end-user’s web browser is redirected to the callback URL specified by 
    the redirect_uri parameter, appended with the following values in its 
    query string:
    
        code:   The authorization code that is passed to get the access and refresh tokens.
        state:  The state value that was passed in as part of the initial request, if applicable.
    
    The client application server must extract the authorization code and pass
    it in a request to Salesforce for an access token. This request should be 
    made as a POST against this URL: 
    https://login.instance_name/services/oauth2/token with the following query 
    parameters:
    
        grant_type:     Value must be authorization_code for this flow.
        client_id:      Consumer key from the remote access application definition.
        client_secret:  Consumer secret from the remote access application definition.
        redirect_uri:   URI to redirect the user to after approval. This must match the value in the Callback URL field in the remote access application definition exactly, and is the same value sent by the initial redirect.
        code:           Authorization code obtained from the callback after approval.
        format:         Expected return format. This parameter is optional. The default is json. Values are:
        
            * urlencoded
            * json
            * xml
    """
    response = make_response(request.args.get("code"))
    response.headers["Content-Type"] = "text/plain"
    
    return response

@app.route('/api/1/lookup/<user>')
def lookup(user="me"):
    """
    Lookup details about the specified user.
    """
    current_user = User.get_current_user()
    current_user_email = current_user.email()
    
    try:
        user_settings = settings.USERS[current_user_email]
        access_token = user_settings["access_token"]
        instance_url = user_settings["instance_url"]
    except:
        abort(404)
    
    http = urllib3.PoolManager()
    resource = "%s/services/data/v24.0/chatter/users/%s/" % (instance_url, user)
    headers = dict(Authorization="OAuth %s" % access_token)
    r = http.request("GET", resource, headers=headers)
    
    # Return JSON response
    response = make_response(r.data)
    response.headers["Content-Type"] = "application/json"
    
    return response
