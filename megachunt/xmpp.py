import logging

from google.appengine.api import xmpp
from google.appengine.ext import webapp

from chatter import Chatter, ChatterAuth

import settings
from models import *

class IncomingXMPPHandler(webapp.RequestHandler):
    def post(self):
        message = xmpp.Message(self.request.POST)
        
        chunt = message.body

        sender = message.sender.split("/")
        user, _ = User.get_by_key_name(sender)

        # logging.info("New XMPP message received from %s to %s", (str(dir(message)), message.to))
        # logging.debug(str(dir(message)))
        # logging.debug(message.sender)
        logging.info("Chunting from %s: %s" % (user.email(), chunt))

        auth = ChatterAuth(settings.CHATTER_CONSUMER_KEY, settings.CHATTER_CONSUMER_SECRET)
        chatter = Chatter(auth=auth, instance_url=user.instance_url, access_token=user.access_token, 
                          refresh_token=user.refresh_token, 
                          access_token_refreshed_callback=user.update_access_token)
        chatter.feeds.news.me.feed_items(_method="POST", text=chunt)

        message.reply("OK! :)")

app = webapp.WSGIApplication([('/_ah/xmpp/message/chat/', IncomingXMPPHandler)],
                             debug=True)

