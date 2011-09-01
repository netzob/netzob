#!/usr/bin/ python
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

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import gtk
import os
import gobject
import pygtk
pygtk.require('2.0')
import logging
import time

#+---------------------------------------------- 
#| Local Imports
#+----------------------------------------------
import Clusterer
import TraceParser
import ConfigParser
from ..Common import Group
from ..Common import ConfigurationParser

#+---------------------------------------------- 
#| Configuration of the logger
#+----------------------------------------------
loggingFilePath = ConfigurationParser.ConfigurationParser().get("logging", "path")
logging.config.fileConfig(loggingFilePath)

#+---------------------------------------------- 
#| TracesExtractor :
#|     manage the extraction of messages from traces
#| @author     : {gbt,fgy}@amossys.fr
#| @version    : 0.2
#+---------------------------------------------- 
class TracesExtractor(object):
    #+---------------------------------------------- 
    #| Constructor :
    #| @param path: path of the directory containing traces to parse 
    #+----------------------------------------------   
    def __init__(self, netzob):
        self.netzob = netzob
        self.path = self.netzob.tracePath
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Modelization.TracesExtractor.py')
    
    #+---------------------------------------------- 
    #| Parse :
    #| @update the groups paramter with the computed groups of messages
    #+----------------------------------------------   
    def parse(self):
        self.log.info("[INFO] Extract traces from directory {0}".format(self.path))
        t1 = time.time()

        # Retrieves all the files to parse
        files = []
        foundConfigFile = False
        
        for file in os.listdir(self.path):
            filePath = self.path + "/" + file
            if file == '.svn':
                self.log.warning("[INFO] Do not parse file {0}".format(filePath))
            elif file == "config.xml":
                foundConfigFile = True
            else :
                files.append(file)
        
        if foundConfigFile :
            self.log.info("A configuration file has been found.")
            configParser = ConfigParser.ConfigParser(self.path+"/config.xml")
            configParser.loadConfiguration()
            return configParser.getGroups()
         
        else :            
            # Parse each file
            groups = []
            for file in files :
                filePath = self.path + "/" + file
                
                # TODO in futur
                # Retrieves the extension of the files in directory
    #            fileExtension = os.path.splitext(filePath)[1]
    #            if (fileExtension != ".xml") :
    #                self.log.warning("Do not parse file {0} since it's not an xml file (extension {1})".format(filePath, fileExtension))
                   
                traceParser = TraceParser.TraceParser(filePath)
                # Append retrieved message to the final list
                tmpMessages = traceParser.parse()
                # Save the extracted messages in a dedicated group
                group = Group.Group(file, tmpMessages)            
                # Now we try to clusterize the newly created group
                clusterer = Clusterer.Clusterer(self.netzob, [group], explodeGroups=True)
                clusterer.mergeGroups()
                groups.extend( clusterer.getGroups() )
                    
            # Now that all the groups are reorganized separately
            # we should consider merging them
            self.log.info("Merging the groups extracted from the different files")
            clusterer = Clusterer.Clusterer(self.netzob, groups, explodeGroups=False)
            clusterer.mergeGroups()
            
            # Now we execute the second part of Netzob Magical Algorithms :)
            # clean the single groups
            if ConfigurationParser.ConfigurationParser().getInt("clustering", "orphan_reduction") == 1 :
                self.log.info("Merging the orphan groups") 
                clusterer.mergeOrphanGroups()
    
            self.log.info("Time of parsing : " + str(time.time() - t1))
    
            for group in clusterer.getGroups() :
                self.log.debug("Group {0}".format(group.getName()))
                for message in group.getMessages() :
                    self.log.debug("- "+message.getStringData())
    
            return clusterer.getGroups()
