import md5

from urllib import quote

import settings

def md5hash(s):
    """
    Generates an MD5 hash from s
    """
    hash = md5.md5(s)
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
