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
from netzob.Common.Models.FileMessage import FileMessage
from netzob.Common.Models.Factories.FileMessageFactory import FileMessageFactory
import uuid

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+

class FileMessageTest(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_loadFromXml(self):
        id = str(uuid.uuid4())
        filename = "fichierDeTest.txt"
        lineNumber = 1
        creationDate = "2011-12-01 18:01"
        modificationDate = "2011-12-01 18:02"
        owner = "netzob"
        size = "1000ko"
        strData = "NETwork protocol modeliZatiOn By reverse engineering"
        data = str(bytearray(strData)).encode('hex')
        
        message = FileMessage()
        message.setID(id)
        message.setLineNumber(lineNumber)
        message.setFilename(filename)
        message.setCreationDate(creationDate)
        message.setModificationDate(modificationDate)
        message.setOwner(owner)
        message.setSize(size)
        message.setData(data)
        
        outputXml = message.getFactory().saveInXML(message)
        
        rootElement2 = ElementTree.XML(outputXml)
        self.message2 = FileMessageFactory.loadFromXML(rootElement2)       
        
        self.assertEqual(id, self.message2.getID())
        self.assertEqual(lineNumber, self.message2.getLineNumber())
        self.assertEqual(filename, self.message2.getFilename())
        self.assertEqual(creationDate, self.message2.getCreationDate())
        self.assertEqual(modificationDate, self.message2.getModificationDate())
        self.assertEqual(owner, self.message2.getOwner())        
        self.assertEqual(size, self.message2.getSize())
        self.assertEqual(bytearray(strData.encode('hex')), self.message2.getData())
        
      
