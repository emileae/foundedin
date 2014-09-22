from google.appengine.ext import ndb

class Startup(ndb.Model):
    q1 = ndb.StringProperty()
    q2 = ndb.StringProperty()
    q3 = ndb.StringProperty()
    q4 = ndb.StringProperty()
    q5 = ndb.StringProperty()
    q6 = ndb.StringProperty()
    new_logo = ndb.StringProperty()
    blob_key = ndb.BlobKeyProperty()
    approved = ndb.BooleanProperty(default=False)
    created = ndb.DateTimeProperty(auto_now_add=True)

class EarlyAdopter(ndb.Model):
    ea = ndb.StringProperty()
    removed = ndb.BooleanProperty(default=False)
    monthly = ndb.BooleanProperty(default=False)
    created = ndb.DateTimeProperty(auto_now_add=True)


    
    

    