import logging

from email.utils import parseaddr

from google.appengine.api import xmpp
from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler 

from django.utils.html import strip_tags

from chatter import Chatter, ChatterAuth

import settings
from models import *

class IncomingMailHandler(InboundMailHandler):
    """
    Handles all incoming mail.
    """
    def receive(self, message):
        # TODO: Support multiple recipients
        # Extract the recipient details from message.to
        recipient_label, recipient_addr = parseaddr(message.to)

        # Extract the 'chunt' from the first plain text body
        plaintext_bodies = [body.decode() for content_type, body in message.bodies("text/plain")]
        chunt = plaintext_bodies[0]
        
        # Log the sender and message body...
        logging.info("Received message from %s to %s: %s" % (message.sender, message.to, chunt))
        
        # Get the handle
        handle = recipient_addr.split("@")[0]
        
        # Get the user
        user = EmailHandle.get_user_from_handle(handle)
        
        # Chunt!
        logging.info("Chunting from %s: %s" % (user, chunt))
        auth = ChatterAuth(settings.CHATTER_CONSUMER_KEY, settings.CHATTER_CONSUMER_SECRET)
        chatter = Chatter(auth=auth, instance_url=user.instance_url, access_token=user.access_token, 
                          refresh_token=user.refresh_token, 
                          access_token_refreshed_callback=user.update_access_token)
        chatter.feeds.news.me.feed_items.post(text=chunt)

        # TODO: Save the Chunt

emailapp = webapp.WSGIApplication([IncomingMailHandler.mapping()], debug=True)

class IncomingXMPPHandler(webapp.RequestHandler):
    def post(self):
        # TODO: tidy this mess up!
        message = xmpp.Message(self.request.POST)
        
        # TODO: handle @-mentions in message.body
        # e.g. @[Steve Winton] becomes {@005E0000000Fpox} (I think!)
        # text: {@005E0000000Fpox}
        # text: howdy, {@005E0000000Fpox}

        chunt = strip_tags(message.body)

        sender = message.sender.split("/")
        user, _ = User.get_by_key_name(sender)

        if not user:
            # Send a link to the authentication page
            return message.reply(
                """<html xmlns='http://jabber.org/protocol/xhtml-im'>
                    <body xmlns='http://www.w3.org/1999/xhtml'>
                    <p>Sorry, I don't know who you are... Please try <a href='%s'>authenticating</a> first.</p> 
                    </body>
                   </html>""" % settings.CHATTER_AUTHENTICATE_URL, raw_xml=True)

        logging.info("Chunting from %s: %s" % (user.email(), chunt))

        auth = ChatterAuth(settings.CHATTER_CONSUMER_KEY, settings.CHATTER_CONSUMER_SECRET)
        chatter = Chatter(auth=auth, instance_url=user.instance_url, access_token=user.access_token, 
                          refresh_token=user.refresh_token, 
                          access_token_refreshed_callback=user.update_access_token)
        status, chunt = chatter.feeds.news.me.feed_items.post(text=chunt)
        logging.info("Got chunt: %s" % str(chunt))

        if "id" in chunt:
            # Success!
            # TODO: Save the Chunt

            # Send a response
            chunt_url = user.instance_url.rstrip("/") + "/" + chunt["id"]
            logging.info("Chunt url: " + chunt_url)
            message.reply(
                """<html xmlns='http://jabber.org/protocol/xhtml-im'>
                    <body xmlns='http://www.w3.org/1999/xhtml'>
                    <p><a href='%s'>Got it</a>! :)</p>
                    </body>
                   </html>""" % chunt_url, raw_xml=True)
        else:
            # Something went wrong?
            message.reply("OH NOES :(")

xmppapp = webapp.WSGIApplication([('/_ah/xmpp/message/chat/', IncomingXMPPHandler)],
                                 debug=True)

