#!/usr/bin/env python

from obspy.xseed import Parser
import requests
import sys

from obspy.fdsn import Client

nets = ['CI', 'US', 'IU', 'II', 'TA']
for net in nets:
    client = Client("IRIS")
    inventory = client.get_stations(network=net)

    stas = inventory[0]


    for idx, sta in enumerate(stas):

        print('On station: ' + str(idx+ 1) + ' of ' + str(len(stas)))

            # for each station grab the MUSTANG PDF and save it
            
        for chan in ['BHN', 'BHE', 'BHZ', 'LHZ','LHN','LHE','LH1','LH2']:
            try:
                string = "http://service.iris.edu/mustang/noise-pdf/1/query?target="
                string += net + '.' + sta.code + '..' + chan + '.M&format=text'
                r = requests.get(string)
                f = open('PDF' + sta.code + '.' + chan , 'w')
                f.write('lat: ' + str(sta.latitude) + '\n')
                f.write('long: ' + str(sta.longitude) + '\n')
                f.write(r.text)
                f.close()
            except:
                print('Problem with : ' + sta.code + ' ' + chan)
        
        
    
    
