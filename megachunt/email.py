#!/usr/bin/env python

import logging, email

from google.appengine.ext import webapp 
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 
from google.appengine.ext.webapp.util import run_wsgi_app

class IncomingMailHandler(InboundMailHandler):
    """
    Handles all incoming mail.
    """
    def receive(self, message):
        plaintext_bodies = message.bodies('text/plain')
        
        # Log the sender and message body...
        logging.info("Received message from %s: %s" % (message.sender, message.bodies('text/plain')))
        
        # Send a response...
        # TODO...
    

app = webapp.WSGIApplication([IncomingMailHandler.mapping()], debug=True)
# run_wsgi_app(application)