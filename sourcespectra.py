# -*- coding: utf-8 -*-
"""" sourcespectra.py

This hopefully provides a clean method for calculating source spectra and then applying 
other terms such as attenuation and geometrical spreading.

"""
import logging
import numpy as np
from obspy.signal.spectral_estimation import get_nlnm, get_nhnm

def ass_snes(f,mw,c_o,phase='P',rho=2.7,stressdrop=1.,n=2,gamma=2.):
  """
  Calculate the acceleration source spectrum at the given frequencies f.
  r is in kilometers hypocentral distance
  n=0 output in displacement
  n=1 output in velocity
  n=2 output in acceleration # this is the default
  c_o is the phase velocity at the source
  stressdrop is in MPA
  
  Note the dependence on r was removed to provide the source spectra.  This allows us
  to compare methods and select the appropriate geometric spreading and attenuation.
  
  gamma the damping constant for high frequencies
  D’Alessandro A, Luzio D, D’Anna G, Mangano G (2011) Seismic Network Evaluation through 
  Simulation: An Application to the Italian National Seismic Network. 
  B Seismol Soc Am 101:1213–1232. doi: 10.1785/0120100066
  """
  
  # Convert units
  stressdrop=stressdrop*1.e6
  c=c_o*1.e3
  rho=rho*1.e6
  
  #r=np.sqrt(delta**2+depth**2)
  m_o=mw2moment(mw)
  
  w=np.array(f)*np.pi*2
  if phase=='P':
    Rp=0.516
  elif phase=='S':
    Rp=0.632
  else:
    raise ValueError('Unknown phase type requested')
  Cs=Rp/(4*np.pi*rho*(c**3))
  w_o=corner_frequency(m_o,stressdrop,c,phase=phase)
  S_w=Cs*m_o*(w**n)/(1+(w/w_o)**gamma)
  return S_w  

def ass2mw(f,A,c_o,phase='P',rho=2.7,stressdrop=1.,n=2,gamma=2.):
  """ Convert a spectral value determined at the source (ie attenuation and geometrical 
  spreading removed to match the source spectra for a Mw, really the inverse method of
  ass_snes()
  """
  # Convert units
  stressdrop=stressdrop*1.e6
  c=c_o*1.e3
  rho=rho*1.e6
  w=np.array(f)*np.pi*2
  if phase=='P':
    Rp=0.516
  elif phase=='S':
    Rp=0.632
  else:
    raise ValueError('Unknown phase type requested')
  Cs=Rp/(4*np.pi*rho*(c**3))
  # With only one amplitude measurement the corner frequency cannot be known.
  # We start by assuming it is close to the range of frequencies we are looking at
  w_o=2*np.pi*np.mean(f)
  m_o=(A*(1+(w/w_o)**gamma))/(Cs*(w**n))   
  # Now we take our resulting moment and calculate the corner frequency and moment again
  w_o=corner_frequency(np.mean(m_o),stressdrop,c,phase=phase)
  m_o=(A*(1+(w/w_o)**gamma))/(Cs*(w**n))
  return momment2mw(np.mean(m_o))
  
def mw2moment(mw):
  """ Returns the seismic moment in N-m
  
  """
  mo=np.power(10,((mw+10.7)*(3./2.))) # dyne cm
  mo=(mo/1.e5)*.01
  return mo

def momment2mw(mo):
  mo=(mo*1.e5)/.01 # Convert to dyne cm
  return (2./3.)*np.log10(mo)-10.7
  
def corner_frequency(mo,stressdrop,c,phase='S'):
  """ return the source corner frequency in radians for a given source
  c is the velocity
  from EQN B8:
  D’Alessandro A, Luzio D, D’Anna G, Mangano G (2011) Seismic Network Evaluation through 
  Simulation: An Application to the Italian National Seismic Network. 
  B Seismol Soc Am 101:1213–1232. doi: 10.1785/0120100066
  """
  # Set velocity of fault rupture
  if phase=='P':
    k=3.36
  elif phase=='S':
    k=2.34
  else:
    raise ValueError('Unknown phase type requested')
  xi=np.cbrt(16./7.)*k
#  a=np.cbrt((7.*mo)/(16*stressdrop))
  wo=np.cbrt(stressdrop/mo)*xi*c
  return wo

def attenuation(f,q,delta,depth,c,phase='P',vpvs=1.73):
  """ Apply geometrical spreading and attenuation q is the attenuation of shear waves
  delta and depth are in kilometers and c is in km/s since 1/r geometric spreading is in
  terms of km
  """
  Qk=57823
  if phase=='S':
    Q=q
  if phase=='P':  # From Lay & Wallace p. 170
    L=4./3.*((1./vpvs)**2)
    Qinv=L*(1./q)+(1-L)*(1./Qk)
    Q=1./Qinv
  else:
    raise ValueError('Unknown phase type requested')

  # calculate
  r=np.sqrt(delta**2+depth**2)
  w=np.array(f)*np.pi*2
  # Factor of 2 for Free surface amplification
  A=(2./r)*np.exp(-w*r/(c*Q))
  return A
  
def noise2mw(f,db,Q=600,rho=2.7,vel=6.0,delta=100.,depth=5.,stressdrop=5.,phase='P'):
    """ Calculate the MW detectable given a measured noise level averaged at frequencies f
    """
    # Convert energy in decibels to an amplitude
    A=np.sqrt(np.power(10,(db)/10.)*f)
    db_new=10*np.log10((A**2)/f)
    #logging.debug("dB difference %f" % (db -np.mean(db_new)))
    # Remove the attenuation by calculating the attenuation and then taking the inverse
    Ae=attenuation(f,Q,delta,depth,vel,phase=phase)
    A=A/Ae
    mw=ass2mw(f,A,vel,phase=phase,rho=rho,stressdrop=stressdrop,n=2,gamma=2.)
    
    return mw
    
if __name__=="__main__":
  import matplotlib.pyplot as plt
  f=np.array([20.,19.,18.,17.,16.,15.,14.,13.,12.,11.,10.,9.,8.,7.,6.,5.,4.,3.,2.,1.,.5,
    .25,.1,.01,.001])
  mw=4.5
  rho=2.7
  alpha=6.2
  stressdrop=5. # MPa
  delta=100.
  depth=10.
  
  print("Corner f %f" % (np.pi*2*corner_frequency(mw2moment(mw),stressdrop,alpha*1.e3,phase='P')))
  As=ass_snes(f,mw,alpha,phase='P',rho=rho,stressdrop=stressdrop,n=2,gamma=2.)
  Ae=attenuation(f,600.,delta,depth,alpha,phase='P')

  plt.figure()
  per1,nlnm=get_nlnm()
  per2,nhnm=get_nhnm()
  plt.semilogx(per1,nlnm, label='NLNM/NHNM', color='.7')
  plt.semilogx(per2,nhnm, color='.7')
  plt.semilogx(1./f,10*np.log10((As**2)/f),label='SNES')
#   plt.semilogx(1./f,10*np.log10((Ae**2)/f),label='Attenuate')
  plt.semilogx(1./f,10*np.log10(((As*Ae)**2)/f),label="Mw %.1f @ %.1f,z=%.1fkm" % (mw,delta,depth))
  plt.xlabel('Period (s)')
  plt.ylabel('Acceleration (db)')
  plt.legend()
  
  # Check to see if we go backwards fine
  f=np.array([4,6,8])
  As=ass_snes(f,mw,alpha,phase='P',rho=rho,stressdrop=stressdrop,n=2,gamma=2.)
  Ae=attenuation(f,600.,delta,depth,alpha,phase='P')
  db=np.mean(10*np.log10(((As*Ae)**2)/f))
  mw_calc=noise2mw(f,db,Q=600,rho=2.7,vel=alpha,delta=100.,depth=10.,stressdrop=stressdrop,phase='P')
  print(mw_calc)
  print("Mw= %.2f reversed=%.2f" % (mw,mw_calc))
  plt.show()