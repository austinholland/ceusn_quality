""" grid_detection.py
Create a grid of detectable magnitudes at node points in the defined region
"""

from statcalc import *
from sourcespectra import *
from obspy.geodetics import gps2dist_azimuth

def calc_detection(netset,conf,session,dd=0.2):
  """ Calculate the magnitude of detection at a delta degrees of dd"""
  stalist=get_stations(netset,session)
  stalist2csv(stalist,netset)
  fh=open("GIS/%s/%s_mdetect.csv" % (netset['label'],netset['label']),'w')
  fh.write("longitude,latitude,Mdetect\n")
  for lat in np.arange(conf['region']['minlatitude'],conf['region']['maxlatitude'],dd):
    for lon in np.arange(conf['region']['minlongitude'],conf['region']['maxlongitude'],dd):
      dv=[] # Store detection values to all stations
      for sta in stalist:
        d,azm,baz=gps2dist_azimuth(sta.latitude,sta.longitude,lat,lon)
        threshold_db = sta.meanp25+conf['source']['nsigma']*sta.stdp25+conf['source']['snr_db']
        f=np.array([1,2])
        mw=noise2mw(f,threshold_db,
          Q=conf['source']['Q'],rho=conf['source']['rho'],vel=conf['source']['alpha'],
          delta=d/1000.,depth=conf['source']['depth'],stressdrop=conf['source']['stressdrop'],
          phase='P')
        dv.append(mw)
      dv=np.sort(dv)
      fh.write("%.2f,%.2f,%.2f\n" % (lon,lat,dv[conf['source']['nstations']-1]))
  fh.close()

def calc_detection_1s(netset,conf,session,dd=0.2):
  """ Calculate the magnitude of detection using the 1 second band at a delta degrees of dd"""
  stalist=get_stations(netset,session)
  stalist2csv(stalist,netset)
  fh=open("GIS/%s/%s_mdetect_1s.csv" % (netset['label'],netset['label']),'w')
  fh.write("longitude,latitude,Mdetect\n")
  for lat in np.arange(conf['region']['minlatitude'],conf['region']['maxlatitude'],dd):
    for lon in np.arange(conf['region']['minlongitude'],conf['region']['maxlongitude'],dd):
      dv=[] # Store detection values to all stations
      for sta in stalist:
        d,azm,baz=gps2dist_azimuth(sta.latitude,sta.longitude,lat,lon)
        threshold_db = sta.mean1+conf['source']['nsigma']*sta.std1+conf['source']['snr_db']
        f=np.array([1,2])
        mw=noise2mw(f,threshold_db,
          Q=conf['source']['Q'],rho=conf['source']['rho'],vel=conf['source']['alpha'],
          delta=d/1000.,depth=conf['source']['depth'],stressdrop=conf['source']['stressdrop'],
          phase='P')
        dv.append(mw)
      dv=np.sort(dv)
      fh.write("%.2f,%.2f,%.2f\n" % (lon,lat,dv[conf['source']['nstations']-1]))
  fh.close()

def stalist2csv(stalist,netset):
  """ Save a CSV file of stations used in detection estimations"""
  fname="GIS/%s/%s_stations.csv" % (netset['label'],netset['label'])
  fh=open(fname,'w')
  fh.write("label,longitude,latitude,mc100km,aggregate,peravailability,gapsperday,nlnmp25,nlnm1,nlnm8,nlnm22,nlnm110,staion,network\n")       
  for sta in stalist:
    fh.write("%s.%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%s,%s\n" % (sta.network,
      sta.station,sta.longitude,sta.latitude,sta.mc100km,sta.aggregate,sta.peravailability,sta.gapsperday,sta.nlnmp25,
      sta.nlnm1,sta.nlnm8,sta.nlnm22,sta.nlnm110,sta.station,sta.network))
  fh.close()
  
def get_stations(netset,session):
  """ Get a list of stations from statcalc.StationStats """
  stalist=[]
  if netset['label']=='All':
    netset['networks']=[]
    for net in session.query(StationStats.network).distinct():
      netset['networks'].append(net[0])
  elif netset['label']=='All-N4':
    netset['networks']=[]
    for net in session.query(StationStats.network).filter(StationStats.network!='N4').distinct():
      netset['networks'].append(net[0])   
  for net in netset['networks']:
    for sta in session.query(StationStats).filter(StationStats.network==net):
      stalist.append(sta)      
  return stalist

if __name__=="__main__":
  logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
  logging.info("Config file: %s" % (sys.argv[1]))
  if len(sys.argv)>2:
    cmd=sys.argv[2]
  else:
    cmd="base"
  config=load_config(sys.argv[1])
  # Create our database or open it
  if not os.path.exists(config['dbfile']):
    logging.error("Database file does not exist")
  else:
    engine=create_engine("sqlite:///%s" % (config['dbfile']),echo=False)
  Session=sessionmaker(bind=engine)
  session=Session()
  config=load_config(sys.argv[1])
  Session=sessionmaker(bind=engine)
  session=Session()
  for netset in config['mapdetect']:
    calc_detection_1s(netset,config,session)