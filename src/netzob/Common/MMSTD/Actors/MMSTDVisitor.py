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
from threading import Thread

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from ... import ConfigurationParser

#+---------------------------------------------------------------------------+
#| Configuration of the logger
#+---------------------------------------------------------------------------+
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------------------------------------+
#| MMSTDVisitor :
#|     Definition of a visitor of an MMSTD automata
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.3
#+---------------------------------------------------------------------------+
class MMSTDVisitor():
    
    def __init__(self, mmstd, isMaster, inputFile, outputFile):
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Common.MMSTD.Actors.MMSTDVisitor.py')
        self.mmstd = mmstd
        self.isMaster = isMaster
        self.inputFile = inputFile
        self.outputFile = outputFile
        
    def run(self):
        self.log.info("The MMSTD Visitor is running")
        # self.rfile is a file-like object created by the handler;
        # we can now use e.g. readline() instead of raw recv() calls
        data = self.inputFile.readline().strip()
        while data != "quit" :
            print data
            # Likewise, self.wfile is a file-like object used to write back
            # to the client
            self.outputFile.write(data.upper())
            data = self.inputFile.readline().strip()
                
    #+-----------------------------------------------------------------------+
    #| GETTERS AND SETTERS
    #+-----------------------------------------------------------------------+
    def getName(self):
        return self.name
    def getModel(self):
        return self.model
    def isMaster(self):
        return self.isMaster
    
    def setModel(self, model):
        self.model = model
    def setName(self, name):
        self.name = name
    
    
