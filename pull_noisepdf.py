""" pull_noisepdf.py

Pull noise pdfs and save to raw text files as they come from IRISWS
"""

from obspy.core import *
from obspy import read_inventory
import obspy.clients.fdsn as fdsn
import irisws
from utils import *
import json
import logging
import sys
import os
import re


def get_ppdf(conf,inventory):
  """ For each channel in the inventory get the noise PPDF and save it by sncl to a 
  directory for each network.  The data is saved as the raw text output from the iris 
  webservice
  The method returns the number of channels written to file.
  """
  channels=channel_list(inv)
  for chan in channels:
    fname=pdfpath(chan,conf)
    if not os.path.exists(fname):
      try:
        txt=irisws.noise_pdf.query(target=chan+'.M',starttime=conf['starttime'],endtime=conf['endtime'],format='text')
        txt=txt.decode('utf-8')
        if txt=='':
          logging.warn("First attempt to get PPDF for %s failed" % (chan))
          txt=irisws.noise_pdf.query(target=chan+'.M',starttime=conf['starttime'],endtime=conf['endtime'],format='text')
          txt=txt.decode('utf-8')
        else:
          logging.debug("Got data for %s now save to file %s" % (chan,fname))
          ofh=open(fname,'w')
          ofh.write(txt)
          ofh.close()
      except:
        logging.warn("Unable to download or save PPDF for %s" % (chan))
  return len(channels)

    
    
if __name__=="__main__":
  logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
  logging.info("Config file: %s" % (sys.argv[1]))
  config=load_config(sys.argv[1])
  inv=get_inventory(config)
  make_netdirectories(config,inv)
  get_ppdf(config,inv)