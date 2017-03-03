""" single_stationgain.py

Calculate the single station gain for the N4 and the ANSS.  When talking about gain it
is the gain in detection.

"""


from statcalc import *
from sourcespectra import *
from obspy.geodetics import gps2dist_azimuth
from grid_detection import get_stations
import numpy as np

def calc_gain(session,netset,compare,conf,outfile,dd=0.2):
  node=np.loadtxt(compare,skiprows=1,delimiter=',')
  stations=get_stations(netset,session)
  outfh=open(outfile,'w')
  outfh.write("longitude,latitude,label,areagain,meangain,maxgain,num_nodes\n")
  for sta in stations:
    N=np.shape(node)[0]
    single=np.zeros(N)
    for i in np.arange(0,N):
      d,azm,baz=gps2dist_azimuth(sta.latitude,sta.longitude,node[i,1],node[i,0])
      threshold_db = sta.meanp25+conf['source']['nsigma']*sta.stdp25+conf['source']['snr_db']
      f=np.array([4,6,8])
      mw=noise2mw(f,threshold_db,
        Q=conf['source']['Q'],rho=conf['source']['rho'],vel=conf['source']['alpha'],
        delta=d/1000.,depth=conf['source']['depth'],stressdrop=conf['source']['stressdrop'],
        phase='P')
      single[i]=node[i,2]-mw
    indexes=np.where(single>0.)
    indexes=indexes[0]
    n=len(indexes)
    if n==0:
      areagain=0.
      meangain=0.
      maxgain=0.
    else:
      areagain=((n-2.)/2.)*(dd**2)
      meangain=np.mean(single[indexes])
      maxgain=np.max(single[indexes])
    stationgain2csv(outfh,sta,areagain,meangain,maxgain,n)
  outfh.close()
       
def stationgain2csv(fh,sta,areagain,meangain,maxgain,n):    
  fh.write("%.2f,%.2f,%s.%s,%.2f,%.2f,%.2f,%d\n"% (sta.longitude,sta.latitude,sta.network,
    sta.station,areagain,meangain,maxgain,n))

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
  comparefile="GIS/All-N4/All-N4_mdetect.csv"
  netset={"label":"N4","networks":['N4']}
  outfile="GIS/All-N4/station_gain.csv"
  calc_gain(session,netset,comparefile,config,outfile)