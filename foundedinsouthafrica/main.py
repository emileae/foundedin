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

from urlparse import urlparse

from google.appengine.ext import ndb
from google.appengine.api import images
from google.appengine.api import memcache
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.datastore.datastore_query import Cursor

import model
import utils

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

        o = urlparse(q3)
        if 'http' not in o.scheme:
            q3 = "http://%s" % q3 

        su = model.Startup(q1=q1, q2=q2, q3=q3, q4=q4, q5=q5, q6=q6)
        su.put()

#serve the admin page
class Admin(MainHandler):
    def get(self):
        year = datetime.datetime.now().year
        startups = model.Startup.query().order(-model.Startup.q1).fetch(100)
        self.render("admin.html", startups=startups, year=year)

# serve the about page
class About(MainHandler):
    def get(self):
        year = datetime.datetime.now().year
        self.render("about.html", year=year)

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

app = webapp2.WSGIApplication([
    ('/', HomePage),
    ('/add_startup', AddStartup),
    ('/admin', Admin),
    ('/about', About),
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
