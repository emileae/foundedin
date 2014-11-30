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

        if self.request.url.endswith('.json'):
            self.format = 'json'
        else:
            self.format = 'html'

#Global function
def tweet(status):
    tw = model.TwitterApi.query().get()
    if tw:
        try:
            CONSUMER_KEY = tw.tw_consumer_key
            CONSUMER_SECRET = tw.tw_consumer_secret
            
            ACCESS_TOKEN_KEY = tw.tw_access_token_key
            ACCESS_TOKEN_SECRET = tw.tw_access_token_secret

            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET)
            api = tweepy.API(auth)
            result = api.update_status(status)
        except Exception as ex:
            logging.error(ex)


# ===================================================================================================================================================
# ===================================================================================================================================================

#serves the homepage
class HomePage(MainHandler):
    def get(self):
        curs = Cursor(urlsafe=self.request.get('cursor'))
        year = datetime.datetime.now().year
        settings = model.Settings.query().get()
        mail = model.MandrillApi.query().get()
        tw = model.TwitterApi.query().get()
        #startups = model.Startup.query(model.Startup.approved == True).order(model.Startup.q1).fetch(500)

        startups, next_curs, more = model.Startup.query(model.Startup.approved == True).order(model.Startup.q1).fetch_page(500, start_cursor=curs)
        if more and next_curs:
            next_curs = next_curs.urlsafe()
        else:
            next_curs = False

        if not settings:
            self.response.out.write("If you are the admin for this page please navigate to /dashboard and complete the page setup")
        else:
            self.render("index.html", startups=startups, year=year, settings=settings, mail=mail, tw=tw, next_curs=next_curs)

class ViewLogos(MainHandler):
    def get(self):
        year = datetime.datetime.now().year
        settings = model.Settings.query().get()
        mail = model.MandrillApi.query().get()
        tw = model.TwitterApi.query().get()
        startups = model.Startup.query(model.Startup.approved == True).order(model.Startup.q1).fetch(500)

        self.render("admin.html", startups=startups, year=year, settings=settings, mail=mail, tw=tw)

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
            utils.send_notification_mail(q1)
        except:
            logging.error("no notification sent")
            pass

#serve the admin page
class Admin(MainHandler):
    def get(self):
        #year = datetime.datetime.now().year
        #settings = model.Settings.query().get()
        #mail = model.MandrillApi.query().get()
        #tw = model.TwitterApi.query().get()
        #startups = model.Startup.query().order(-model.Startup.q1).fetch(500)
        #self.render("admin.html", startups=startups, year=year)

        self.redirect("/dashboard")

# serve the about page
class About(MainHandler):
    def get(self):
        settings = model.Settings.query().get()
        mail = model.MandrillApi.query().get()
        tw = model.TwitterApi.query().get()
        year = datetime.datetime.now().year
        self.render("about.html", year=year, settings=settings, mail=mail, tw=tw)

class Dashboard(MainHandler):
    def get(self):
        settings = model.Settings.query().get()
        tw = model.TwitterApi.query().get()
        mail = model.MandrillApi.query().get()
        self.render("dashboard_general.html", settings=settings, tw=tw, mail=mail)

    def post(self):
        name = self.request.get("name")
        svg_html = self.request.get("svg_html")
        bg_color = self.request.get("bg_color")
        link_color = self.request.get("link_color")
        logo_highlight_color = self.request.get("logo_highlight_color")
        intro_html = self.request.get("intro_html")
        in_common_1 = self.request.get("in_common_1")
        in_common_2 = self.request.get("in_common_2")
        in_common_3 = self.request.get("in_common_3")
        follow_facebook = self.request.get("follow_facebook")
        follow_twitter = self.request.get("follow_twitter")
        follow_instagram = self.request.get("follow_instagram")
        follow_soundcloud = self.request.get("follow_soundcloud")
        site_credit = self.request.get("site_credit")
        site_credit_name = self.request.get("site_credit_name")
        logo_credit = self.request.get("logo_credit")
        logo_credit_name = self.request.get("logo_credit_name")
        about_html = self.request.get("about_html")
        seo_title = self.request.get("seo_title")
        seo_description = self.request.get("seo_description")
        seo_keywords = self.request.get("seo_keywords")
        share_url = self.request.get("share_url")
        css = self.request.get("css")

        tw_handle = self.request.get("tw_handle")
        tw_short_url = self.request.get("tw_short_url")
        tw_consumer_key = self.request.get("tw_consumer_key")
        tw_consumer_secret = self.request.get("tw_consumer_secret")
        tw_access_token_key = self.request.get("tw_access_token_key")
        tw_access_token_secret = self.request.get("tw_access_token_secret")

        mandrill_key = self.request.get("mandrill_key")
        reply_to = self.request.get("reply_to")
        subject_line = self.request.get("subject_line")
        from_email = self.request.get("from_email")
        from_name = self.request.get("from_name")
        notification_email = self.request.get("notification_email")

        settings = model.Settings.query().get()

        if not settings:

            settings = model.Settings(
                    seo_title=seo_title,
                    seo_description=seo_description,
                    seo_keywords=seo_keywords,
                    share_url=share_url,
                    name=name,
                    svg_html=svg_html,
                    bg_color=bg_color,
                    link_color=link_color,
                    logo_highlight_color=logo_highlight_color,
                    intro_html=intro_html,
                    in_common_1=in_common_1,
                    in_common_2=in_common_2,
                    in_common_3=in_common_3,
                    follow_facebook=follow_facebook,
                    follow_twitter=follow_twitter,
                    follow_instagram=follow_instagram,
                    follow_soundcloud=follow_soundcloud,
                    site_credit=site_credit,
                    site_credit_name=site_credit_name,
                    logo_credit=logo_credit,
                    logo_credit_name=logo_credit_name,
                    about_html=about_html,
                    css=css
                )
            settings.put()
        else:
            settings.seo_title=seo_title
            settings.seo_description=seo_description
            settings.seo_keywords=seo_keywords
            settings.share_url=share_url
            settings.name=name
            settings.svg_html=svg_html
            settings.bg_color=bg_color
            settings.link_color=link_color
            settings.logo_highlight_color=logo_highlight_color
            settings.intro_html=intro_html
            settings.in_common_1=in_common_1
            settings.in_common_2=in_common_2
            settings.in_common_3=in_common_3
            settings.follow_facebook=follow_facebook
            settings.follow_twitter=follow_twitter
            settings.follow_instagram=follow_instagram
            settings.follow_soundcloud=follow_soundcloud
            settings.site_credit=site_credit
            settings.site_credit=site_credit
            settings.site_credit_name=site_credit_name
            settings.logo_credit=logo_credit
            settings.logo_credit_name=logo_credit_name
            settings.about_html=about_html
            settings.css=css
            settings.put()

        tw = model.TwitterApi.query().get()
        if not tw:

            tw = model.TwitterApi(
                    tw_handle=tw_handle,
                    tw_short_url=tw_short_url,
                    tw_consumer_key=tw_consumer_key,
                    tw_consumer_secret=tw_consumer_secret,
                    tw_access_token_key=tw_access_token_key,
                    tw_access_token_secret=tw_access_token_secret,
                )
            tw.put()
        else:
            tw.tw_handle=tw_handle
            tw.tw_short_url=tw_short_url
            tw.tw_consumer_key=tw_consumer_key
            tw.tw_consumer_secret=tw_consumer_secret
            tw.tw_access_token_key=tw_access_token_key
            tw.tw_access_token_secret=tw_access_token_secret
            tw.put()

        mail = model.MandrillApi.query().get()
        if not mail:

            mail = model.MandrillApi(
                    mandrill_key=mandrill_key,
                    reply_to=reply_to,
                    subject_line=subject_line,
                    from_email=from_email,
                    from_name=from_name,
                    notification_email=notification_email
                )
            mail.put()
        else:
            mail.mandrill_key=mandrill_key
            mail.reply_to=reply_to
            mail.subject_line=subject_line
            mail.from_email=from_email
            mail.from_name=from_name
            mail.notification_email=notification_email
            mail.put()


        self.redirect('/dashboard')


class DashboardStartups(MainHandler):
    def get(self):
        startups = model.Startup.query().order(-model.Startup.q1).fetch(500)
        ea = model.EarlyAdopter.query().fetch(500)

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
        ea = model.EarlyAdopter.query().fetch(500)

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
        ea = model.EarlyAdopter.query().fetch(500)

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
        settings = model.Settings.query().get()
        mail = model.MandrillApi.query().get()
        tw = model.TwitterApi.query().get()

        existing_email = model.EarlyAdopter.query(model.EarlyAdopter.ea == ea).get()

        if not existing_email:
            ea = model.EarlyAdopter(ea = ea)
            ea.put()

            ea_id = ea.key.id()

            t = jinja_env.get_template("mailer.html")
            html = t.render(ea_id=ea_id, settings=settings, tw=tw, mail=mail)

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
        feature_id = self.request.get("feature_id")
        if len(startup_id) > 0:
            url = utils.request_blob_url(self, '/upload/%s' % startup_id, 1000000)
        elif len(feature_id) > 0:
            url = utils.request_blob_url(self, '/upload_feature/%s' % feature_id, 1000000)

        obj = {"url": url}
        self.render_json(obj)

#handler called after an image is uploaded to the blobstore
class Upload(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, startup_id):
        upload_files = self.get_uploads('new_logo')

        logging.error(upload_files)

        blob_info = upload_files[0]
        blob_key = blob_info.key()

        serving_url = utils.get_blob_serving_url(blob_key)
        
        startup = model.Startup.get_by_id(int(startup_id))
        tw = model.TwitterApi.query().get()

        #delete old blob
        if startup.blob_key:
            utils.delete_blob(startup.blob_key)

        startup.blob_key = blob_key
        startup.new_logo = serving_url
        startup.approved = True
        startup.put()


        year = datetime.datetime.now().year

        if startup.q4:
            if int(startup.q2) == year:
                status = "New #startup on %s: %s via %s" % ( tw.tw_short_url, startup.q4, tw.tw_handle )
                #status = "Check out the hot new SA #startup, %s, via @foundedinsa bit.ly/1ugm5eG" % startup.q4
            else:
                status = "Featured #startup on %s: %s via %s" % ( tw.tw_short_url, startup.q4, tw.tw_handle )
        else:
            if int(startup.q2) == year:
                status = "New #startup on %s: %s via %s" % ( tw.tw_short_url, startup.q4, tw.tw_handle )
            else:
                status = "Featured #startup on %s: %s via %s" % ( tw.tw_short_url, startup.q4, tw.tw_handle )

        try:
            tweet(status)
            #pass
        except tweepy.TweepError as e:
            logging.error(e.response.status)


        #status = "Checkout the hot new SA startup, %s" % startup.q4

        #tweet(serving_url, status)

        self.redirect("/dashboard/logo")

class UploadFeature(blobstore_handlers.BlobstoreUploadHandler):
    def post(self, feature_id):
        upload_files = self.get_uploads('new_logo')

        blob_info = upload_files[0]
        blob_key = blob_info.key()

        serving_url = utils.get_blob_serving_url(blob_key)
        
        feature = model.Feature.get_by_id(int(feature_id))
        
        #delete old blob
        if feature.blob_key:
            utils.delete_blob(feature.blob_key)

        feature.blob_key = blob_key
        feature.new_logo = serving_url
        feature.put()
        self.redirect('/dashboard/feature_edit/%s' % feature_id)


class TweetStartup(MainHandler):
    def get(self, startup_id):
        startup = model.Startup.get_by_id(int(startup_id))

        #serving_url = startup.new_logo
        #tweet(serving_url, status)

        #blob_reader = blobstore.BlobReader(startup.blob_key)
        #value = blob_reader.read()
        
        #logging.error("===================================")
        #logging.error(value)
        
        #blob_info = blobstore.BlobInfo.get(startup.blob_key)

        year = datetime.datetime.now().year
        if int(startup.q2) == year:
            status = "Checkout the hot new SA startup, %s, via @foundedinsa" % startup.q4
        else:
            status = "a Proudly South African startup, %s via @foundedinsa" % startup.q4
        
        tweet(status)

        self.redirect("/dashboard/logo")

# some unsubscribe functions
class Unsubscribe(MainHandler):
    def get(self):
        year = datetime.datetime.now().year
        ea_id = self.request.get("ea_id")

        settings = model.Settings.query().get()
        mail = model.MandrillApi.query().get()
        tw = model.TwitterApi.query().get()

        self.render("unsubscribe.html", year=year, ea_id=ea_id, settings=settings, mail=mail, tw=tw)

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

        settings = model.Settings.query().get()
        mail = model.MandrillApi.query().get()
        tw = model.TwitterApi.query().get()

        features = model.Feature.query( model.Feature.live == True ).order(-model.Feature.created).fetch()

        self.render("archive.html", features=features, settings=settings, mail=mail, tw=tw)

class Feature(MainHandler):
    def get(self, feature_id):

        settings = model.Settings.query().get()
        mail = model.MandrillApi.query().get()
        tw = model.TwitterApi.query().get()

        feature = model.Feature.get_by_id(int(feature_id))

        feature_website = feature.startup.get().q3[7:]

        self.render("feature.html", feature=feature, feature_website=feature_website, settings=settings, mail=mail, tw=tw)

class StartupsApi(MainHandler):
    def get(self):
        curs = Cursor(urlsafe=self.request.get('cursor'))
        settings = model.Settings.query().get()
        startups, next_curs, more = model.Startup.query().fetch_page(100, start_cursor=curs)

        if more and next_curs:
            next_curs = next_curs.urlsafe()
        else:
            next_curs = False

        obj = {}
        startup_list = []

        for s in startups:
            startup_obj = {}
            startup_obj["name"] = s.q1
            startup_obj["founded_year"] = s.q2
            startup_obj["website"] = s.q3
            startup_obj["twitter_handle"] = s.q4
            startup_list.append(startup_obj)

        user = {}
        user["name"] = settings.name
        user["bg_color"] = settings.bg_color
        user["twitter"] = settings.follow_twitter

        obj["startups"] = startup_list
        obj["next_page"] = next_curs
        obj["user"] = user

        self.render_json(obj)

class FeaturesApi(MainHandler):
    def get(self):
        curs = Cursor(urlsafe=self.request.get('cursor'))
        settings = model.Settings.query().get()
        features, next_curs, more = model.Feature.query().fetch_page(100, start_cursor=curs)

        if more and next_curs:
            next_curs = next_curs.urlsafe()
        else:
            next_curs = False

        obj = {}
        feature_list = []

        for f in features:
            feature_obj = {}
            feature_obj["startup"] = f.startup.get().q1
            feature_obj["description"] = f.description
            feature_obj["founder"] = f.founder
            feature_obj["twitter_handle"] = f.startup.get().q4
            feature_obj["new_logo"] = f.new_logo
            feature_list.append(feature_obj)

        user = {}
        user["name"] = settings.name
        user["bg_color"] = settings.bg_color
        user["twitter"] = settings.follow_twitter

        obj["features"] = feature_list
        obj["next_page"] = next_curs
        obj["user"] = user

        self.render_json(obj)


app = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/add_startup', AddStartup),
    ('/admin', Admin),
    ('/view_logos', ViewLogos),
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
    #('/dashboard2', Dashboard2),
    ('/dashboard/startup_emails', StartupEmails),
    ('/dashboard/earlyadopter_emails', EarlyAdopterEmails),
    ('/add_email', AddEmail),
    ('/add_ea', EarlyAdopter),
    ('/delete_startup', DeleteStartup),
    ('/get_upload_url', GetUploadUrl),
    ('/upload/(\w+)', Upload),
    ('/upload_feature/(\w+)', UploadFeature),
    ('/unsubscribe', Unsubscribe),
    ('/change_email', ChangeEmail),
    ('/change_email_early_adopter', ChangeMailEA),
    ('/reduce_mail_load', ReduceMailLoad),
    ('/remove_early_adopter', RemoveEarlyAdopter),
    ('/startups/?(?:\.json)?', StartupsApi),
    ('/features/?(?:\.json)?', FeaturesApi),
], debug=False)
