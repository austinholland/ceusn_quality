""" get_event_channels.py
Get the vertical response information and save it in the mongodb
"""
import pymongo
from bson.son import SON
from obspy.core import *
import obspy.clients.fdsn as fdsn
import obspy.clients.iris as iris
import obspy.geodetics as geodetics
import obspy.taup as taup
import numpy as np
import shapely.geometry
import logging
from utils import *

def respfilename(seedid):
  return "resp/RESP.%s" % (ch)
  
def get_travel_time(dist_km,phase='P',velmod='AK135')
  """ use taup to get the travel time for the selected phase so we know which data
  to get """
  

def get_trace_data(db,ev,inv):
  """ Get trace data for a channel and save it in the event document in mongodb.
  """   
  scnl=inv['_id']
  
if __name__=="__main__":
  logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
  logging.info("Config file: %s" % (sys.argv[1]))
  if len(sys.argv)>2:
    cmd=sys.argv[2]
  else:
    cmd="all"
  config=load_config(sys.argv[1])
  inv=get_inventory(config)
    # Get the resp files for the following interval    
  starttime=UTCDateTime('2015-01-01T00:00:00.0')
  endtime=UTCDateTime('2017-04-05T00:00:00.0')
  irisclient=iris.Client()

  dbcon=pymongo.MongoClient('mongodb://localhost:27017')
  db=dbcon.ceusn_quality
  inventory=db.inventory
  channels=channel_list(inv)
  events=db.events
  events.create_index([("geometry", pymongo.GEOSPHERE)])
  inventory.create_index([("geometry", pymongo.GEOSPHERE)])
  ev=events.find_one()
  print(ev)
  #query=[SON([("geonear","geometry")('near', [ev['geometry']['coordinates']]), ("$maxDistance", 600000)]),'spherical':True]
  query = events.aggregate([{'$geoNear':{'near':ev['geometry'],'spherical':True,'distanceField':'distance','maxDistance':600000}}])
  coords=ev['geometry']['coordinates']
  print(coords)
  for doc in inventory.find({'geometry':{'$near':{'coordinates':coords},'$maxDistance':600000}}):
    print(doc)
#   for doc in inventory.find({'geometry':{'$near':{'coordinates':coords},'$maxDistance':600000}}):
#     print(doc)