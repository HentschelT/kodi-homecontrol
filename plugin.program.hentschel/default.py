# -*- coding: utf-8 -*-
# Licence: GPL v.3 http://www.gnu.org/licenses/gpl.html
# This is an XBMC addon for demonstrating the capabilities
# and usage of PyXBMCt framework.

import sys
import os
import xbmc, xbmcaddon, xbmcgui
from pyxbmct.addonwindow import *

# custom path
lib_path = xbmcaddon.Addon('plugin.program.hentschel').getAddonInfo('path') + '/resources/lib/'
sys.path.append(lib_path)

from BackDeckControls import *
from LivingRoomControls import *
from GarageControls import *
from BedRoomControls import *
from LoftControls import *
from GuestBedroomControls import *

controller = None
controls = {'Back Deck': 'BackDeckControls', 
            'Living Room' : 'LivingRoomControls',
            'Bed Room': 'BedRoomControls',
            'Guest Bed Room': 'GuestBedroomControls',
            'Garage': 'GarageControls',
            'Loft': 'LoftControls'}

class HomeControl(AddonDialogWindow):

    def __init__(self, title=''):
        super(HomeControl, self).__init__(title)
        # get this addon
        self.browser = xbmcaddon.Addon('plugin.program.hentschel')
        
        # instantiate the correct controls class based on where we are
        locationName = self.browser.getSetting('location')
        location = controls[locationName]
        clazz = globals()[location]
        self.controls = clazz(self)
        
        rows = self.controls.getRows()
        cols = self.controls.getColumns()
        if cols < 1:
            cols = 1

        self.setGeometry(cols * 75, rows * 75, rows, cols)
        
        self.setWindowTitle(locationName)
        self.controls.set_active_controls();

        # Connect a key action (Backspace) to close the window.
        self.connect(ACTION_NAV_BACK, self.close)
        
        self.controls.set_navigation()


    def setAnimation(self, control):
        # Set fade animation for all add-on window controls
        control.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=200',),
                                ('WindowClose', 'effect=fade start=100 end=0 time=500',)])

def main():
    window = HomeControl('Home Control')
    window.doModal()

if __name__ == '__main__':
    main()
