#!/usr/bin/env python

import logging, email

from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app

from chatter import Chatter, ChatterAuth

import settings
from models import *

class IncomingMailHandler(InboundMailHandler):
    """
    Handles all incoming mail.
    """
    def receive(self, message):
        # Extract the 'chunt' from the first plain text body
        plaintext_bodies = [body.decode() for content_type, body in message.bodies("text/plain")]
        chunt = plaintext_bodies[0]
        
        # Log the sender and message body...
        logging.info("Received message from %s to %s: %s" % (message.sender, message.to, chunt))
        
        # Get the handle
        handle = message.to.split("@")[0]
        
        # Get the user
        user = EmailHandle.get_user_from_handle(handle)
        
        # Chunt!
        logging.info("Chunting from %s: %s" % (user, chunt))
        auth = ChatterAuth(settings.CHATTER_CONSUMER_KEY, settings.CHATTER_CONSUMER_SECRET)
        chatter = Chatter(auth=auth, instance_url=user.instance_url, access_token=user.access_token, 
                          refresh_token=user.refresh_token, 
                          access_token_refreshed_callback=user.update_access_token)
        feed_items = getattr(chatter.feeds.news.me, "feed-items")
        feed_items(_method="POST", text=chunt)

        # TODO: Save the Chunt

app = webapp.WSGIApplication([IncomingMailHandler.mapping()], debug=True)
