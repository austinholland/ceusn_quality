""" get_ceusn_events.py

Get CEUS earthquakes for analysis.  The goal is to get a good geographical mix so that could
end up being a bit of a challenge.
Currently I am going to try an algorithm that creates a distance measure that is a 
combination of distance in degrees (r) and magnitude (m) so that our distance is
dist=np.sqrt(r**2+(m2-m1)**2)
We can then apply a cutoff for distance.  For now I will try a distance greater than 1.0.  
The idea is to get a large sampling of event magnitudes and different locations.  I am 
afraid this will still produce a lot of events in Oklahoma.

Data is stored in a local mongo database in order to allow for changes in data structure 
as this develops.
"""

from pymongo import MongoClient
from obspy.core import *
import obspy.clients.fdsn as fdsn
import obspy.geodetics as geodetics
import numpy as np
import shapely.geometry
import logging
from utils import *
 
        
def get_eventsUS(db,conf,starttime=None,endtime=None):
  """ Get all events in the US within our study region, it turns out it is probably easier 
  to save the events in the database and then work through them"""
  fdsnclient=fdsn.Client('USGS')
  cat=fdsnclient.get_events(starttime=starttime,endtime=endtime,minmagnitude=2.5,maxmagnitude=4.5,
    orderby='time',minlatitude=conf['region']['minlatitude'],
    minlongitude=conf['region']['minlongitude'],maxlatitude=conf['region']['maxlatitude'],
    maxlongitude=conf['region']['maxlongitude'])
  logging.info("Retrieved %d events using fdsn client" % (cat.count()))
  catUS=event.catalog.Catalog(comments='withinUS')  
  borders=db.USborder
  eventsCEUS=db.eventsCEUS
  res=borders.find_one( {},{"features.geometry.coordinates":1} )
  coordinates=res['features'][0]['geometry']['coordinates']
  # Check to see if 
  eventsCEUS=db.eventCEUS
  polylist=[]
  for p in coordinates:
    polylist.append(shapely.geometry.Polygon(p[0]))
  poly=shapely.geometry.MultiPolygon(polylist) 
  for ev in cat:
    p=shapely.geometry.Point([ev.origins[0]['longitude'],ev.origins[0]['latitude']])
    if poly.contains(p):
      ev_id=eventsCEUS.insert_one(catalog2mongodict(ev))
  logging.info("%d events where inside the US" % (eventsCEUS.count()))

 

def catalog2mongodict(catev):
  """ Convert an Obspy event to a dictionary for MongoDB
  Right now we are not concerned with getting the best origin just an origin since obspy
  catalog items are more trouble than they are worth."""
  doc={
        'origintime':catev.origins[0]['time'].datetime,
        'latitude':catev.origins[0]['latitude'],
        'longitude':catev.origins[0]['longitude'],
        'depth':catev.origins[0]['depth']/1000.,
        'description':catev.event_descriptions[0]['text'],
        'magnitude':catev.magnitudes[0]['mag'],
        'magnitude_type':catev.magnitudes[0]['magnitude_type'],
        'geometry': [ catev.origins[0]['longitude'], catev.origins[0]['latitude'] ]
      }
  return doc
    
 

if __name__=="__main__":
  logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
  logging.info("Config file: %s" % (sys.argv[1]))
  if len(sys.argv)>2:
    cmd=sys.argv[2]
  else:
    cmd="all"
  config=load_config(sys.argv[1])
  #
  dbcon=MongoClient('mongodb://localhost:27017')
  db=dbcon.ceusn_quality
  #Get all events that meet our criteria
  get_eventsUS(db,config,starttime=UTCDateTime('2015-01-01T00:00:00.0'),endtime=UTCDateTime('2017-04-05T00:00:00.0'))
  # Add events to the database that meet our distance requirements
