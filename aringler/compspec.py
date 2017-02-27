#!/usr/bin/env python

import matplotlib.pyplot as plt
from obspy.geodetics import degrees2kilometers
from obspy.signal.spectral_estimation import get_nlnm, get_nhnm
import numpy as np
from obspy.signal.invsim import paz_to_freq_resp

import matplotlib as mpl
mpl.rc('font',family='serif')
mpl.rc('font',serif='Times') 
mpl.rc('text', usetex=False)
mpl.rc('font',size=12)

# Acceleration, velocity or displacement
n=2.

# Magnitude
Mw=3.3

# Attenuation at 24.4 km from prem
Qmu=600.
Qk=57823.

# Density in g /m^3 from source and receiver at 24.4 km
rhos = 2.9*10**6
rhor=1.02*10**6

# Distance in degrees to meters
deg = 1.
Rrs = degrees2kilometers(deg)*1000.
Rrs = 13.2*1000.

# Velocity of P-waves 
vpr =1.45*1000. # At receiver
vps=6.8*1000. # At source
vss=3.9*1000. # At source

# Quality Factor from Shearer
L=(4./3.)*(vpr/vss)**2
Qinv=L*(1./Qmu)+(1.-L)*(1./Qk)
Q= 1./Qinv

# Seismic Moment
M0=10.**((Mw+10.7)*(3./2.))

# N-m
M0=(M0/(10**5))*.01
print("Moment: %g" % (M0))
perNLNM, NLNM = get_nlnm()
perNHNM, NHNM = get_nhnm()

# Make a vector of frequency
sampling_rate = 1000.
lenfft = 10000
freq = np.fft.rfftfreq(lenfft, d=1./sampling_rate)
#freq = np.array([.0001, .001,.05,1.,4.,6.,8.])
#freq = freq[1:]
# Source radiation 
F=1.

# Page 149 of Nolet's book
#AE= F/(4.*np.pi*(rhos*vpr*vps**5)**.5)
AE=1./Rrs
# Add attenuation
AE = AE *np.exp(-2.*np.pi*freq*Rrs/(Q*(vpr*vps)**.5))



# Now we want to add in the source term

# Stress drop
sigma0= 5.*1.e6

# Equation B7 from Seismic Network Evaluation through Simulation
R0 = (7.*M0/(16.*sigma0))**(1./3.)

Kp =2.

# Corner frequency from B8 in previous paper
f0= Kp*vps/(2.*np.pi*R0)
print("Corner F %f" %(f0))

gamma = 2.

# Equation B2 from Seismic Network Evaluation through Simulation
print(str(rhos),str(vps))
Cs=F/(4.*np.pi*rhos*(vpr*vps**5)**.5)
print("Cs %g" % (Cs))
#print((2.*np.pi*1.)**n)/(1.+(2.*np.pi*1./(2.*np.pi*f0))**gamma)
AS = M0*((2.*np.pi*freq)**n)/(1.+(2.*np.pi*freq/(2.*np.pi*f0))**gamma)*Cs


# Now convert to dB relative to (m/s^2)/Hz
A = 10.*np.log10(((AS*AE)**2)/freq)
#A = 10.*np.log10(((AS)**2)/freq)


# Why not add an error for no episensor response
# paz = {'poles': [-981. + 1009j, -981. - 1009j , -3290.+1263j, -3290.-1263j], 'gain': 2.45956*10**13}
# 
# New A with no response removed
# resp = 1.
# for pole in paz['poles']:
#     resp *=1./(2.*np.pi*pole-freq)
#    
# resp = resp/resp[1]    
# Aerr = 10.*np.log10(((AS*AE*(resp) )**2)/freq)
# 
# 
# 
# 
# 
# We can do the same thing for an STS-1 response
# paz2 = {'gain': 3948.58, 'zeros': [0, 0], 'poles': [-0.01234 - 0.01234j,  
#             -0.01234 + 0.01234j, -39.18 - 49.12j, -39.18 + 49.12j],
#             'sensitivity': 3.3554432*10**9}
#             
# respval = paz_to_freq_resp(paz2['poles'],paz2['zeros'],paz2['sensitivity'],t_samp = 1./sampling_rate, 
# 		nfft=lenfft,freq = False)
# respval = np.absolute(respval*np.conjugate(respval))
# respval = respval[1:]
# respval = respval/respval[1]    
# AerrSTS1 = 10.*np.log10(((AS*AE*(respval) )**2)/freq)



fig = plt.figure(1)

plt.semilogx(perNLNM, NLNM, label='NLNM/NHNM', color='.7', linewidth=2.)
plt.semilogx(perNHNM, NHNM, color='.7', linewidth=2.)
plt.semilogx(1./freq, A, label='Brune Spectra Mw=' + str(Mw) + ' at ' + str(Rrs/1000.) + ' km' )
# plt.semilogx(1./freq,10.*np.log10(((AE)**2)/freq),label='Att')
# plt.semilogx(1./freq,10.*np.log10(((AS)**2)/freq),label='Source')
plt.legend()
plt.xlabel('Period (s)')

plt.ylabel('Power (dB rel. 1 $(m/s^2)^2/Hz)$')


fig.tight_layout()
plt.show()
