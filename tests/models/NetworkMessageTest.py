#!/usr/bin/python
# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|         01001110 01100101 01110100 01111010 01101111 01100010             | 
#+---------------------------------------------------------------------------+
#| NETwork protocol modeliZatiOn By reverse engineering                      |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @license      : GNU GPL v3                                                |
#| @copyright    : Georges Bossert and Frederic Guihery                      |
#| @url          : http://code.google.com/p/netzob/                          |
#| ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+
#| @author       : {gbt,fgy}@amossys.fr                                      |
#| @organization : Amossys, http://www.amossys.fr                            |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+ 
#| Standard library imports
#+---------------------------------------------------------------------------+
import unittest
from netzob.Common.Models.NetworkMessage import NetworkMessage
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+

class NetworkMessageTest(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_loadFromXml(self):
        
        id = str(uuid.uuid4()) 
        ipSource = "192.168.0.10"
        ipTarget = "192.168.0.20"
        protocol = "TCP"
        l4SourcePort = 5799
        l4TargetPort = 80
        strData = "NETwork protocol modeliZatiOn By reverse engineering"
        data = str(bytearray(strData)).encode('hex')
        
        xml = '''
        <message type="network" id="{0}">            
            <ipSource>{1}</ipSource>
            <ipTarget>{2}</ipTarget>
            <protocol>{3}</protocol>
            <l4SourcePort>{4}</l4SourcePort>
            <l4TargetPort>{5}</l4TargetPort>
            <data>{6}</data>
        </message>
        '''.format(id, ipSource, ipTarget, protocol, l4SourcePort, l4TargetPort, data)
        
        
        rootElement = ElementTree.XML(xml)
        self.message = NetworkMessage.loadFromXML(rootElement)
        
        self.assertEqual(id, self.message.getID())
        self.assertEqual(ipSource, self.message.getIPSource())
        self.assertEqual(ipTarget, self.message.getIPTarget())
        self.assertEqual(l4SourcePort, self.message.getL4SourcePort())
        self.assertEqual(l4TargetPort, self.message.getL4TargetPort())
        self.assertEqual(bytearray(strData.encode('hex')), self.message.getData())
        
   

