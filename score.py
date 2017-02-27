""" score.py
Caclulate the scoring parameters for nlnm1 and nlnmp25
"""
from statcalc import *
from utils import *
import matplotlib.pyplot as plt

if __name__=="__main__":
  logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
  logging.info("Config file: %s" % (sys.argv[1]))
  config=load_config(sys.argv[1])
  # Create our database or open it
  if not os.path.exists(config['dbfile']):
    engine=create_engine("sqlite:///%s" % (config['dbfile']),echo=False)
    Base.metadata.create_all(engine)
  else:
    engine=create_engine("sqlite:///%s" % (config['dbfile']),echo=False)
  Session=sessionmaker(bind=engine)
  session=Session()   
  bottom_percentile=1.
  top_percentile=61.
  vals=[]
  for v in session.query(ChannelStats.nlnm1).filter(ChannelStats.nlnm1!=None):
    if v!=None:
      vals.append(v[0])
  vals=np.array(vals)
  plt.figure()
  plt.hist(vals,bins=50)
  plt.title('1-.5')
  vals.sort()
  per5=np.percentile(vals,bottom_percentile)
  p2=per5
  per95=np.percentile(vals,top_percentile) 
  best=vals[np.where(vals<=per95)]
  best=vals[np.where(best>=per5)]
  m=np.mean(best)-p2
  print("Number of Channels: "+str(len(vals)))
  print("From %f percentile to %f percentile"% (bottom_percentile,top_percentile))
  print("NLNM 0.5 - 1 s Period Deviation p2: %f, m: %f" % (p2,m))
  plt.figure()
  plt.subplot(211)
  plt.plot(np.arange(0,len(vals)),vals,'-k')
  plt.ylabel("dB")
  plt.suptitle("NLNM 0.5 - 1 s Period Deviation")
  plt.subplot(212)
  plt.plot(np.arange(0,len(vals)),calc_grade(vals,p2,m),'-k')
  plt.ylabel("Percent")
  plt.xlabel("channel number")
  plt.savefig("score-nlnm1.png")
  
  vals=[]
  for v in session.query(ChannelStats.nlnmp25).filter(ChannelStats.nlnmp25!=None):
    if v!=None:
      vals.append(v[0])
  vals=np.array(vals)
  vals.sort()
  plt.figure()
  plt.hist(vals,bins=50)
  plt.title('4 8 Hz')
  per5=np.percentile(vals,bottom_percentile)
  p2=per5
  per95=np.percentile(vals,top_percentile) 
  best=vals[np.where(vals<=per95)]
  best=vals[np.where(best>=per5)]
  m=np.mean(best)-p2
  print("NLNM 0.125 - .25 s Period Deviation p2: %f, m: %f" % (p2,m))
  plt.figure()
  plt.subplot(211)
  plt.plot(np.arange(0,len(vals)),vals,'-k')
  plt.ylabel("dB")
  plt.suptitle("NLNM 0.125 - .25 s Period Deviation")
  plt.subplot(212)
  plt.plot(np.arange(0,len(vals)),calc_grade(vals,p2,m),'-k')
  plt.ylabel("Percent")
  plt.xlabel("channel number")
  plt.savefig("score-nlnmp25.png")
  
 
  plt.show()