#!/usr/bin/env python

import hashlib
import sys

try:
    import json
except ImportError:
    import simplejson as json

from urllib import quote

import urllib3

try:
    import settings
except ImportError:
    if __name__ == "__main__":
        sys.path.append("..")
        import settings

def md5hash(s):
    """
    Generates an MD5 hash from s
    """
    hash = hashlib.md5(s)
    return hash.hexdigest()

def chatter_authorize_url(login_instance="na1.salesforce.com"):
    """
    Returns an appropriate URL to authorize the app using your Chatter account.
    
        response_type   Must be code for this authentication flow
        client_id       The Consumer Key value from the remote access application defined for this application
        redirect_uri    The Callback URL value from the remote access application defined for this application
    
    """
    return "https://%s/services/oauth2/authorize?response_type=code&client_id=%s&redirect_uri=%s" % (
        login_instance,
        quote(settings.CHATTER_CONSUMER_KEY),
        quote(settings.CHATTER_CALLBACK_URL),
    )

def get_access_token(code):
    """
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
    
    e.g.
    
        $ curl -i --form grant_type=authorization_code \
            --form client_id=<client_id> \
            --form client_secret=<client_secret> \
            --form redirect_uri=https://megachunt.appspot.com/authenticate/_callback \
            --form code=<code> \
            --form format=json \
             https://na1.salesforce.com/services/oauth2/token
    """
    http = urllib3.PoolManager()
    resource = "https://na1.salesforce.com/services/oauth2/token"
    fields = dict(grant_type="authorization_code", client_id=settings.CHATTER_CONSUMER_KEY,
                  client_secret=settings.CHATTER_CONSUMER_SECRET, 
                  redirect_uri=settings.CHATTER_CALLBACK_URL, code=code, 
                  format="json")
    r = http.request("POST", resource, fields=fields)
    
    return r.status, json.loads(r.data)

def refresh_access_token(refresh_token):
    """
    If the client application has a refresh token, it can use it to send a request for a new access token. 
    
    To ask for a new access token, the client application should send a POST request to https://login.instance_name/services/oauth2/token with the following query parameters:
    
        grant_type:     Value must be refresh_token for this flow.
        refresh_token:  The refresh token the client application already received. 
        client_id:      Consumer key from the remote access application definition.
        client_secret:  Consumer secret from the remote access application definition.
        format:         Expected return format. This parameter is optional. The default is json. Values are:
    
            * urlencoded
            * json
            * xml
    
    e.g.
    
        $ curl -i --form grant_type=refresh_token \
            --form refresh_token=<refresh_token> \
            --form client_id=<client_id> \
            --form client_secret=<client_secret> \
            --form format=json \
            https://na1.salesforce.com/services/oauth2/token
    """
    http = urllib3.PoolManager()
    resource = "https://na1.salesforce.com/services/oauth2/token"
    fields = dict(grant_type="refresh_token", refresh_token=refresh_token,
                  client_id=settings.CHATTER_CONSUMER_KEY,
                  client_secret=settings.CHATTER_CONSUMER_SECRET, 
                  format="json")
    r = http.request("POST", resource, fields=fields)
    
    return r.status, json.loads(r.data)

if __name__ == "__main__":
    print get_access_token(sys.argv[1])
