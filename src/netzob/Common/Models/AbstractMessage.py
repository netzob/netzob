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
import uuid
import re
import glib

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from .. import ConfigurationParser

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| AbstractMessage :
#|     Definition of a message
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------------------------------------+
class AbstractMessage():
    
    def __init__(self, type):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.Models.AbstractMessage.py')
        self.id = uuid.uuid4() 
        self.type = type
        self.group = None
        self.rightReductionFactor = 0
        self.leftReductionFactor = 0
        
    
    #+-----------------------------------------------------------------------+
    #| getFactory
    #|     Abstract method to retrieve the associated factory
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def getFactory(self):
        self.log.error("The message class doesn't have an associated factory !")
        raise NotImplementedError("The message class doesn't have an associated factory !")
    
    #+-----------------------------------------------------------------------+
    #| getProperties
    #|     Abstract method to retrieve the properties of the message
    #|     MUST BE IMPLEMENTED IN SUB CLASSES
    #+-----------------------------------------------------------------------+
    def getProperties(self):
        self.log.error("The message class doesn't have a method 'getProperties' !")
        raise NotImplementedError("The message class doesn't have a method 'getProperties' !")
    
    #+---------------------------------------------- 
    #|`getStringData : compute a string representation
    #| of the data 
    #| @return string(data)
    #+----------------------------------------------
    def getStringData(self):
        return str(self.data)
    
    def getReducedSize(self):
        start = 0
        end = len(self.getStringData())
        
        if self.getLeftReductionFactor() > 0 :
            start = self.getLeftReductionFactor() * len(self.getStringData()) / 100
            if (end - start) % 2 == 1 :
                start = start - 1
        if self.getRightReductionFactor() > 0 :
            end = self.getRightReductionFactor() * len(self.getStringData()) / 100 
            if (end - start) % 2 == 1 :
                end = end + 1 
        
        if (end - start) % 2 == 1 :
            end = end + 1 
            
        return len(self.getStringData()) - (end - start)
    
    def getReducedStringData(self):        
        start = 0
        end = len(self.getStringData())
        
        if self.getLeftReductionFactor() > 0 :
            start = self.getLeftReductionFactor() * len(self.getStringData()) / 100
            if (end - start) % 2 == 1 :
                start = start - 1 
        if self.getRightReductionFactor() > 0 :
            end = self.getRightReductionFactor() * len(self.getStringData()) / 100 
            if (end - start) % 2 == 1 :
                end = end + 1
                
                  
        return "".join(self.getStringData()[start:end]) 
    
    #+---------------------------------------------- 
    #| applyRegex: apply the current regex on the message
    #|  and return a table
    #+----------------------------------------------
    def applyRegex(self, styled=False, encoded=False):
        regex = []
        for col in self.group.getColumns():
            regex.append(col['regex'])
        compiledRegex = re.compile("".join(regex))
        data = self.getStringData()
        m = compiledRegex.match(data)
        if m == None:
            self.log.warning("The regex of the group doesn't match one of its message")
            return [ self.getStringData() ]
        res = []
        iCol = 0
        dynamicCol = 1
        for col in self.group.getColumns():
            if col['regex'].find("(") != -1: # Means this column is not static
                start = m.start(dynamicCol)
                end = m.end(dynamicCol)
                if self.group.getColorByCol(iCol) == "" or self.group.getColorByCol(iCol) == None:
                    color = 'blue'
                else:
                    color = self.group.getColorByCol(iCol)
                if styled:
                    if encoded:
                        res.append('<span foreground="' + color + '" font_family="monospace">' + glib.markup_escape_text(self.group.getRepresentation(data[start:end], iCol)) + '</span>')
                    else:
                        res.append('<span foreground="' + color + '" font_family="monospace">' + data[start:end] + '</span>')
                else:
                    if encoded:
                        res.append(glib.markup_escape_text(self.group.getRepresentation(data[start:end], iCol)))
                    else:
                        res.append(data[start:end])
                dynamicCol += 1
            else:
                if styled:
                    if encoded:
                        res.append('<span>' + glib.markup_escape_text(self.group.getRepresentation(col['regex'], iCol)) + '</span>')
                    else:
                        res.append('<span>' + col['regex'] + '</span>')
                else:
                    if encoded:
                        res.append(glib.markup_escape_text(self.group.getRepresentation(col['regex'], iCol)))
                    else:
                        res.append(col['regex'])
            iCol = iCol + 1
        return res
    
    
    
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getID(self):
        return self.id
    def getType(self):
        return self.type
    def getData(self):
        return self.data.strip()
    def getGroup(self):
        return self.group
    def getRightReductionFactor(self):
        return self.rightReductionFactor
    def getLeftReductionFactor(self):
        return self.leftReductionFactor
    
    def setID(self, id):
        self.id = id
    def setType(self, type):
        self.type = type
    def setData(self, data):
        self.data = data
    def setGroup(self, group):
        self.group = group
    def setRightReductionFactor(self, factor):
        self.rightReductionFactor = factor
        self.leftReductionFactor = 0
    def setLeftReductionFactor(self, factor):
        self.leftReductionFactor = factor
        self.rightReductionFactor = 0
