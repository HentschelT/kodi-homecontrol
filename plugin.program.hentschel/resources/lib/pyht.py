# -*- coding: utf-8 -*-
# Licence: GPL v.3 http://www.gnu.org/licenses/gpl.html

from xml.dom.minidom import parseString
import urllib
import urllib2
from _warnings import once_registry


def open(host='hottub.home.hentschel.net', port='80'):
    out = htcontrol(host, port)
    if not out.Ping():
        out = dummy()

    return out


class htcontrol(object):
    __x10__ = {
        'all_off': 1,
        'all_on': 4,
        'on': 3,
        'off': 11,
        'bright': 7,
        'dim': 15}

    __dummy__ = False

    def __init__(self, host='hottub.home.hentschel.net', port='80'):
        self._host = host
        self._port = port

        self.Connect()

    def Connect(self):
        # create connection to ISY
        url = self._BaseURL()

    def Ping(self):
        try:
            theurl = self._BaseURL()
            #normalize the URL
            theurl = urllib.quote(theurl, safe="%/:=&?~#+!$,;'@()*[]")
            self._SendGetRequest(theurl)
            return True
        except urllib2.URLError:
            return False

    def _BaseURL(self):
        url = 'http://'
        url += self._host + ':' + str(self._port) + '/htmobile/rest/hottub/'
        return url

    def _SendGetRequest(self, url):
        try:
            pagehandle = urllib2.urlopen(url)
        except urllib2.HTTPError:
            self.Connect()
            pagehandle = urllib2.urlopen(url)

        data = pagehandle.read()
        pagehandle.close()
        return data

    def _SendPutRequest(self, url):
        method = 'PUT'
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)
        request = urllib2.Request(url, data=None )
        request.get_method = lambda: method

        connection = opener.open(request)
        data = connection.read()
        connection.close()
        return data

    def setPump(self, on=False):
        theurl = self._BaseURL() + 'pump/'
        if on is True:
            theurl += 'ON'
        else:
            theurl += 'OFF'
        theurl = urllib.quote(theurl, safe="%/:=&?~#+!$,;'@()*[]")
        self._SendPutRequest(theurl)
        
    def setBlower(self, on=False):
        theurl = self._BaseURL() + 'blower/'
        if on is True:
            theurl += 'ON'
        else:
            theurl += 'OFF'
        theurl = urllib.quote(theurl, safe="%/:=&?~#+!$,;'@()*[]")
        self._SendPutRequest(theurl)
        
    def setTemp(self, value):
        theurl = self._BaseURL() + 'setpoint/' + str(value)
        theurl = urllib.quote(theurl, safe="%/:=&?~#+!$,;'@()*[]")
        self._SendPutRequest(theurl)
        
    def getStatus(self):
        theurl = self._BaseURL();
        theurl = urllib.quote(theurl, safe="%/:=&?~#+!$,;'@()*[]")
        data = self._SendGetRequest(theurl)
        return self._parseStateXML(data)

    def _parseStateXML(self, data):
        try:
            dom = parseString(data)
        except:
            data += '>'   # sometimes the xml is missing the closing bracket
            dom = parseString(data)

        child_dict = {}
        elements = dom.getElementsByTagName('hottub')[0]
        blower = elements.getElementsByTagName('blower')[0]
        heater = elements.getElementsByTagName('heater')[0]
        pump = elements.getElementsByTagName('pump')[0]
        setpoint = elements.getElementsByTagName('setpoint')[0]
        temperature = elements.getElementsByTagName('temperature')[0]
        
        child_dict['blower'] = blower.attributes['state'].value
        child_dict['heater'] = heater.attributes['state'].value
        child_dict['pump'] = pump.attributes['state'].value
        child_dict['setpoint'] = setpoint.attributes['value'].value
        child_dict['temperature'] = temperature.attributes['value'].value

        return child_dict

class dummy(object):

    __dummy__ = True

    def __init__(self, *kargs, **kwargs):
        pass

    def Connect(self):
        pass

    def Ping(self):
        return True

    def setPump(self, on=False):
        pass

    def setBlower(self, on=False):
        pass

    def setTemp(self, value):
        pass

    def getStatus(self):
        return   {'blower' : 'OFF',
                  'heater' : 'OFF',
                  'pump'   : 'OFF',
                  'setpoint' : '80',
                  'temperature' : '90'}
