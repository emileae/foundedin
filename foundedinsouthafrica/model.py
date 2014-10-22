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
    created = ndb.DateTimeProperty(auto_now_add=True)

    
    

    