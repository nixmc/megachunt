#!/usr/bin/env python

try:
    import json
except ImportError:
    import simplejson as json

import re

import sys

from urllib import quote

import urllib3

from chatter_globals import POST_ACTIONS     

class ChatterAuth(object):
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret


class ChatterCall(object):
    def __init__(self, auth, instance_url, access_token, callable_cls, uriparts, refresh_token=None, access_token_refreshed_callback=None):
        self.auth = auth
        self.instance_url = unicode(instance_url)
        self.access_token = unicode(access_token)
        self.callable_cls = callable_cls
        self.uriparts = uriparts
        self.refresh_token = unicode(refresh_token)
        self.access_token_refreshed_callback = access_token_refreshed_callback

    def __getattr__(self, k):
        try:
            return object.__getattr__(self, k)
        except AttributeError:
            def extend_call(arg):
                return self.callable_cls(
                    auth=self.auth, instance_url=self.instance_url, access_token=self.access_token, 
                    callable_cls=self.callable_cls, uriparts=self.uriparts + (arg,),
                    refresh_token=self.refresh_token, 
                    access_token_refreshed_callback=self.access_token_refreshed_callback)
            if k == "_":
                return extend_call
            else:
                return extend_call(k)

    def __call__(self, **kwargs):
        # Build the uri.
        uriparts = []
        for uripart in self.uriparts:
            # If this part matches a keyword argument, use the
            # supplied value otherwise, just use the part.
            uriparts.append(str(kwargs.pop(uripart, uripart)))
        uri = '/'.join(uriparts)

        method = kwargs.pop('_method', None)
        if not method:
            method = "GET"
            for action in POST_ACTIONS:
                if re.search("%s(/\d+)?$" % action, uri):
                    method = "POST"
                    break

        # If an id kwarg is present and there is no id to fill in in
        # the list of uriparts, assume the id goes at the end.
        id = kwargs.pop('id', None)
        if id:
            uri += "/%s" %(id)

        resource = self.instance_url.rstrip('/') + '/' + uri

        return self._handle_response(method, resource, fields=kwargs)

    def _refresh_access_token(self):
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

        resource = "https://na1.salesforce.com/services/oauth2/token"
        fields = dict(grant_type="refresh_token", refresh_token=self.refresh_token,
                      client_id=self.auth.client_id, client_secret=self.auth.client_secret,
                      format="json")
        status, data = self._handle_response("POST", resource, fields=fields, refresh_access_token=False)
        
        if 'access_token' in data:
            # Update access token
            self.access_token = data['access_token']
            
            # Notify others via callback
            if callable(self.access_token_refreshed_callback):
                self.access_token_refreshed_callback(self.access_token)
            
            # Return True, indicating access_token refresehed
            return True

        # Return False, indicating access_token not refreshed
        return False

    def _handle_response(self, method, resource, fields, headers=None, refresh_access_token=True, max_retries=2):
        http = urllib3.PoolManager()
        
        headers = headers or dict()

        retries = 1
        invalid_session_id = True
        while invalid_session_id and retries <= max_retries:
            # Need to always overwrite the Authorization header in case the access token has been
            # refreshed
            headers["Authorization"] = "OAuth %s" % self.access_token

            r = http.request(method, resource, headers=headers, fields=fields)
            data = json.loads(r.data)

            # Does the access token need to be refreshed? I.e. is the session ID invalid?
            invalid_session_id = len([
                item for item in data 
                    if 'errorCode' in item and item['errorCode'] == 'INVALID_SESSION_ID']) > 0
            
            if invalid_session_id and refresh_access_token and retries < max_retries:
                self._refresh_access_token()

            retries += 1

        return r.status, data

class Chatter(ChatterCall):
    def __init__(self, auth, instance_url, access_token, refresh_token=None, 
                 version="v24.0", access_token_refreshed_callback=None):

        uriparts = ("services", "data", version, "chatter")

        ChatterCall.__init__(
            self, auth=auth, instance_url=instance_url, access_token=access_token, 
            callable_cls=ChatterCall, refresh_token=refresh_token, uriparts=uriparts, 
            access_token_refreshed_callback=access_token_refreshed_callback)

