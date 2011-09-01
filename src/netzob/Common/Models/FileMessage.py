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
import logging.config

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+
from xml.etree import ElementTree

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from .. import ConfigurationParser
from .AbstractMessage import AbstractMessage
from Factories.FileMessageFactory import FileMessageFactory

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| FileMessage :
#|     Definition of a file message
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class FileMessage(AbstractMessage):
    def __init__(self):
        AbstractMessage.__init__(self, "File")
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.Models.FileMessage.py')
    
    #+-----------------------------------------------------------------------+
    #| getFactory
    #| @return the associated factory
    #+-----------------------------------------------------------------------+
    def getFactory(self):
        return FileMessageFactory
        
    #+---------------------------------------------- 
    #| GETTERS : 
    #+----------------------------------------------
    def getLineNumber(self):
        return self.lineNumber
    def getFilename(self):
        return self.filename
    def getCreationDate(self):
        return self.creationDate
    def getModificationDate(self):
        return self.modificationDate
    def getOwner(self):
        return self.owner
    def getSize(self):
        return self.size
       
    #+---------------------------------------------- 
    #| SETTERS : 
    #+----------------------------------------------
    def setLineNumber(self, lineNumber):
        try :
            self.lineNumber = int(lineNumber)
        except :
            self.log.warning("Impossible to set the given line number since its not an int !")
    def setFilename(self, filename):
        self.filename = filename
    def setCreationDate(self, creationDate):
        self.creationDate = creationDate
    def setModificationDate(self, modificationDate):
        self.modificationDate = modificationDate
    def setOwner(self, owner):
        self.owner = owner
    def setSize(self, size):
        self.size = size
  

