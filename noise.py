""" noise.py
Create noise models from NLNM or NHNM
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
from obspy.core import *
from obspy.signal.spectral_estimation import get_nhnm, get_nlnm



class Noise():
  """ Originally this class was intended to provide a more generic set of Earth noise
  models.  However, It is now designed to provide just the Peterson (1993) noise models.
  One can specify the units and the percentage in terms from 0 to 1 of NHNM so 0. would
  be a comple NLNM mode and 1 would be the NHNM. 
  """
  _nlnm_coeff=np.array([[.1,-162.36,5.64],
    [.17,-166.7,0.00],
    [.4,-170.,-8.3],
    [.8,-166.4,28.9],
    [1.24,-168.60,52.48],
    [2.4,-159.98,29.81],
    [4.3,-141.1,0.],
    [5.,-71.36,-99.77],
    [6.,-97.26,-66.49],
    [10.,-132.18,-31.57],
    [12.,-205.27,36.16],
    [15.6,-37.65,-104.33],
    [21.9,-114.37,-47.10],
    [31.6,-160.58,-16.28],
    [45.,-187.5,0.],
    [70.,-216.47,15.70],
    [101.,-185.,0.],
    [154.,-168.34,-7.61],
    [328.,-217.43,11.9],
    [600.,-258.28,26.6],
    [10000.,-346.88,48.75],
    [100000.,np.nan,np.nan]])

  _nhnm_coeff=np.array([[0.1,-108.73,-17.23],
    [.22,-150.34,-80.5],
    [.32,-122.31,-23.87],
    [.8,-116.85,32.51],
    [3.8,-108.48,18.08],
    [4.6,-74.66,-32.95],
    [6.3,0.66,-127.18],
    [7.9,-93.37,-22.42],
    [15.4,73.54,-162.98],
    [20.,-151.52,10.01],
    [354.8,-206.66,31.63],
    [100000.,np.nan,np.nan]])
    
  def __init__(self,ratio_nhnm=0.,units='ACC'):

    self.units='ACC'
    self.ratio=ratio_nhnm
      #self.calculate=_perterson
  
  def calculate(self,p):
    """ Implement it the slow way at the moment this could be linearized, but for now it 
    will work.  
    """
    p=np.asarray(p,dtype=np.float64)
    out=np.zeros(np.shape(p))
    self.nlnm=np.zeros(np.shape(p))
    self.nhnm=np.zeros(np.shape(p))
    for j, period in np.ndenumerate(p):
      for c in self._nlnm_coeff:
        if period >= c[0]:
          self.nlnm[j]=self._coef2psd(c,period)
       
    for j, period in np.ndenumerate(p):
      for c in self._nhnm_coeff:
        if period >= c[0]:
          self.nhnm[j]=self._coef2psd(c,period)
    #Don't do anymore work if we just want the NLNM
    if self.ratio==0.:
       return p,self.nlnm    
    #Don't do anymore work if we just want the NHNM
    if self.ratio==1.:
       return p,self.nhnm
     
     # Calculate the PSD for the combined model
     # This method of combining the NLNM & NHNM come from Adam Ringler
    out=self.ratio*self.nhnm+(1.-self.ratio)*self.nlnm
    return p,out
  
  def _coef2psd(self,coeff,period):  
    """ Given coefficients and a period calculate the correct noise PSD at a period not
    efficient as it will only work with all range of possible periods to apply the correct
    coefficients only operates with a single set of coefficients."""
    nm_psd=coeff[1]+coeff[2]*np.log10(period)
    if self.units=='VEL':
      nm_psd+=20.*np.log10(period/(2.*np.pi))
    if self.units=='DIS':
      nm_psd+=20.*np.log10((period**2)/((2.*np.pi)**2))
    return nm_psd
  
