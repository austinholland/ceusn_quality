"""irisws

Python module for low end helper functions to query IRIS FDSNWS and IRISWS IRIS DMC Web 
Services Interfaces
Returns the data as returned by the IRIS DMC Web Services as a the 
resulting response, the user must know what the data types are and what to do with it.

More information and example keys http://service.iris.edu/

Could be expanded to support the WADL definitions and allow for a more high end interface.

Help for each webservices help can be displayed, as markdown text, or html  
representation. html2text is required for markdown conversion.  In addition one can view 
the help on webservices from the IRIS website if working in interactive mode this can
be helpful.

Defined available queries are attributes of this module ['dataselect', 'distaz', 
'evalresp', 'event', 'fedcatalog', 'finnengdahl', 'measurements', 'metadatachange', 
'metrics', 'noise_pdf', 'noise_psd', 'resp', 'rotation', 'sacpz', 'station', 'targets', 
'timeseries', 'traveltime', 'urllib', 'virtualnetwork']

new ones that follow the IRIS conventions can be created with the webservice class.

Example usage:
import irisws
irisws.station.query(net='IU',sta='ANMO',cha='BH1',loc='00',format='text')
#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime 
IU|ANMO|34.9459|-106.4572|1850.0|Albuquerque, New Mexico, USA|1995-07-14T00:00:00|2000-10-19T16:00:00
IU|ANMO|34.9502|-106.4602|1839.0|Albuquerque, New Mexico, USA|2000-10-19T16:00:00|2002-11-19T21:07:00
IU|ANMO|34.94591|-106.4572|1820.0|Albuquerque, New Mexico, USA|2002-11-19T21:07:00|2008-06-30T00:00:00
IU|ANMO|34.94591|-106.4572|1820.0|Albuquerque, New Mexico, USA|2008-06-30T00:00:00|2008-06-30T20:00:00
IU|ANMO|34.94591|-106.4572|1820.0|Albuquerque, New Mexico, USA|2008-06-30T20:00:00|2599-12-31T23:59:59

You may have to decode your results for example if you had some output :
>>> type(txt)
<class 'bytes'>
>>>txt=txt.decode('utf-8')
"""
import urllib
import urllib.parse
import urllib.request
import logging

class WebService():
  """ Generic class to support different web service queries"""
  def __init__(self,urlprefix,timeout=120):
    self.prefix=urlprefix
    self.timeout=timeout
  
  def query(self,**kwargs):
    """Webservice query arguments are passed in as a python dictionary or as keyword 
    arguments and rewritten as web request arguments.  More information on each web
    service argurments are available at http://service.iris.edu/."""
    # Ensure that all keys are converted to string values for building URL
    for key in kwargs.keys():
      kwargs[key]=str(kwargs[key])
    query=urllib.parse.urlencode(kwargs,safe=':')
    url=self.prefix+'query?'+query
    print(url)
    logging.debug(url)
    try:
      ust=urllib.request.urlopen(url,timeout=self.timeout).read()
    except:
      logging.error("Unable to access URL: %s",url)
      ust=''
    return ust
    
  def help(self,output='html',view=False):
    """ Return the description information for the Web Service from it's web page.  The
    default output format is html.  If view equals true display in webbrowser"""
    hstr=urllib.request.urlopen(self.prefix).read()
    hstr=str(hstr)
    if output=='md' or output=='text':
      import html2text
      import re
      hstr=re.sub('<script>.*?</script>','',hstr)
      h=html2text.HTML2Text()
      h.ignore_images=True
      hstr=h.handle(hstr)
    if view:
      import webbrowser
      webbrowser.open(self.prefix)

    return hstr

#FDSN WebServices
station=WebService('http://service.iris.edu/fdsnws/station/1/')
event=WebService('http://service.iris.edu/fdsnws/event/1/')
dataselect=WebService('http://service.iris.edu/fdsnws/dataselect/1/')

#IRIS WebServices
fedcatalog=WebService('http://service.iris.edu/irisws/fedcatalog/1/')
timeseries=WebService('http://service.iris.edu/irisws/timeseries/1/')
rotation=WebService('http://service.iris.edu/irisws/rotation/1/')
sacpz=WebService('http://service.iris.edu/irisws/sacpz/1/')
resp=WebService('http://service.iris.edu/irisws/resp/1/')
evalresp=WebService('http://service.iris.edu/irisws/evalresp/1/')
virtualnetwork=WebService('http://service.iris.edu/irisws/virtualnetwork/1/')
traveltime=WebService('http://service.iris.edu/irisws/traveltime/1/')
finnengdahl=WebService('http://service.iris.edu/irisws/flinnengdahl/2/')
distaz=WebService('http://service.iris.edu/irisws/distaz/1/')
metadatachange=WebService('http://service.iris.edu/irisws/metadatachange/1/')

#MUSTANG WebServices
measurements=WebService('http://service.iris.edu/mustang/measurements/1/')
noise_psd=WebService('http://service.iris.edu/mustang/noise-psd/1/')
noise_pdf=WebService('http://service.iris.edu/mustang/noise-pdf/1/')
metrics=WebService('http://service.iris.edu/mustang/metrics/1/')
targets=WebService('http://service.iris.edu/mustang/targets/1/')

 