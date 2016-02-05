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
from ThermostatControl import ThermostatControl

_isyfolder = '26883'
_isyNames = ['Living Room',
             'Movie', 
             'Plant Lights', 
             'Bar', 
             'Hallway', 
             'Corner Lamp']

_isyProperties = {
             _isyNames[0] : ['Living-Room'], 
             _isyNames[1] : ['Living-Room'], 
             _isyNames[2] : ['Plant-Lights'], 
             _isyNames[3] : ['Bar-Dimmer'], 
             _isyNames[4] : ['Hallway-Lights'], 
             _isyNames[5] : ['Corner Lamp Applinc']
             }
rows = len(_isyNames) + 1
colums = 9
firstcol = 0
secondcol = 5
controlspanx = 3


class LivingRoomControls():

    def __init__(self, window):
        self.window = window

        # only get nodes from the 'downstairs' folder
        args = ['plugin://plugin.program.isybrowse/','4','?addr='+ _isyfolder + '&browsing=nodes&type=folder']
        isyshared.initialize(args)
        self.isy = isyshared.isy
        self.nodes = self.isy.BrowseNodes(_isyfolder)
        xbmc.log('nodes:' + str(self.nodes))
        self.buttons = {}
        
    def getColumns(self):
        return colums
    
    def getRows(self):
        return rows
        
    def set_active_controls(self):
        
        row = 0
        self.window.placeControl(Label('[COLOR orange][B]Lights[/B][/COLOR]'), row, firstcol + 2, 1, controlspanx + 1)

        for name in _isyNames:
            button = RadioButton(name)
            row += 1
            self.window.placeControl(button, row, firstcol, 1, controlspanx + 1)
            value = self.getDeviceValue(name)
            button.setSelected( int(value) > 0 )
            self.buttons[name] = (button)
            callback = lambda name = name : self.handler(name)
            self.window.connect(button, callback)
        
        self.window.placeControl(Label('[COLOR orange][B]Thermostat[/B][/COLOR]'), 0, secondcol + 1, 1, controlspanx + 1)
        self.thermostatControls = self.addThermostatControl(1, secondcol)

    def addThermostatControl(self, row, col):
        controls = {}
        self.thermostat = ThermostatControl(self)
        controls = self.thermostat.initThermostatControls(row, col)
        return controls

    def set_navigation(self):
        # Set initial focus
        self.window.setFocus(self.buttons[_isyNames[0]])
        # Set navigation between controls
        # left colum
        for num in range(0, len(_isyNames)):
            name1 = _isyNames[num]
            if num + 1 == len(_isyNames):
                name2 = _isyNames[0]
            else:
                name2 = _isyNames[num + 1]
                         
            button1 = self.buttons[name1]
            button2 = self.buttons[name2]
            button1.controlDown(button2)
            button2.controlUp(button1)
            
        self.buttons[_isyNames[0]].controlRight(self.thermostatControls['coolset'])
        self.buttons[_isyNames[1]].controlRight(self.thermostatControls['coolset'])
        self.buttons[_isyNames[2]].controlRight(self.thermostatControls['coolset'])
        self.buttons[_isyNames[3]].controlRight(self.thermostatControls['coolset'])
#        self.buttons[_isyNames[3]].controlRight(self.thermostatControls['fanset'])
        self.thermostatControls['coolset'].controlLeft(self.buttons[_isyNames[2]])
#        self.thermostatControls['fanset'].controlLeft(self.buttons[_isyNames[3]])

    def getSceneAddress(self, sceneName):
        return self.nodes[sceneName][1]

    def getDeviceAddress(self, sceneName):
        return self.nodes[_isyProperties[sceneName][0]][1]
    
    def getDeviceValue(self, sceneName):
        return self.nodes[_isyProperties[sceneName][0]][2]
    
    def handler(self, name):
        addr = self.getSceneAddress(name)
        selected = self.buttons[name].isSelected()
        xbmc.log('handler invoked with: ' + str(name) + ", addr is " + str(addr) + ", selected is " + str(selected))
        if self.buttons[name].isSelected():
            self.isy.NodeOn(addr)
        else:
            self.isy.NodeOff(addr)

