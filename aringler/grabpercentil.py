#!/usr/bin/env python
import glob
import sys
from obspy.core import UTCDateTime
import numpy as np

debug = False

chan = 'BHZ'
pdfFiles = glob.glob('PDF*' + chan)
minfreq = 1./8.
maxfreq = 1./4.
stats = [10., 50., 90.,'mean']

fRes = open('Results' + str(int(1./maxfreq)) + 'to' + str(int(1./minfreq)) + chan,'w')
fRes.write('station, lat, lon, Start, End, ')
for stat in stats:
    if stat != 'mean':
        fRes.write(str(int(stat)) + ', ')
    else:
        fRes.write('mean \n')



vals = []
for pdfFile in pdfFiles:
    print('On the following station: ' + pdfFile)
    f = open(pdfFile,'r')
    goodpows = []
    goodfreqs = []
    sta = pdfFile.replace('PDF','')
    sta = sta.replace('.' + chan,'')
    fRes.write(sta + ', ')
    for idx, line in enumerate(f):
        if idx == 0:
            lat = float(line.replace('lat: ',''))
            fRes.write(str(lat) + ', ')
        elif idx == 1:
            lon = float(line.replace('long: ',''))
            fRes.write(str(lon) + ', ')
        elif idx == 3:
            try:
                stime = UTCDateTime(line.replace('# start=',''))
                fRes.write(str(stime.year) + '-' + str(stime.julday).zfill(3) + ', ')
            except:
                f.close()
                break
        elif idx == 4:
            etime = UTCDateTime(line.replace('# end=',''))
            fRes.write(str(etime.year) + '-' + str(etime.julday).zfill(3) + ', ')
        if idx > 6:
            line =line.strip()
            freq, power, hits = line.split(',')
            freq = float(freq)
            # If we have something in the period band grab it
            if (freq <= maxfreq) and (freq >= minfreq):
                hits = int(hits)
                power = int(power)
                goodpows += [power]*hits
                goodfreqs += [freq]*hits
            elif freq >= maxfreq:
                # We are now outside our frequency range
                # goodpows contains all the power values
                # goodfreqs contains the associated frequencies
                goodfreqs = np.asarray(goodfreqs)
                goodpows = np.asarray(goodpows)
                if debug:
                    print('Here are the powers')
                    print(goodpows)
                # Grab the unique frequencies
                uniquefreqs = list(set(goodfreqs))
                if debug:
                    print('Here are the unique frequencies')
                    print(uniquefreqs)
                df = np.diff(np.sort(uniquefreqs))
                if debug:
                    print('Here is df')
                    print(df)
                for stat in stats:
                    currentstat = []
                    for goodfreq in uniquefreqs:
                        if stat != 'mean':
                            currentstat.append(np.percentile(goodpows[(goodfreqs==goodfreq)], stat))
                        else:
                            currentstat.append(np.mean(goodpows[(goodfreqs==goodfreq)]))
                    if debug:
                        print('Here is currentstat')
                        print(currentstat)    
                    percentile = np.trapz(10**(np.asarray(currentstat)/10.),x=None, dx=df)
                    if debug:
                        print(df)
                        print(percentile)
                    percentile = 10.*np.log10(percentile)
                    if stat != 'mean':
                        fRes.write(str(percentile) + ', ')
                    else:
                        fRes.write(str(percentile) + ' \n')
                break
    f.close()
fRes.close()


