""" dbutils.py 

These database utilities are a collection of methods to work with the pymongo database
such as pickling objects in a format that can be stored in documents and such.

"""
from obspy.core import *
import numpy as np
from datetime import datetime

def trace2dict(tr):
  """ Transform an obspy trace (tr) to a dictionary that can save the trace as a JSON object
  This method only works with a single trace.  Not sure what the best method to handle
  multiple traces might be.  
  
  Response data is not saved in this structure as technically it is not part of a trace.
  UTCDateTimes are converted to python datatime objects
  """
  trace={}
  trace['data']=list(tr.data)
  trace['stats']={}
  for key in tr.stats.keys():
    if key!='response':
      if isinstance(tr.stats[key],UTCDateTime):
        trace['stats'][key]=tr.stats[key].datetime
      else:
        trace['stats'][key]=tr.stats[key]
  return trace
  
  
def dict2trace(trace):
  """ Transform a dictionary to an obspy trace
  """
  tr=Trace()
  for key in trace['stats'].keys():
    if isinstance(trace['stats'][key],datetime):
      if key=='starttime':
        tr.stats[key]=UTCDateTime(trace['stats'][key])
    else:
      tr.stats[key]=trace['stats'][key]
  tr.data=np.array(trace['data'])
  return tr
