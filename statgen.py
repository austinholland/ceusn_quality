""" statgen.py

Generate channel and station statistics.  Currently using a mongodb database for storing
results.

"""
import irisws
from utils import *
import noise
from sourcespectra import *
import pymodm
import re

# Connect to MongoDB and call the connection "my-app".
pymodm.connect("mongodb://localhost:27017/ceusn_quality", alias="quality")

class StationStats(pymodm.MongoModel):
  label=pymodm.fields.CharField(primary_key=True)
  network = pymodm.fields.CharField()
  station = pymodm.fields.CharField()
  location=pymodm.fields.PointField(verbose_name="Station Location")
  gapsperday = pymodm.fields.FloatField(verbose_name="Gaps per Day")
  peravailability = pymodm.fields.FloatField(verbose_name="Percent Availability")
  aggregate=pymodm.fields.FloatField(verbose_name="Aggregate Score")
  nlnm1 = pymodm.fields.FloatField(verbose_name="NLNM Deviation .5-1 s")
  nlnmp25 = pymodm.fields.FloatField(verbose_name="NLNM Deviation .125-.25 s")
  nlnm1 = pymodm.fields.FloatField(verbose_name="NLNM Deviation .5-1 s")
  nlnm8 = pymodm.fields.FloatField(verbose_name="NLNM Deviation 4-8 s")
  nlnm22 = pymodm.fields.FloatField(verbose_name="NLNM Deviation 18-22 s")
  nlnm110 = pymodm.fields.FloatField(verbose_name="NLNM Deviation 90-110 s")
  mean1=pymodm.fields.FloatField(verbose_name="Mean Noise .5-1 s")
  meanp25=pymodm.fields.FloatField(verbose_name="Mean Noise .125-.25 s")
  std1=pymodm.fields.FloatField(verbose_name="STD Noise .5-1 s")
  stdp25=pymodm.fields.FloatField(verbose_name="STD Noise .125-.25 s")

   class Meta:
    write_concern = WriteConcern(j=True)
    connection_alias = 'quality'
    
  def __init__(self,label)
    lv=label.split('.')
    self.station=lv[1]
    self.network=lv[0]
    
  def get_coordinates(self,db,inventory):   
    for ch in db.ChannelStats.objects.raw({'network':{'$eq':self.network},'station':{'$eq':self.station}}):
      chan=ch.channel
      d=inventory.get_coordinates(chan)
      self.location=([d['longitude'],d['latitude']])
      return True
    else:
      return False    

  def populate_metrics(self,db,conf):
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
    for ch in db.ChannelStats.objects.raw({'network':self.network,'station':self.station,'nlnm1':{$exists:True,'$ne':""}}):
      if not (ch.network=='IU' and  (re.seach('\.HH.',ch.channel)):
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

class ChannelStats(pymodm.MongoModel):
  channel = pymodm.fields.CharField(primary_key=True)
  network = pymodm.fields.CharField()
  station = pymodm.fields.CharField()
  gapsperday = pymodm.fields.FloatField(verbose_name="Gaps per Day")
  peravailability = pymodm.fields.FloatField(verbose_name="Percent Availability")
  nlnm1 = pymodm.fields.FloatField(verbose_name="NLNM Deviation .5-1 s")
  nlnmp25 = pymodm.fields.FloatField(verbose_name="NLNM Deviation .125-.25 s")
  nlnm1 = pymodm.fields.FloatField(verbose_name="NLNM Deviation .5-1 s")
  nlnm8 = pymodm.fields.FloatField(verbose_name="NLNM Deviation 4-8 s")
  nlnm22 = pymodm.fields.FloatField(verbose_name="NLNM Deviation 18-22 s")
  nlnm110 = pymodm.fields.FloatField(verbose_name="NLNM Deviation 90-110 s")
  mean1=pymodm.fields.FloatField(verbose_name="Mean Noise .5-1 s")
  meanp25=pymodm.fields.FloatField(verbose_name="Mean Noise .125-.25 s")
  mean8=pymodm.fields.FloatField(verbose_name="Mean Noise 4-8 s")
  mean22=pymodm.fields.FloatField(verbose_name="Mean Noise 18-22 s")
  mean110=pymodm.fields.FloatField(verbose_name="Mean Noise 90-110 s")
  std1=pymodm.fields.FloatField(verbose_name="STD Noise .5-1 s")
  stdp25=pymodm.fields.FloatField(verbose_name="STD Noise .125-.25 s")
  std8=pymodm.fields.FloatField(verbose_name="STD Noise 4-8 s")
  std22=pymodm.fields.FloatField(verbose_name="STD Noise 18-22 s")
  std110=pymodm.fields.FloatField(verbose_name="STD Noise 90-110 s")
  ske1=pymodm.fields.FloatField(verbose_name="Skew Noise .5-1 s")
  skew25=pymodm.fields.FloatField(verbose_name="Skew Noise .125-.25 s")
  skew8=pymodm.fields.FloatField(verbose_name="Skew Noise 4-8 s")
  skew22=pymodm.fields.FloatField(verbose_name="Skew Noise 18-22 s")
  skew110=pymodm.fields.FloatField(verbose_name="Skew Noise 90-110 s")
  aggregate=pymodm.fields.FloatField(verbose_name="Aggregate Score")

  class Meta:
    write_concern = WriteConcern(j=True)
    connection_alias = 'quality'
    
  def __init__(self,channel)
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
    cmd="all"
  config=load_config(sys.argv[1])
  # Create our database or open it
  session=pymodm.connect(config['dbfile'], alias="quality")

  inv=get_inventory(config)
  if cmd=="base" or cmd=='all':
    channels=channel_list(inv)
    for chan in channels:
      logging.debug("Processing channel %s" % (chan))
      chstats=ChannelStats(chan)
      chstats.get_sumstats_iris(config)
      chstats.get_noisestats(config)
      chstats.save()
      
  if cmd=="aggregate" or cmd=='all':
    for ch in db.ChannelStats.objects.raw({'nlnm1':{$exists:True,'$ne':""}}):
      scores=[]
      scores.append(calc_grade([ch.nlnm1],16.073476,10.5388043))
      scores.append(calc_grade([ch.nlnmp25],16.355719,17.022342))
      scores.append(calc_grade([ch.nlnm8],3.33,12.53))
      scores.append(calc_grade([ch.nlnm22],13.41,12.64))
      scores.append(calc_grade([ch.nlnm110],13.57,14.79))
      scores.append(calc_grade([ch.gapsperday],.00274,.992))
      scores.append(ch.peravailability)
      ch.aggregate=np.average(scores)
      ch.save()
      
  if cmd=="station" or cmd=='all':
    stations=station_list(inv)
    for station in stations:      
      sta=StationStats(station)
      if sta.get_coordinates(session,inv):
        sta.populate_metrics(session,config)
      if sta.aggregate!=None:
        sta.save()
        