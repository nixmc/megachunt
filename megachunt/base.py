#!/usr/bin/env python

"""
Overview
========

This script generates a CSV view of a specified user's Google Calendar, grouping events by Title and Hashtag.

Usage
=====

To run for Steve's calendar between Nov 11th and 18th 2011:

`$ ./caltags.py -u steve.winton@nixonmcinnes.co.uk -s 2011-11-14 -e 2011-11-18 > steve.csv`

To do
=====

* Report number of hours/minutes, as well as actual start and end times.
* Make it into a web app (using Flask + Google App Engine).
* Unleash it onto the unsuspecting masses.

"""

import csv
import getopt
import os
import re
import sys

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

import dateutil.parser

import gdata
import gdata.calendar.client

import settings

def mkclient(requestor_id='steve.winton@nixonmcinnes.co.uk'):
    """
    Makes a Google Calendar client for the given user (requestor_id).
    
    Since we have a Google Apps account, we can simplify the whole thing by
    using 2-legged OAuth (see: http://code.google.com/apis/accounts/docs/OAuth.html#GoogleAppsOAuth)
    """
    client = gdata.calendar.client.CalendarClient(source='nixonmcinnes-gtags-v1')
    client.auth_token = gdata.gauth.TwoLeggedOAuthHmacToken(
        settings.CONSUMER_KEY, settings.CONSUMER_SECRET, requestor_id
    )
    return client

def date_range_query(calendar_client, start_date, end_date):
    """
    Returns all events on a user's primary calendar between 2 given dates.
    
    Stolen from http://code.google.com/apis/calendar/data/2.0/developers_guide_python.html#RetrievingDateRange
    """
    # print 'Date range query for events on Primary Calendar: %s to %s' % (start_date, end_date,)
    query = gdata.calendar.client.CalendarEventQuery()
    query.start_min = start_date
    query.start_max = end_date
    feed = calendar_client.GetCalendarEventFeed(q=query)
    for i, an_event in enumerate(feed.entry):
        yield i, an_event

def hashtags(text):
    """
    Returns all the hashtags in the given text.
    """
    # The following regex supports complex hashtags with delimiters
    # capturing #foobar, $foobar, #foo-bar, #foo+bar, #foo:bar:baz etc.
    m = re.compile(r'([$#](?:\w+[-|:\+]*)+)', re.MULTILINE)
    for hashtag in m.findall(text):
        yield hashtag

def events_by_hashtag(requestor_id, start_date, end_date):
    """
    Emits hashtagged events on a user's calendar by title, hashtag, start time and end time. 
    """
    for i, ev in date_range_query(mkclient(requestor_id=requestor_id), start_date=start_date, end_date=end_date):
        if not ev.title.text and not ev.content.text:
            continue
        title = ev.title.text if ev.title.text else ""
        description = ev.content.text if ev.content.text else ""
        for hashtag in hashtags(" ".join((title, description))):            
            for when in ev.when:
                yield (title, hashtag, dateutil.parser.parse(when.start), dateutil.parser.parse(when.end))

def usage():
    """
    Prints out basic usage instructions
    """
    sys.stderr.write("%s -u <user> -s <start-date> -e <end-date>\n" % (sys.argv[0],))

if __name__ == "__main__":
    try:
        opts, args = getopt.getopt(sys.argv[1:], "u:s:e:", ["user=", "start=", "end="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    user = start = end = None
    for o, a in opts:
        if o in ("-u", "--user"):
            user = a
        elif o in ("-s", "--start"):
            start = a
        elif o in ("-e", "--end"):
            end = a
        
    user = user if user else "steve.winton@nixonmcinnes.co.uk"
    start = start if start else "2011-11-14"
    end = end if end else "2011-11-18"
    
    sys.stderr.write("User: %s, start: %s, end: %s\n" % (user, start, end))
    
    writer = csv.writer(sys.stdout)
    writer.writerow(("Title", "Hashtag", "Start", "End",))
    for row in events_by_hashtag(requestor_id=user, start_date=start, end_date=end):
        writer.writerow(row)
