""" network_plots.py

Here we plot summaries of performance by network

"""
import matplotlib.pyplot as plt
from statcalc import *
from utils import *

def plot_net(network,session):
  N=session.query(StationStats.station).filter(StationStats.network==network).count()
  averages={"network":network,"num_stations":N}
  fig=plt.figure(figsize=(8.5,11))
  fig.subplots_adjust(left=0.09, wspace=0.2,hspace=.33,right=.97,top=.92,bottom=.05)
  ax1=plt.subplot2grid((5,2),(0,0),colspan=2)
  v=session.query(StationStats.aggregate).filter(StationStats.network==network).all()
  v=np.array(list(v))
  v.flatten()
  ax1.hist(v,bins=[0,50,60,70,80,90,100])
  #plt.xlim([60,100])
  plt.title("Aggregate (Avg %.2f)" % (np.average(v)))
  averages['aggregate']=np.average(v)
  plt.ylabel('# stations')

  ax2=plt.subplot2grid((5,2),(1,0))
  v=session.query(StationStats.peravailability).filter(StationStats.network==network).all()
  v=np.array(list(v))
  v.flatten()
  ax2.hist(v,bins=[0,50,60,70,80,90,100])
  plt.title("Percent Availability (Avg %.2f)" % (np.average(v)))
  averages['peravailability']=np.average(v)
  plt.ylabel('# stations')    
  ax3=plt.subplot2grid((5,2),(1,1))
  v=session.query(StationStats.gapsperday).filter(StationStats.network==network).all()
  v=np.array(list(v))
  v.flatten()
  ax3.hist(v,bins=[0.15,0.3,1.0,2.0,5.0,10,20,50,200])
  plt.xlim([0,10.])
  plt.title("Gaps per day (Avg %.2f)" % (np.average(v)))
  averages['gapsperday']=np.average(v) 

  ax4=plt.subplot2grid((5,2),(2,0))
  v=session.query(StationStats.mc100km).filter(StationStats.network==network).all()
  v=np.array(list(v))
  v.flatten()
  ax4.hist(v,bins=[1.5,1.8,2.1,2.4,2.7,3.0,3.3,3.6])
  plt.title("M detection @ 100 km (Avg %.2f)" % (np.average(v)))
  averages['mc100km']=np.average(v)
  plt.ylabel('# stations')    
  ax5=plt.subplot2grid((5,2),(2,1))
  v=session.query(StationStats.nlnmp25).filter(StationStats.network==network).all()
  v=np.array(list(v))
  v.flatten()
  ax5.hist(v,bins=[10,20,30,40,50,60,70,80,90,100])
  plt.title("NLNM dev 4-8 Hz (Avg %.2f dB)" % (np.average(v)))
  averages['nlnmp25']=np.average(v) 

  ax6=plt.subplot2grid((5,2),(3,0))
  v=session.query(StationStats.nlnm1).filter(StationStats.network==network).all()
  v=np.array(list(v))
  v.flatten()
  ax6.hist(v,bins=[10,20,30,40,50,60,70,80,90,100])
  plt.title("NLNM dev 1-2 Hz (Avg %.2f dB)" % (np.average(v)))
  averages['nlnm1']=np.average(v)
  plt.ylabel('# stations')    
  ax7=plt.subplot2grid((5,2),(3,1))
  v=session.query(StationStats.nlnm8).filter(StationStats.network==network).all()
  v=np.array(list(v))
  v.flatten()
  ax7.hist(v,bins=[5,10,15,20,25,30,35,40,45,50,90])
  plt.title("NLNM dev 4-8 s (Avg %.2f dB)" % (np.average(v))) 
  averages['nlnm8']=np.average(v)

  ax8=plt.subplot2grid((5,2),(4,0))
  v=session.query(StationStats.nlnm22).filter(StationStats.network==network).all()
  v=np.array(list(v))
  v.flatten()
  ax8.hist(v,bins=[5,10,15,20,25,30,35,40,45,50,60,70,80,90])
  plt.title("NLNM dev 18-22 s (Avg %.2f dB)" % (np.average(v)))
  averages['nlnm22']=np.average(v)
  plt.ylabel('# stations')    
  ax9=plt.subplot2grid((5,2),(4,1))
  v=session.query(StationStats.nlnm110).filter(StationStats.network==network).all()
  v=np.array(list(v))
  v.flatten()
  ax9.hist(v,bins=[5,10,15,20,25,30,35,40,45,50,60,70,80,90])
  plt.title("NLNM dev 90-110 s (Avg %.2f dB)" % (np.average(v))) 
  averages['nlnm110']=np.average(v)

  plt.suptitle("%s Network Summary (%d stations)" % (network,N))
  plt.savefig("summary_%s.pdf" % (network))
  return averages
#   except:
#     logging.info("No data for network %s" % (network))
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
  fh=open('network_averages.csv','w')
  fh.write("network,aggregate,percent_availability,gapsperday,mc100km,nlnmp25,nlnm1,nlnm8,nlnm22,nlnm110\n")
  for net in session.query(StationStats.network).distinct():
    avg=plot_net(net[0],session)
    fh.write("%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f\n" % 
      (avg['network'],avg['aggregate'],avg['peravailability'],avg['gapsperday'],
      avg['mc100km'],avg['nlnmp25'],avg['nlnm1'],avg['nlnm8'],avg['nlnm22'],avg['nlnm110']))
  fh.close()