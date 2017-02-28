""" statcalc.py

Calculate and save channel and station statistics.

"""
import irisws
from sqlalchemy import Column, Integer, Float, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from utils import *
import noise
from sourcespectra import *

Base = declarative_base()

class StationStats(Base):
  __tablename__='stations'
  
  id=Column(Integer, primary_key=True)
  network=Column(String(2))
  station=Column(String(5))
  latitude=Column(Float)
  longitude=Column(Float)
  gapsperday=Column(Float)
  peravailability=Column(Float)
  nlnm1=Column(Float)
  nlnmp25=Column(Float)
  nlnm8=Column(Float)
  nlnm22=Column(Float)
  nlnm110=Column(Float)
  meanp25=Column(Float)
  stdp25=Column(Float)
  mc100km=Column(Float)
  aggregate=Column(Float)
  
  def __init__(self,station=None,network=None):
    self.network=network
    self.station=station
    self.aggregate=None
    
  def get_coordinates(self,session,inventory):
    ch=session.query(ChannelStats).filter(ChannelStats.network==self.network).filter(ChannelStats.station==self.station).first()
    if ch!=None:
      chan=ch.channel
      d=inventory.get_coordinates(chan)
      self.latitude=d['latitude']
      self.longitude=d['longitude']
      return True
    else:
      return False
    
  def populate_metrics(self,session,conf):
    gapsperday=[]
    peravailability=[]
    nlnm1=[]
    nlnmp25=[]
    nlnm8=[]
    nlnm22=[]
    nlnm110=[]
    meanp25=[]
    stdp25=[]
    aggregate=[]
    for ch in session.query(ChannelStats).filter(ChannelStats.nlnm1!=None).filter(ChannelStats.network==self.network).filter(ChannelStats.station==self.station):
      gapsperday.append(ch.gapsperday)
      peravailability.append(ch.peravailability)
      nlnm1.append(ch.nlnm1)
      nlnmp25.append(ch.nlnmp25)
      nlnm8.append(ch.nlnm8)
      nlnm22.append(ch.nlnm22)
      nlnm110.append(ch.nlnm110)
      meanp25.append(ch.meanp25)
      stdp25.append(ch.stdp25)
      aggregate.append(ch.aggregate)
    self.gapsperday=np.mean(gapsperday)
    self.peravailability=np.mean(peravailability)
    self.nlnm1=np.mean(nlnm1)
    self.nlnmp25=np.mean(nlnmp25)
    self.nlnm8=np.mean(nlnm8)
    self.nlnm22=np.mean(nlnm22)
    self.nlnm110=np.mean(nlnm110)
    self.meanp25=np.mean(meanp25)
    self.stdp25=np.mean(stdp25)
    self.aggregate=np.mean(aggregate)
    threshold_db = self.meanp25+conf['source']['nsigma']*self.stdp25+conf['source']['snr_db']
    f=np.array([4,6,8])
    mw=noise2mw(f,threshold_db,
      Q=conf['source']['Q'],rho=conf['source']['rho'],vel=conf['source']['alpha'],
      delta=100.,depth=conf['source']['depth'],stressdrop=conf['source']['stressdrop'],
      phase='P')
    self.mc100km=np.round(mw,decimals=2)
    return True
    
  
class ChannelStats(Base):
  __tablename__='channels'
  
  id=Column(Integer, primary_key=True)
  network=Column(String(2))
  station=Column(String(5))
  channel=Column(String)
  gapsperday=Column(Float)
  peravailability=Column(Float)
  nlnm1=Column(Float)
  nlnmp25=Column(Float)
  nlnm8=Column(Float)
  nlnm22=Column(Float)
  nlnm110=Column(Float)
  mean1=Column(Float)
  meanp25=Column(Float)
  mean8=Column(Float)
  mean22=Column(Float)
  mean110=Column(Float)
  std1=Column(Float)
  stdp25=Column(Float)
  std8=Column(Float)
  std22=Column(Float)
  std110=Column(Float)
  skew1=Column(Float)
  skewp25=Column(Float)
  skew8=Column(Float)
  skew22=Column(Float)
  skew110=Column(Float)
  aggregate=Column(Float) 
  
  def __init__(self,channel):
    """ Initialize an object with the unique channel NSLC"""
    self.channel=channel
    cvals=channel.split('.')
    self.network=cvals[0]
    self.station=cvals[1]
    
  def get_sumstats_iris(self,conf):
    """ Get the data for the channel based on time period expressed in our config file"""
    self.gapsperday=get_numgaps(self.channel,conf)
    self.peravailability=get_availability(self.channel,conf)
    
  def get_noisestats(self,conf):
    nlnm_model=noise.Noise(ratio_nhnm=0.,units='ACC')
    prange=[]
    data=load_noisepdf(self.channel,conf)
    if data!=None:
      for p in conf['periods']:
        prange=Prange(p)
        d=prange.contains_values(data)
        p,nlnm=nlnm_model.calculate(d[:,0])
        setattr(self,'mean'+prange.label,np.mean(d[:,1]))
        setattr(self,'std'+prange.label,np.mean(d[:,2]))
        setattr(self,'skew'+prange.label,np.mean(d[:,3]))
        setattr(self,'nlnm'+prange.label,np.mean(d[:,1])-np.mean(nlnm))


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
    engine=create_engine("sqlite:///%s" % (config['dbfile']),echo=False)
    Base.metadata.create_all(engine)
  else:
    engine=create_engine("sqlite:///%s" % (config['dbfile']),echo=False)
  Session=sessionmaker(bind=engine)
  session=Session()
  inv=get_inventory(config)
  if cmd=="base":
    channels=channel_list(inv)
    for chan in channels:
      logging.debug("Processing channel %s" % (chan))
      chstats=ChannelStats(chan)
      chstats.get_sumstats_iris(config)
      chstats.get_noisestats(config)
      session.add(chstats)
      session.commit()
  if cmd=="aggregate":
    for ch in session.query(ChannelStats).filter(ChannelStats.nlnm1!=None):
      scores=[]
      scores.append(calc_grade([ch.nlnm1],16.073476,10.5388043))
      scores.append(calc_grade([ch.nlnmp25],16.355719,17.022342))
      scores.append(calc_grade([ch.nlnm8],3.33,12.53))
      scores.append(calc_grade([ch.nlnm22],13.41,12.64))
      scores.append(calc_grade([ch.nlnm110],13.57,14.79))
      scores.append(calc_grade([ch.gapsperday],.00274,.992))
      scores.append(ch.peravailability)
      ch.aggregate=np.average(scores)
      session.add(ch)
      session.commit()
  if cmd=="station":
    stations=station_list(inv)
    for station in stations:
      network,station=station.split('.')
      sta=StationStats(network=network,station=station)
      if sta.get_coordinates(session,inv):
        sta.populate_metrics(session,config)
      if sta.aggregate!=None:
        session.add(sta)
        session.commit()