# -*- coding: utf-8 -*-
# Licence: GPL v.3 http://www.gnu.org/licenses/gpl.html

import sys
import os
import xbmc, xbmcaddon, xbmcgui
from pyxbmct.addonwindow import *

from xml.dom.minidom import parseString
import urllib
import urllib2

class ThermostatControl():

    def __init__(self, parent):
        self.parent = parent
        self.addr = '14 23 AC 1'
        self.isy = parent.isy
        self.window = parent.window

        
    def getThermostatData(self):
        theurl = self.isy._BaseURL() + 'rest/nodes/' + self.addr.replace(' ', '%20')
        #normalize the URL
        theurl = urllib.quote(theurl, safe="%/:=&?~#+!$,;'@()*[]")
        data = self.isy._SendRequest(theurl)

        dom = parseString(data)
        node = dom.getElementsByTagName('node')[0]
        properties = node.getElementsByTagName('property')
        result = {}
        for property in properties:
            id = property.attributes['id'].value
            value = property.attributes['formatted'].value
            result[id] = value

        xbmc.log('thermostat properties: ' + str(result))
        return result
    
    def addThermoListControl(self, labeltext, row, col, trange, current, callback):
        list_label = Label(labeltext)
        self.window.placeControl(list_label, row, col, 1, 2)
        list = List()
        self.window.placeControl(list, row + 1, col, 1, 2)
        items = [' {0}'.format(i) for i in trange]
        list.addItems(items)
        list.selectItem(int(float(current)) - int(trange[0]))
        # Connect the list to a function to display which list item is selected.
        self.window.connect(list, lambda: callback (list.getListItem(list.getSelectedPosition()).getLabel()))
        return list
                
    def initThermostatControls(self, row, col):
        spanx = 3
        controls = {}
        data = self.getThermostatData()
        
        caption = Label('Temperature')
        self.window.placeControl(caption, row, col, 1, spanx)

        currenttemp_value = Label(data['ST'] + "F")
        self.window.placeControl(currenttemp_value, row, col + 2)
        
        heatset = data['CLISPH']
        coolset = data['CLISPC']
        
        controls['coolset'] = self.addThermoListControl('Cool Set', row + 1, col, range(76, 86), coolset, self.coolAdjustCallback)
        controls['heatset'] = self.addThermoListControl('Heat Set', row + 1, col + 2, range(70, 76), heatset, self.heatAdjustCallback)
        
#        button = RadioButton('Fan')
#        self.window.placeControl(button, row + 3, col, 1, 3)
#        button.setSelected( 0 )
#        controls['fanset'] = button
#        callback = lambda button = button : self.fanAdjustCallback(button)
#        self.window.connect(button, callback)

#        controls['coolset'].controlLeft(controls['fanset'])
        controls['coolset'].controlRight(controls['heatset'])
        controls['heatset'].controlLeft(controls['coolset'])
#        controls['heatset'].controlRight(controls['fanset'])
#        controls['fanset'].controlUp(controls['heatset'])
#        controls['fanset'].controlDown(controls['coolset'])
        
        return controls
    
    def heatAdjustCallback(self, value):
        xbmc.log('thermostat adjusting heat: ' + str(value))
        adjusted = int(value) * 2
        theurl = self.isy._BaseURL() + 'rest/nodes/' + self.addr.replace(' ', '%20') + '/cmd/CLISPH/' + str(adjusted)
        #normalize the URL
        theurl = urllib.quote(theurl, safe="%/:=&?~#+!$,;'@()*[]")
        data = self.isy._SendRequest(theurl)
        xbmc.log('thermostat adjusting heat reply: ' + str(data))
    
    def coolAdjustCallback(self, value):
        xbmc.log('thermostat adjusting cool: ' + str(value))
        adjusted = int(value) * 2
        theurl = self.isy._BaseURL() + 'rest/nodes/' + self.addr.replace(' ', '%20') + '/cmd/CLISPC/' + str(adjusted)
        #normalize the URL
        theurl = urllib.quote(theurl, safe="%/:=&?~#+!$,;'@()*[]")
        data = self.isy._SendRequest(theurl)
        xbmc.log('thermostat adjusting cool reply: ' + str(data))
        
    def fanAdjustCallback(self, button):
        xbmc.log('thermostat adjusting fan: ' + str(button.isSelected()))
        
