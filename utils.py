""" utils.py
A catch-all for utilities used in the processing.
"""
from obspy.core import *
from obspy import read_inventory
import obspy.clients.fdsn as fdsn
import numpy as np
import irisws
import json
import logging
import sys
import os
import re

class Prange():
  """ This class is a utility to define a period range and compare values to that range
  not sure this will help simplify things, but we will see.
  """
  def __init__(self,cdict):
    self.label=cdict['label']
    self.min=cdict['min']
    self.max=cdict['max']
    
  def contains(self,P):
    """ If a period P is within bounds return True otherwise false"""
    if P>=self.min and P<=self.max:
      return True
    else: 
      return False
    
  def contains_values(self,pv_array):
    """ Compare period and value tuples to see if they are in the range. Returns a list of
    periods and values. 
    """
    indexes=[]
    for i in np.arange(0,np.shape(pv_array)[0]):
      if self.contains(pv_array[i,0]):
       indexes.append(i)
    return pv_array[indexes,:]
      
  def __repr__(self):
    return "<Prange %s (%s,%s)>" % (self.label,str(self.min),str(self.max))
    
def load_config(jsonfile):
  if os.path.exists(jsonfile):
    fh=open(jsonfile)
    raw=fh.read()
    try:
      config=json.loads(raw)
    except:
      logging.error("Error in JSON file %s please validate it." % (jsonfile))
    fh.close()
  else:
    logging.error("Configuration file %s does not exist" % (jsonfile))
  logging.info("Config file %s loaded" % (jsonfile))
  logging.info(json.dumps(config,sort_keys=True,indent=4, separators=(',', ': ')))
  return config

def pdfpath(channel,conf):
    cvals=channel.split('.')
    net=cvals[0]
    return "%s/%s/%s_pdf.txt" % (conf['datadir'],net,channel)
    
def get_inventory(conf,level='channel',select="[BH]H?"):
  """ Get or load the inventory depending on whether it exists or not.  Be sure to delete
  the inventory if you change relevant parameters in the config file such as region or 
  channel matching."""
  if os.path.exists(conf["inventoryfile"]):
    inv=read_inventory(conf["inventoryfile"])
    return inv
  else:
    fdsnclient=fdsn.Client("IRIS")
    temp=fdsnclient.get_stations(minlatitude=conf['region']['minlatitude'],
      maxlatitude=conf['region']['maxlatitude'],
      minlongitude=conf['region']['minlongitude'],
      maxlongitude=conf['region']['maxlongitude'],
      level=level,
      starttime=conf['starttime'],
      endtime=conf['endtime'])
    # Select the channels from the temporary inventory
    inv=temp.select(channel="[BH]H?")
    inv.write(conf["inventoryfile"],format='STATIONXML')
    logging.info(str(inv))
  return inv

def station_list(inventory):
  """ Return a list of stations contained in an inventory"""
  d=inventory.get_contents()
  lsta=[]
  stas=d['stations']
  for sta in stas:
    stav=sta.split(' ')
    lsta.append(stav[0])
  return lsta
  
def channel_list(inventory):
  """ Return a unique list of channels contained in an inventory"""
  d=inventory.get_contents()
  lchan=d['channels']
  lchan=set(lchan)
  return list(lchan)

def make_netdirectories(config,inventory):
  d=inventory.get_contents()
  nets=d['networks']
  for n in nets:
    dirpath="%s/%s" % (config['datadir'],n)
    if not os.path.exists(dirpath):
      os.mkdir(dirpath)
  return True
  
def get_availability(channel,conf):
  """ Retrieve mustang availability measurements for all channel average all values 
  returned"""
  txt=''
  try:
    txt=irisws.measurements.query(metric='percent_availability',target=channel+'.M',
      starttime=conf['starttime'],endtime=conf['endtime'],format='text')
    txt=txt.decode('utf-8')
  except:
    logging.warn("Unable to retrieve availability for %s" % (channel))
    return 0.
  lines=txt.split('\n')
  vals=[]
  for line in lines[2:]:  #skip first two lines for header hopefully this doesn't change
    lv=line.split(',')
    try:
      vals.append(float(lv[0].strip('"')))
    except:
      pass
  return np.mean(vals)
  
def get_numgaps(channel,conf):
  """ Retrieve mustang availability measurements for all channel average all values 
  returned"""
  txt=''
  try:
    txt=irisws.measurements.query(metric='num_gaps',target=channel+'.M',
      starttime=conf['starttime'],endtime=conf['endtime'],format='text')
    txt=txt.decode('utf-8')
  except:
    logging.warn("Unable to retrieve num_gags for %s" % (channel))
    return 0.
  lines=txt.split('\n')
  vals=[]
  for line in lines[2:]:  #skip first two lines for header hopefully this doesn't change
    lv=line.split(',')
    try:
      vals.append(float(lv[0].strip('"')))
    except:
      pass
  return np.mean(vals)
  
def load_noisepdf(channel,conf):
  import scipy.stats as stats
  fname=pdfpath(channel,conf)
  if os.path.exists(fname):
    freq=[]
    mean=[]
    std=[]
    skew=[]
    ifh = open(fname,'r')
    curf=None
    powers=[]
    firstpass=True
    for line in ifh:
      if line[0]!='#': # Ignore lines starting with # sign
        lv=line.split(',')
        f=float(lv[0])
        if f!=curf and not firstpass:
          freq.append(curf)
          mean.append(np.mean(powers))
          std.append(np.std(powers))
          skew.append(stats.skew(powers))
          powers=[]   
        curf=f
        if firstpass:
          firstpass=False
        powers.extend([int(lv[1])]*int(lv[2]))
      
    freq=np.array(freq)

    data=np.zeros(shape=(len(freq),4))
    data[:,0]=1./freq
    data[:,1]=mean
    data[:,2]=std
    data[:,3]=skew
    return data
  else:
    return None
    
def calc_grade(p1,p2,m):
  p1=np.array(p1)
  grade=100.-15.*((p1-p2)/(m))
  np.clip(grade,0.,100.,out=grade)
  return grade
  
  
      
  