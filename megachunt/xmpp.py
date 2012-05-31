import logging

from google.appengine.api import xmpp
from google.appengine.ext import webapp

from django.utils.html import strip_tags

from chatter import Chatter, ChatterAuth

import settings
from models import *

class IncomingXMPPHandler(webapp.RequestHandler):
    def post(self):
        # TODO: tidy this mess up!
        message = xmpp.Message(self.request.POST)
        
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

app = webapp.WSGIApplication([('/_ah/xmpp/message/chat/', IncomingXMPPHandler)],
                             debug=True)

