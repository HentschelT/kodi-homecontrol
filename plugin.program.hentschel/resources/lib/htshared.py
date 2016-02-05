# -*- coding: utf-8 -*-
# Licence: GPL v.3 http://www.gnu.org/licenses/gpl.html

import pyht
import htshared as self
import urls
import xbmc
import xbmcaddon

# addon classes
browser = None

# connection to ISY controller
htcontroller = None

# runtime parameters
__path__ = ''
__params__ = {}
__id__ = -1

# function shortcuts
translate = None

# common paths
__lib__ = ''


def initialize():
    '''
    initialize()

    DESCRIPTION:
    This function initialize the shared variable library.
    The only input to this function is the program's
    system arguments.  There is no output.
    '''
    # get this addon
    self.browser = xbmcaddon.Addon('plugin.program.hentschel')

    # get plugin information
    self.translate = self.browser.getLocalizedString

    # get common file paths
    self.__lib__ = self.browser.getAddonInfo('path') + '/resources/lib/'

    # connect to htcontroller
    host = self.browser.getSetting('host')
    port = int(self.browser.getSetting('port'))
    self.htcontroller = pyht.open(host, port)

    # verify htcontroller opened correctly
    if self.htcontroller.__dummy__:
        header = self.translate(30501)
        message = self.translate(30502)
        xbmc.executebuiltin('Notification(' + header + ','
                            + message + ', 15000)')
    return self.htcontroller
