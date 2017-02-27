#!/usr/bin/env python
import numpy as np

import matplotlib.mlab as ml
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt


debug = True

jet = plt.cm.get_cmap('jet')



m = Basemap(projection='merc',llcrnrlat=20,urcrnrlat=50,\
            llcrnrlon=-130,urcrnrlon=-60,lat_ts=20,resolution='i')
m.drawcoastlines()
m.drawcountries()
m.drawstates()
#m.drawstates()
# draw parallels and meridians.
#parallels = np.arange(-90.,91.,5.)
# Label the meridians and parallels
#m.drawparallels(parallels,labels=[False,True,True,False])
# Draw Meridians and Labels
#meridians = np.arange(-180.,181.,10.)
#m.drawmeridians(meridians,labels=[True,False,False,True])
#m.drawmapboundary(fill_color='white')



f = open('Results4to8BHZ','r')
lats = []
lons = []
means =[]
for idx, line in enumerate(f):
    if idx > 0:

        lats.append(float(line.split(',')[1]))
        lons.append(float(line.split(',')[2]))
        means.append(float(line.split(',')[6]))
f.close()
means = np.asarray(means)
lats = np.asarray(lats)
lons = np.asarray(lons)

goodmeans = []
goodlats =[]
goodlons =[]

for triple in zip(means, lats, lons):
    if (triple[0] > np.mean(means) + 22.*np.std(means)) or (triple[0] < np.mean(means) - 22.*np.std(means)):
        pass
    elif triple[1] > 50.:
        pass
    else:
        goodmeans.append(triple[0])
        goodlats.append(triple[1])
        goodlons.append(triple[2])

means = goodmeans
lats= goodlats
lons = goodlons


if debug:
    print(lats)
    print(lons)
    print(means)
    
    

latsG =np.linspace(min(lats),max(lats),200)
lonsG = np.linspace(min(lons), max(lons),200)
print(min(lons))


if debug:
    print('New lats')
    print(latsG)
    print('New lons')
    print(lonsG)

LONS, LATS = np.meshgrid(lonsG, latsG)

MEANS = ml.griddata(lons, lats, means, lonsG, latsG, interp='linear')

for mean in MEANS:
    print(mean)

x,y = m(LONS, LATS)
sc = plt.pcolor(x, y ,MEANS, cmap=jet)
cbar = plt.colorbar(sc)
plt.clim((np.mean(means)-3.*np.std(means), np.mean(means)+3.*np.std(means)))
#plt.xlim((-130, -70))



















plt.show()
