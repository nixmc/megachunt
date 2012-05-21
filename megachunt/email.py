#!/usr/bin/env python

import logging, email

from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app

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
        
        # TODO: Chunt
        # (Send the chunt, refresh token, if necessary, then save the chunt)
    

app = webapp.WSGIApplication([IncomingMailHandler.mapping()], debug=True)
