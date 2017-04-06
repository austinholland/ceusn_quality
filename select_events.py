""" select_events.py

Get CEUS earthquakes for analysis.  The goal is to get a good geographical mix so that could
end up being a bit of a challenge.
Currently I am going to try an algorithm that creates a distance measure that is a 
combination of distance in degrees (r) and magnitude (m) so that our distance is
dist=np.sqrt(r**2+(m2-m1)**2)
We can then apply a cutoff for distance.  For now I will try a distance greater than 1.0.  
The idea is to get a large sampling of event magnitudes and different locations.  I am 
afraid this will still produce a lot of events in Oklahoma.

db.events.count({"description":/.*Oklahoma.*/})

Data is stored in a local mongo database in order to allow for changes in data structure 
as this develops.

"""

import pymongo
from bson.objectid import ObjectId
from obspy.core import *
import obspy.clients.fdsn as fdsn
import obspy.geodetics as geodetics
import numpy as np
import shapely.geometry
import logging
from utils import *
 
class Event(dict):
  """
  Map a dictionary to be able to use keys like attributes and then you can even add 
  functionality.  There could be some gotchas here I haven't thought about.  
  """
  def __init__(self, *args, **kwargs):
      super(Event, self).__init__(*args, **kwargs)
      for arg in args:
          if isinstance(arg, dict):
              for k, v in arg.items():
                  self[k] = v

      if kwargs:
          for k, v in kwargs.iteritems():
              self[k] = v

  def __getattr__(self, attr):
      return self.get(attr)

  def __setattr__(self, key, value):
      self.__setitem__(key, value)

  def __setitem__(self, key, value):
      super(Event, self).__setitem__(key, value)
      self.__dict__.update({key: value})

  def __delattr__(self, item):
      self.__delitem__(item)

  def __delitem__(self, key):
      super(Event, self).__delitem__(key)
      del self.__dict__[key]
      
def magdistance(event,lat,lon,mag):
  r=geodetics.locations2degrees(event.latitude,event.longitude,lat,lon)
  dm=event.magnitude-mag    
  return np.sqrt(r**2+dm**2)
 
def process_catalog(db,mdist=1.0):
  """ Calculate the minimum magnitude_distance metric for each event """
  events=db.events
  eventsCEUS=db.eventCEUS
  #Copy one event into the events collection
  ev=eventsCEUS.find_one({})
  id=ev.pop('_id')
  coord=ev['geometry']
  ev.update({'geometry':{'type':'Point','coordinates':coord}})
  print(id)
  newid=events.insert_one(ev)
  for ev in eventsCEUS.find({'_id':{'$ne':ObjectId(id)}}).sort("magnitude",pymongo.DESCENDING):
    ev=Event(ev)
    mdist_list=[]
    for evs in events.find({}):     
      mdist_list.append(magdistance(ev,evs['latitude'],evs['longitude'],evs['magnitude']))
    if np.min(mdist_list)>=mdist:
      ev.mdist=np.min(mdist_list)
      coord=ev['geometry']
      ev.update({'geometry':{'type':'Point','coordinates':coord}})

      ev.pop('_id')
      #print(ev)
      events.insert_one(ev)
    
    

    
 
def eventdistance(lat1,lon1,m1,lat2,lon2,m2):
   r=geodetics.locations2degrees(lat1,lon1,lat2,lon2)
   dm=m1-m2
   return np.sqrt(r**2+dm**2)

if __name__=="__main__":
  logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
  logging.info("Config file: %s" % (sys.argv[1]))
  if len(sys.argv)>2:
    cmd=sys.argv[2]
  else:
    cmd="all"
  config=load_config(sys.argv[1])
  #
  dbcon=pymongo.MongoClient('mongodb://localhost:27017')
  db=dbcon.ceusn_quality
  #Get all events that meet our criteria
  
  # Add events to the database that meet our distance requirements
  process_catalog(db,mdist=0.8)