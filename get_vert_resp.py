""" get_vert_response.py
Get the vertical response information and save it in the mongodb
"""
import pymongo
import gridfs
from obspy.core import *
import obspy.clients.fdsn as fdsn
import obspy.clients.iris as iris
import obspy.geodetics as geodetics
import numpy as np
import shapely.geometry
import logging
from utils import *

def respfilename(seedid):
  return "resp/RESP.%s" % (ch)
  
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
  for ch in channels:
    if ch[-1]=='Z':     
      net,sta,loc,c=ch.split('.')
      d=inv.get_coordinates(ch)
      geom=([d['longitude'],d['latitude']])
      chan={'_id':ch,'latitude':d['latitude'],'longitude':d['longitude'],
        'geometry':{'type':'Point','coordinates':geom},
        'respfile':respfilename(ch)}
      inventory.insert_one(chan)
      try:
        resp=irisclient.resp(net,sta,location=loc,channel=c,starttime=starttime,endtime=endtime,filename=respfilename(ch))
      except:
        print("No response data for channel %s" % (ch))