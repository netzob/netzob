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
import logging

#+---------------------------------------------------------------------------+
#| Related third party imports
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Models.AbstractMessage import AbstractMessage
from netzob.Common.Models.Factories.FileMessageFactory import FileMessageFactory


#+---------------------------------------------------------------------------+
#| FileMessage :
#|     Definition of a file message
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class FileMessage(AbstractMessage):
    def __init__(self, id, timestamp, data, filename, creationDate, modificationDate, owner, size, lineNumber):
        AbstractMessage.__init__(self, id, timestamp, data, "File")
        self.filename = filename
        self.creationDate = creationDate
        self.modificationDate = modificationDate
        self.owner = owner
        self.size = size
        self.lineNumber = lineNumber
        
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.Models.FileMessage.py')
    
    #+-----------------------------------------------------------------------+
    #| getFactory
    #| @return the associated factory
    #+-----------------------------------------------------------------------+
    def getFactory(self):
        return FileMessageFactory
    
    #+-----------------------------------------------------------------------+
    #| getProperties
    #|     Computes and returns the properties of the current message
    #| @return an array with all the properties [[key,val],...]
    #+-----------------------------------------------------------------------+
    def getProperties(self):
        properties = []        
        properties.append(['ID', str(self.getID())])
        properties.append(['Type', self.getType()])
        properties.append(['Timestamp', self.getTimestamp()])
        properties.append(['Filename', self.getFilename()])
        properties.append(['Creation Date', self.getCreationDate()])
        properties.append(['Modification Date', self.getModificationDate()])
        properties.append(['Owner', self.getOwner()])
        properties.append(['Size', self.getSize()])
        properties.append(['Line number', self.getLineNumber()])        
        properties.append(['Data', self.getStringData()])
        
        return properties 
        
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
  

