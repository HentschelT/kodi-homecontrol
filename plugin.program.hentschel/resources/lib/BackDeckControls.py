# -*- coding: utf-8 -*-
# Licence: GPL v.3 http://www.gnu.org/licenses/gpl.html


import sys
import os
import xbmc, xbmcaddon, xbmcgui
from pyxbmct.addonwindow import *

# custom path
lib_path = xbmcaddon.Addon('plugin.program.isybrowse').getAddonInfo('path') + '/resources/lib/'
sys.path.append(lib_path)
import shared as isyshared

import htshared as htshared
import pyht
import urls

_mintemp = 94
_maxtemp = 104
_difftemp = _maxtemp - _mintemp
_scaletemp = 100/_difftemp

_isyfolder = '15813'
_isyNames = ['Deck-Outer',
             'Deck-Inner', 
             'Sideyard-Lights', 
             'Front Porch', 
             'Fountain-Outside']

_isyProperties = {
             _isyNames[0] : ['Deck-Outer-Inline'], 
             _isyNames[1] : ['Deck-Inner-Inline'], 
             _isyNames[2] : ['Outlet-Sideyard-Lights'], 
             _isyNames[3] : ['Hallway-6-Way-Front-Porch'], 
             _isyNames[4] : ['Outlet-Fountain-Back']
             }

rows = 7
colums = 9
firstcol = 0
secondcol = 5
controlspanx = 3

class BackDeckControls():

    def __init__(self, window):
        self.window = window
        self.htcontroller = htshared.initialize()

        # only get nodes from the 'outdoor' folder
        args = ['plugin://plugin.program.isybrowse/','4','?addr='+ _isyfolder + '&browsing=nodes&type=folder']
        isyshared.initialize(args)
        self.isy = isyshared.isy
        self.nodes = self.isy.BrowseNodes(_isyfolder)
        xbmc.log('nodes:' + str(self.nodes))
        
    def getColumns(self):
        return colums
    
    def getRows(self):
        return rows
        
    def set_active_controls(self):
        
        self.window.placeControl(Label('[COLOR orange][B]Lights[/B][/COLOR]'), 0, firstcol + 2, 1, controlspanx + 1)
        
        name = _isyNames[0]
        self.deckOuterButton = RadioButton(name)
        self.window.placeControl(self.deckOuterButton, 1, firstcol, 1, controlspanx + 1)
        value = self.nodes[_isyProperties[name][0]][2]
        self.deckOuterButton.setSelected( int(value) > 0 )
        self.window.connect(self.deckOuterButton, self.deckOuter_update)

        name = _isyNames[1]
        self.deckInnerButton = RadioButton(_isyNames[1])
        self.window.placeControl(self.deckInnerButton, 2, firstcol, 1, controlspanx + 1)
        value = self.nodes[_isyProperties[name][0]][2]
        self.deckInnerButton.setSelected( int(value) > 0 )
        self.window.connect(self.deckInnerButton, self.deckInner_update)

        name = _isyNames[2]
        self.sideDeckButton = RadioButton(name)
        self.window.placeControl(self.sideDeckButton, 3, firstcol, 1, controlspanx + 1)
        value = self.nodes[_isyProperties[name][0]][2]
        self.sideDeckButton.setSelected( int(value) > 0 )
        self.window.connect(self.sideDeckButton, self.sideDeck_update)

        name = _isyNames[3]
        self.frontPorchButton = RadioButton(name)
        self.window.placeControl(self.frontPorchButton, 4, firstcol, 1, controlspanx + 1)
        value = self.nodes[_isyProperties[name][0]][2]
        self.frontPorchButton.setSelected( int(value) > 0 )
        self.window.connect(self.frontPorchButton, self.frontPorch_update)

        name = _isyNames[4]
        self.fountainButton = RadioButton(name)
        self.window.placeControl(self.fountainButton, 5, firstcol, 1, controlspanx + 1)
        value = self.nodes[_isyProperties[name][0]][2]
        self.fountainButton.setSelected( int(value) > 0 )
        self.window.connect(self.fountainButton, self.fountain_update)

        #
        data = self.htcontroller.getStatus()
        pumpState = False
        if( data['pump'] == 'ON' ):
            pumpState = True
            
        blowerState = False
        if( data['blower'] == 'ON' ):
            blowerState = True
            
        heaterState = False
        if( data['heater'] == 'ON' ):
            heaterState = True
            
        setpointValue = "%.1f" % float(data ['setpoint'])
        temperatureValue = "%.1f" % float(data ['temperature'])
        
        self.window.placeControl(Label('[COLOR orange][B]Hot Tub[/B][/COLOR]'), 0, secondcol + 1, 1, controlspanx + 1)

        temp_caption = Label('Temperature')
        self.window.placeControl(temp_caption, 1, secondcol, 1, controlspanx)

        self.currenttemp_value = Label(temperatureValue, alignment=ALIGN_CENTER)
        self.window.placeControl(self.currenttemp_value, 1, secondcol + controlspanx)

        # Slider
        captiontext = "Heater " 
        if (heaterState == True):
            captiontext += "On "
        else:
            captiontext += "Off"
            
        self.setpointlabel = Label(captiontext)
        self.window.placeControl(self.setpointlabel, 2, secondcol, 1, controlspanx)

        self.setpoint_value = Label(setpointValue, alignment=ALIGN_CENTER)
        self.window.placeControl(self.setpoint_value, 2, secondcol + controlspanx)

        self.tempslider = Slider()
        self.window.placeControl(self.tempslider, 3, secondcol, 1, controlspanx + 1, pad_y=10)
        tempslidervalue = (float(setpointValue) - _mintemp) * _scaletemp
        self.tempslider.setPercent(tempslidervalue)
        # Connect key and mouse events for tempslider update feedback.
        self.window.connectEventList([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT, ACTION_MOUSE_DRAG], self.tempslider_update)
        #
        pumpCaption = 'Pump Off'
        if(pumpState == True):
            pumpCaption = 'Pump On '
            
        self.pumpbutton = RadioButton(pumpCaption)
        self.window.placeControl(self.pumpbutton, 4, secondcol, 1, controlspanx + 1)
        self.window.connect(self.pumpbutton, self.pump_update)
        self.pumpbutton.setSelected( pumpState )
        
        blowerCaption = 'Blower Off'
        if(blowerState == True):
            blowerCaption = 'Blower On '

        self.blowerbutton = RadioButton(blowerCaption)
        self.window.placeControl(self.blowerbutton, 5, secondcol, 1, controlspanx + 1)
        self.window.connect(self.blowerbutton, self.blower_update)
        self.blowerbutton.setSelected(blowerState)

    def set_navigation(self):
        # Set initial focus
        self.window.setFocus(self.deckOuterButton)
        # Set navigation between controls
        # left colum
        self.deckOuterButton.controlUp(self.fountainButton)
        self.deckOuterButton.controlDown(self.deckInnerButton)
        self.deckInnerButton.controlUp(self.deckOuterButton)
        self.deckInnerButton.controlDown(self.sideDeckButton)
        self.sideDeckButton.controlUp(self.deckInnerButton)
        self.sideDeckButton.controlDown(self.frontPorchButton)
        self.frontPorchButton.controlUp(self.sideDeckButton)
        self.frontPorchButton.controlDown(self.fountainButton)
        self.fountainButton.controlUp(self.frontPorchButton)
        self.fountainButton.controlDown(self.deckOuterButton)
        
        #right colum
        self.tempslider.controlUp(self.blowerbutton)
        self.tempslider.controlDown(self.pumpbutton)
        self.pumpbutton.controlUp(self.tempslider)
        self.pumpbutton.controlDown(self.blowerbutton)
        self.blowerbutton.controlUp(self.pumpbutton)
        self.blowerbutton.controlDown(self.tempslider)
        
        # in between colums
        self.deckOuterButton.controlRight(self.tempslider)
        self.deckInnerButton.controlRight(self.tempslider)
        self.sideDeckButton.controlRight(self.tempslider)
        self.frontPorchButton.controlRight(self.pumpbutton)
        self.fountainButton.controlRight(self.blowerbutton)
        
#        self.tempslider.controlLeft(self.sideDeckButton)
        self.pumpbutton.controlLeft(self.frontPorchButton)
        self.blowerbutton.controlLeft(self.fountainButton)
        

    def getDeviceAddress(self, sceneName):
        return self.nodes[_isyProperties[sceneName][0]][1]
    
    def deckOuter_update(self):
        addr = self.getDeviceAddress(_isyNames[0])
        if self.deckOuterButton.isSelected():
            self.isy.NodeOn(addr)
        else:
            self.isy.NodeOff(addr)

    def deckInner_update(self):
        addr = self.getDeviceAddress(_isyNames[1])
        if self.deckInnerButton.isSelected():
            self.isy.NodeOn(addr)
        else:
            self.isy.NodeOff(addr)

    def sideDeck_update(self):
        addr = self.getDeviceAddress(_isyNames[2])
        if self.sideDeckButton.isSelected():
            self.isy.NodeOn(addr)
        else:
            self.isy.NodeOff(addr)

    def frontPorch_update(self):
        addr = self.getDeviceAddress(_isyNames[3])
#        xbmc.log('Front update: setting |' + str(addr) + '| to ' + str(self.frontPorchButton.isSelected()))
        if self.frontPorchButton.isSelected():
            self.isy.NodeOn(addr)
        else:
            self.isy.NodeOff(addr)

    def fountain_update(self):
        addr = self.getDeviceAddress(_isyNames[4])
        if self.fountainButton.isSelected():
            self.isy.NodeOn(addr)
        else:
            self.isy.NodeOff(addr)

    def tempslider_update(self):
        # Update tempslider value label when the tempslider nib moves
#        try:
        if self.window.getFocus() == self.tempslider:
            value = self.tempslider.getPercent()/_scaletemp + _mintemp
            self.setpoint_value.setLabel('%.1f' % ( value ))
            self.htcontroller.setTemp(value)
        else:
            xbmc.log('ht debug: slider update w/o focus', level=xbmc.LOGNOTICE)
#        except (RuntimeError, SystemError):
#            xbmc.log(msg='slider update failed')

    def pump_update(self):
        # Update pumpbutton caption on toggle
        if self.pumpbutton.isSelected():
            self.pumpbutton.setLabel('Pump On ')
            self.htcontroller.setPump(True)
            self.setpointlabel.setLabel("Heater On ")
        else:
            self.pumpbutton.setLabel('Pump Off')
            self.htcontroller.setPump(False)
            self.setpointlabel.setLabel("Heater Off")

    def blower_update(self):
        # Update pumpbutton caption on toggle
        if self.blowerbutton.isSelected():
            self.blowerbutton.setLabel('Blower On ')
            self.htcontroller.setBlower(True)
        else:
            self.blowerbutton.setLabel('Blower Off')
            self.htcontroller.setBlower(False)
