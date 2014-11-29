from google.appengine.ext import ndb

class Startup(ndb.Model):
    q1 = ndb.StringProperty()
    q2 = ndb.StringProperty()
    q3 = ndb.StringProperty()
    q4 = ndb.StringProperty()
    q5 = ndb.StringProperty()
    q6 = ndb.StringProperty()
    q7 = ndb.StringProperty()
    add_emails = ndb.StringProperty(repeated=True)
    new_logo = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty()
    approved = ndb.BooleanProperty(default=False)
    created = ndb.DateTimeProperty(auto_now_add=True)

class EarlyAdopter(ndb.Model):
    ea = ndb.StringProperty()
    startup = ndb.BooleanProperty(default=False)
    removed = ndb.BooleanProperty(default=False)
    monthly = ndb.BooleanProperty(default=False)
    created = ndb.DateTimeProperty(auto_now_add=True)

class Feature(ndb.Model):
    startup = ndb.KeyProperty(Startup)
    description = ndb.StringProperty()
    founder = ndb.JsonProperty(repeated=True)
    podcast = ndb.StringProperty()
    live = ndb.BooleanProperty(default=False)
    blob_key = ndb.BlobKeyProperty()
    new_logo = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)

class TwitterApi(ndb.Model):
    tw_handle = ndb.StringProperty()
    tw_short_url = ndb.StringProperty()
    tw_consumer_key = ndb.StringProperty()
    tw_consumer_secret = ndb.StringProperty()
    tw_access_token_key = ndb.StringProperty()
    tw_access_token_secret = ndb.StringProperty()

class MandrillApi(ndb.Model):
    mandrill_key = ndb.StringProperty()
    reply_to = ndb.StringProperty()
    subject_line = ndb.StringProperty()
    from_email = ndb.StringProperty()
    from_name = ndb.StringProperty()
    notification_email = ndb.StringProperty()

class Settings(ndb.Model):
    seo_title = ndb.StringProperty()
    seo_description = ndb.TextProperty()
    seo_keywords = ndb.StringProperty()
    share_url = ndb.StringProperty()
    name = ndb.StringProperty()
    svg_html = ndb.TextProperty()
    bg_color = ndb.StringProperty()
    link_color = ndb.StringProperty()
    logo_highlight_color = ndb.StringProperty()
    intro_html = ndb.TextProperty()
    in_common_1 = ndb.StringProperty()
    in_common_2 = ndb.StringProperty()
    in_common_3 = ndb.StringProperty()
    follow_facebook = ndb.StringProperty()
    follow_twitter = ndb.StringProperty()
    follow_instagram = ndb.StringProperty()
    follow_soundcloud = ndb.StringProperty()
    site_credit = ndb.StringProperty()
    site_credit_name = ndb.StringProperty()
    logo_credit = ndb.StringProperty()
    logo_credit_name = ndb.StringProperty()
    about_html = ndb.TextProperty()
    css = ndb.TextProperty()


























