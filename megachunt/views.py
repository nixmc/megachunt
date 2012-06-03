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
from google.appengine.api import users

# Other non-standard lib imports
try:
    import json
except ImportError:
    import simplejson as json

import urllib3

# Application imports
from flaskapp import app
from decorators import *
from models import *
import settings
import utils

@app.route('/')
def index():
    user = User.get_current_user()
    user_nickname = user.nickname()
    user_email = user.email()
    user_hash = user.md5hash()
    logout_url = users.create_logout_url("/")
    
    handle = EmailHandle.get_handle_for_user(user)
    
    logging.info('Visited by user %s', repr((user_email, user_nickname)))
    
    return render_template('index.html', 
        user=user, user_nickname=user_nickname, user_email=user_email, 
        user_hash=user_hash, logout_url=logout_url, handle=handle)

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
    the end-user's web browser is redirected to the callback URL specified by 
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
    # Ensure we have an authorization code
    code = request.args.get("code", None)
    if not code:
        abort(400)
    
    # Lookup the access code
    status, access = utils.get_access_token(code)
    
    if not (status == 200 and "error" not in access):
        # Error
        abort(500)
    
    # Save the details
    user = User.get_current_user()
    user.access_token = access.get("access_token", "")
    user.refresh_token = access.get("refresh_token", "")
    user.instance_url = access.get("instance_url", "")
    user.save()
    
    # Create email handle
    handle = EmailHandle.create_handle_for_user(user)
    
    # Redirect
    return redirect("/?handle_created")
