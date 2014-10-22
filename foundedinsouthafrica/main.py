#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import webapp2
import jinja2
import logging
import os

import json
from datetime import datetime, timedelta
import datetime
import time

import urllib
import urllib2
from urlparse import urlparse

from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.datastore.datastore_query import Cursor

import model
import utils

import tweepy
import requests
import calendar
import ConfigParser
import HTMLParser
#from tweepy import *

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class MainHandler(webapp2.RequestHandler):
#TEMPLATE FUNCTIONS    
    def write(self, *a, **kw):
        self.response.headers['Host'] = 'localhost'
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(*a, **kw)
        
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)
        
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    #JSON rendering
    def render_json(self, obj):
        self.response.headers['Content-Type'] = 'application/json'
        self.response.headers['Host'] = 'localhost'
        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.response.out.write(json.dumps(obj))

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)

#Global function
def tweet(status):
    CONSUMER_KEY = utils.CONSUMER_KEY
    CONSUMER_SECRET = utils.CONSUMER_SECRET
    
    ACCESS_TOKEN_KEY = utils.ACCESS_TOKEN_KEY
    ACCESS_TOKEN_SECRET = utils.ACCESS_TOKEN_SECRET

    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    result = api.update_status(status)


# ===================================================================================================================================================
# ===================================================================================================================================================

#serves the homepage
class HomePage(MainHandler):
    def get(self):
        year = datetime.datetime.now().year
        startups = model.Startup.query(model.Startup.approved == True).order(model.Startup.q1).fetch(100)
        self.render("index.html", startups=startups, year=year)

# add a startup... completed by prospective startups
class AddStartup(MainHandler):
    def post(self):
        q1 = self.request.get("q1")
        q2 = self.request.get("q2")
        q3 = self.request.get("q3")
        q4 = self.request.get("q4")
        q5 = self.request.get("q5")
        q6 = self.request.get("q6")
        q7 = self.request.get("q7")

        q1 = q1.capitalize()

        o = urlparse(q3)
        if 'http' not in o.scheme:
            q3 = "http://%s" % q3 

        su = model.Startup(q1=q1, q2=q2, q3=q3, q4=q4, q5=q5, q6=q6, q7=q7)
        su.put()

        try:
            #included emails in utils.py file...
            utils.send_notification_mail(utils.notification_email1, utils.notification_email1, utils.notification_email1, q1)
        except:
            pass

#serve the admin page
class Admin(MainHandler):
    def get(self):
        year = datetime.datetime.now().year
        startups = model.Startup.query().order(-model.Startup.q1).fetch(500)
        self.render("admin.html", startups=startups, year=year)

# serve the about page
class About(MainHandler):
    def get(self):
        year = datetime.datetime.now().year
        self.render("about.html", year=year)

class Dashboard(MainHandler):
    def get(self):
        startups = model.Startup.query().order(-model.Startup.q1).fetch(500)
        ea = model.EarlyAdopter.query().fetch(100)

        self.render("dashboard_base.html", startups=startups, ea=ea)

class DashboardStartups(MainHandler):
    def get(self):
        startups = model.Startup.query().order(-model.Startup.q1).fetch(500)
        ea = model.EarlyAdopter.query().fetch(100)

        self.render("dashboard_startups.html", startups=startups, ea=ea)

class DashboardLogo(MainHandler):
    def get(self):
        startups = model.Startup.query().order(-model.Startup.q1).fetch(500)
        self.render("dashboard_logo.html", startups=startups)

class DashboardFeaturedArticles(MainHandler):
    def get(self):
        articles = model.Feature.query().fetch()
        startups = model.Startup.query().order(-model.Startup.q1).fetch(500)

        self.render("dashboard_articles.html", articles=articles, startups=startups)

class DashboardFeature(MainHandler):
    def get(self):
        startups = model.Startup.query().order(-model.Startup.q1).fetch(500)
        ea = model.EarlyAdopter.query().fetch(100)

        self.render("dashboard_feature.html", startups=startups, ea=ea)

    def post(self):
        description = self.request.get("description")
        founder = self.request.get_all("founder")
        podcast = self.request.get("podcast")
        startup_id = self.request.get("startup_id")
        startup = model.Startup.get_by_id(int(startup_id))

        founder_list = []

        for f in founder:
            #f = f.replace(" ", "")
            f = f.strip()
            f = f.split(",")
            if len(f) == 2:
                obj = {
                    "founder": f[0],
                    "twitter": f[1].replace(" ", ""),
                    "twitter_url": "https://twitter.com/%s" % f[1][1:],
                }
            else:
                obj = {
                    "founder": f[0],
                    "twitter": "",
                    "twitter_url": "",
                }
            founder_list.append(obj)

        f = model.Feature(description=description, founder=founder_list, podcast=podcast, startup=startup.key)
        f.put()
        self.redirect("/dashboard/featured_articles")

class DashboardFeatureEdit(MainHandler):
    def get(self, feature_id):

        startups = model.Startup.query().order(-model.Startup.q1).fetch(500)
        feature = model.Feature.get_by_id(int(feature_id))

        self.render("edit_feature.html", feature=feature, startups=startups)

    def post(self, feature_id):
        description = self.request.get("description")
        founder = self.request.get_all("founder")
        podcast = self.request.get("podcast")
        startup_id = self.request.get("startup_id")
        startup = model.Startup.get_by_id(int(startup_id))

        feature_id = feature_id

        founder_list = []

        for f in founder:
            f = f.strip()
            #f = f.lstrip()#leading strip
            f = f.split(",")
            if len(f) == 2:
                obj = {
                    "founder": f[0],
                    "twitter": f[1].replace(" ", ""),
                    "twitter_url": "https://twitter.com/%s" % f[1][1:],
                }
            else:
                obj = {
                    "founder": f[0],
                    "twitter": "",
                    "twitter_url": "",
                }
            founder_list.append(obj)

        feature = model.Feature.get_by_id(int(feature_id))
        feature.description = description
        feature.founder = founder_list
        feature.podcast = podcast
        feature.startup = startup.key

        feature.put()
        self.redirect("/dashboard/featured_articles")

class FeatureGoLive(MainHandler):
    def post(self, feature_id):

        feature = model.Feature.get_by_id(int(feature_id))

        feature.live = True
        feature.put()

        obj = {
            "message": "ok",
            "id": feature_id
        }

        self.render_json(obj)

class FeatureDeactivate(MainHandler):
    def post(self, feature_id):

        feature = model.Feature.get_by_id(int(feature_id))

        feature.live = False
        feature.put()

        obj = {
            "message": "ok",
            "id": feature_id
        }

        self.render_json(obj)

class Dashboard2(MainHandler):
    def get(self):
        startups = model.Startup.query().order(-model.Startup.q1).fetch(500)
        ea = model.EarlyAdopter.query().fetch(100)

        self.render("dashboard2.html", startups=startups, ea=ea)

class AddEmail(MainHandler):
    def post(self):
        email = self.request.get('email')
        sid = self.request.get('sid')
        other_mails = self.request.get('other_mails')

        website = self.request.get('website')
        twitter_handle = self.request.get('twitter_handle')
        contact_person = self.request.get('contact_person')

        if other_mails:
            other_mails = other_mails.replace(" ", "")
            other_mails = other_mails.split(",")

        startup = model.Startup.get_by_id(int(sid))

        if website:
            startup.q3 = website
        if twitter_handle:
            startup.q4 = twitter_handle
        if contact_person:
            startup.q6 = contact_person
        if other_mails:
            startup.add_emails = other_mails
        if email:
            startup.q7 = email

        startup.put()

        message = "ok"

        self.render_json({"message": message})

class StartupEmails(MainHandler):
    def get(self):
        curs = Cursor(urlsafe=self.request.get('cursor'))
        startups, next_curs, more = model.Startup.query().fetch_page(1000, start_cursor=curs)
        if more and next_curs:
            next_curs = next_curs.urlsafe()
        else:
            next_curs = False

        self.render("startup_mails.html", startups=startups, next_curs=next_curs)

class EarlyAdopterEmails(MainHandler):
    def get(self):
        curs = Cursor(urlsafe=self.request.get('cursor'))
        eas, next_curs, more = model.EarlyAdopter.query().fetch_page(1000, start_cursor=curs)
        if more and next_curs:
            next_curs = next_curs.urlsafe()
        else:
            next_curs = False

        self.render("earlyadopter_emails.html", eas=eas, next_curs=next_curs)

# add an early adopter
class EarlyAdopter(MainHandler):
    def post(self):
        ea = self.request.get("ea")

        existing_email = model.EarlyAdopter.query(model.EarlyAdopter.ea == ea).get()

        if not existing_email:
            ea = model.EarlyAdopter(ea = ea)
            ea.put()

            ea_id = ea.key.id()

            t = jinja_env.get_template("mailer.html")
            html = t.render(ea_id=ea_id)

            utils.send_mail(ea.ea, ea_id, html)

# remove a startup in /admin
class DeleteStartup(MainHandler):
    def post(self):
        su_id = self.request.get("id")

        startup = model.Startup.get_by_id(int(su_id))

        if startup.blob_key:
            utils.delete_blob(startup.blob_key)#deletes serving url and blob of an image blob

        startup.key.delete()

#get an upload url, used in ajax call when submitting the image upload form in /admin
class GetUploadUrl(MainHandler):
    def get(self):
        startup_id = self.request.get("startup_id")
        url = utils.request_blob_url(self, '/upload/%s' % startup_id, 1000000)
        obj = {"url": url}
        self.render_json(obj)

#handler called after an image is uploaded to the blobstore
class Upload(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, startup_id):
        upload_files = self.get_uploads('new_logo')

        blob_info = upload_files[0]
        blob_key = blob_info.key()

        serving_url = utils.get_blob_serving_url(blob_key)
        
        startup = model.Startup.get_by_id(int(startup_id))
        startup.blob_key = blob_key
        startup.new_logo = serving_url
        startup.approved = True
        startup.put()


        year = datetime.datetime.now().year

        if startup.q4:
            if int(startup.q2) == year:
                status = "%s %s via @foundedinsa" % ( utilstweet_message_1, startup.q4 )
                #status = "Check out the hot new SA #startup, %s, via @foundedinsa bit.ly/1ugm5eG" % startup.q4
            else:
                status = "%s %s via @foundedinsa" % ( utilstweet_message_2, startup.q4 )
        else:
            if int(startup.q2) == year:
                status = "%s %s via @foundedinsa" % ( utilstweet_message_1, startup.q1 )
            else:
                status = "%s %s via @foundedinsa" % ( utilstweet_message_2, startup.q1 )

        try:
            tweet(status)
        except tweepy.TweepError as e:
            logging.error(e.response.status)

        self.redirect("/admin")

class TweetStartup(MainHandler):
    def get(self, startup_id):
        startup = model.Startup.get_by_id(int(startup_id))

        year = datetime.datetime.now().year
        if int(startup.q2) == year:
            status = "%s %s, via @foundedinsa" % ( utilstweet_message_1, startup.q4 )
        else:
            status = "%s %s via @foundedinsa" % ( utilstweet_message_2, startup.q4 )
        
        tweet(status)

        self.redirect("/admin")

# some unsubscribe functions
class Unsubscribe(MainHandler):
    def get(self):
        year = datetime.datetime.now().year
        ea_id = self.request.get("ea_id")

        self.render("unsubscribe.html", year=year, ea_id=ea_id)

class RemoveEarlyAdopter(MainHandler):
    def get(self):
        ea_id = self.request.get("ea_id")

        ea = model.EarlyAdopter.get_by_id(int(ea_id))
        ea.removed = True
        ea.put()

        obj = {
            "removed": "yes"
        }
        self.render_json(obj)


class ChangeEmail(MainHandler):
    def get(self):
        year = datetime.datetime.now().year
        ea_id = self.request.get("ea_id")

        self.render("change_email.html", year=year, ea_id=ea_id)

class ChangeMailEA(MainHandler):
    def post(self):
        ea_id = self.request.get("ea_id")
        ea_new = self.request.get("ea_new")

        ea = model.EarlyAdopter.get_by_id(int(ea_id))

        ea.ea = ea_new
        ea.put()

        obj = {
            "changed": "yes"
        }
        self.render_json(obj)

class ReduceMailLoad(MainHandler):
    def get(self):
        ea_id = self.request.get("ea_id")
        ea = model.EarlyAdopter.get_by_id(int(ea_id))
        ea.monthly = True
        ea.put()

        obj = {
            "reduced": "yes"
        }
        self.render_json(obj)

class Archive(MainHandler):
    def get(self):

        features = model.Feature.query( model.Feature.live == True ).order(-model.Feature.created).fetch()

        self.render("archive.html", features=features)

class Feature(MainHandler):
    def get(self, feature_id):

        feature = model.Feature.get_by_id(int(feature_id))

        self.render("feature.html", feature=feature)

app = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/add_startup', AddStartup),
    ('/admin', Admin),
    ('/archive', Archive),
    #('/tweet/(\w+)', TweetStartup),
    ('/about', About),
    ('/dashboard', Dashboard),
    ('/dashboard/startups', DashboardStartups),
    ('/dashboard/logo', DashboardLogo),
    ('/dashboard/feature', DashboardFeature),
    ('/dashboard/feature_edit/(\w+)', DashboardFeatureEdit),
    ('/dashboard/featured_articles', DashboardFeaturedArticles),
    ('/feature_golive/(\w+)', FeatureGoLive),
    ('/feature_deactivate/(\w+)', FeatureDeactivate),
    ('/feature/(\w+)', Feature),
    ('/dashboard2', Dashboard2),
    ('/dashboard/startup_emails', StartupEmails),
    ('/dashboard/earlyadopter_emails', EarlyAdopterEmails),
    ('/add_email', AddEmail),
    ('/add_ea', EarlyAdopter),
    ('/delete_startup', DeleteStartup),
    ('/get_upload_url', GetUploadUrl),
    ('/upload/(\w+)', Upload),
    ('/unsubscribe', Unsubscribe),
    ('/change_email', ChangeEmail),
    ('/change_email_early_adopter', ChangeMailEA),
    ('/reduce_mail_load', ReduceMailLoad),
    ('/remove_early_adopter', RemoveEarlyAdopter),
], debug=False)
