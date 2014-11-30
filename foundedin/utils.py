
import re
import hashlib
import hmac
import random
import string
from string import letters
import logging
import urllib2
import json

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import images
from google.appengine.api import urlfetch
from google.appengine.api import mail

from urlparse import urlparse
try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs
    urlparse.parse_qs = parse_qs

import model
        
# for uploading a processed, white logo to the blobstore
def request_blob_url(self, callback_url, max_bytes):
    upload_url = blobstore.create_upload_url(callback_url, max_bytes)
    return upload_url
#get a serving url, so that your app doesnt have to use unnecessary bandwidth serving images
def get_blob_serving_url(blob_key):
    serving_url = images.get_serving_url(blob_key)
    return serving_url
#deleting a blob
def delete_blob(blob_key):
    images.delete_serving_url(blob_key)#delete serving url
    blb = blobstore.BlobInfo.get(blob_key)#delete blob info which deletes blob
    if blb:
        blb.delete()#delete blob info which deletes blob
#keep track of your iamge when it goes to the blobstore
def save_blob_to_image_obj(blob_key, user_obj, img_type):
    if user_obj:
        user_key = user_obj.key
        serving_url = images.get_serving_url(blob_key)
        
        img = model.Image( user=user_key, serving_url=serving_url, blob_key=blob_key, img_type=img_type )
        img.put()
        
        return serving_url

#Send a mail to your early evangelists
def send_mail(email, ea_id, html):
    
    mail = model.MandrillApi.query().get()
    if mail:

        url = "https://mandrillapp.com/api/1.0/messages/send.json"

        #modify text to suite your startup, also see the mailer.html template and adapt for a sweet html mailer
        form_json = {
            "key": mail.mandrill_key,
            "message": {
                "html": html,
                "text": mail.subject_line,
                "subject": mail.subject_line,
                "from_email": mail.from_email,
                "from_name": mail.from_name,
                "to": [
                    {
                        "email": email,
                        "name": "New user",
                        "type": "to"
                    }
                ],
                "headers": {
                    "Reply-To": mail.reply_to
                },
                "important": False,
                "track_opens": None,
                "track_clicks": None,
                "auto_text": None,
                "auto_html": None,
                "inline_css": None,
                "url_strip_qs": None,
                "preserve_recipients": None,
                "view_content_link": None,
                "bcc_address": None,
                "tracking_domain": None,
                "signing_domain": None,
                "return_path_domain": None,
                "merge": True,
                "global_merge_vars": [
                    {
                        "name": "merge1",
                        "content": "merge1 content"
                    }
                ],
                "merge_vars": [
                    {
                        "rcpt": "recipient.email@example.com",
                        "vars": [
                            {
                                "name": "merge2",
                                "content": "merge2 content"
                            }
                        ]
                    }
                ],
                "tags": [
                    "password-resets"
                ],
                "subaccount": None,
                "google_analytics_domains": [
                    None
                ],
                "google_analytics_campaign": None,
                "metadata": {
                    "website": None
                },
                "recipient_metadata": None,
                "attachments": None,
                "images": None
            },
            "async": False,
            "ip_pool": "Main Pool",
            "send_at": None
        }
    

    result = urlfetch.fetch(url=url, payload=json.dumps(form_json), method=urlfetch.POST)#, #headers={'Content-Type': 'application/x-www-form-urlencoded'})


#Send a mail to your early evangelists
def send_notification_mail(name):
    
    url = "https://mandrillapp.com/api/1.0/messages/send.json"

    html = "<p>A new startup has been added: <u>%s</u></p>" % name

    mail = model.MandrillApi.query().get()


    if mail:
        #modify text to suite your startup, also see the mailer.html template and adapt for a sweet html mailer
        form_json = {
            "key": mail.mandrill_key,
            "message": {
                "html": html,
                "text": "New Startup",
                "subject": "Foundedinx  - New Startup",
                "from_email": mail.from_email,
                "from_name": mail.from_name,
                "to": [
                    {
                        "email": mail.notification_email,
                        "name": "admin",
                        "type": "to"
                    },
                ],
                "headers": {
                    "Reply-To": mail.reply_to
                },
                "important": False,
                "track_opens": None,
                "track_clicks": None,
                "auto_text": None,
                "auto_html": None,
                "inline_css": None,
                "url_strip_qs": None,
                "preserve_recipients": None,
                "view_content_link": None,
                "bcc_address": None,
                "tracking_domain": None,
                "signing_domain": None,
                "return_path_domain": None,
                "merge": True,
                "global_merge_vars": [
                    {
                        "name": "merge1",
                        "content": "merge1 content"
                    }
                ],
                "merge_vars": [
                    {
                        "rcpt": "recipient.email@example.com",
                        "vars": [
                            {
                                "name": "merge2",
                                "content": "merge2 content"
                            }
                        ]
                    }
                ],
                "tags": [
                    "password-resets"
                ],
                "subaccount": None,
                "google_analytics_domains": [
                    None
                ],
                "google_analytics_campaign": None,
                "metadata": {
                    "website": None
                },
                "recipient_metadata": None,
                "attachments": None,
                "images": None
            },
            "async": False,
            "ip_pool": "Main Pool",
            "send_at": None
        }
    

    result = urlfetch.fetch(url=url, payload=json.dumps(form_json), method=urlfetch.POST)
    
    
    
    
    
    
    
    