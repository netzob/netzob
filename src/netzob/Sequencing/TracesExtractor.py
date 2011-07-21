#!/usr/bin/ python
# coding: utf8

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
import MessageGroup
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
    def __init__(self, zob):
        self.zob = zob
        self.path = self.zob.tracePath
        # create logger with the given configuration
        self.log = logging.getLogger('netzob.Sequencing.TraceExtractor.py')
    
    #+---------------------------------------------- 
    #| Parse :
    #| @update the groups paramter with the computed groups of messages
    #+----------------------------------------------   
    def parse(self):
        self.log.info("[INFO] Extract traces from directory {0}".format(self.path))
        t1 = time.time()

        # Retrieves all the files to parse
        files = []
        for file in os.listdir(self.path):
            filePath = self.path + "/" + file
            
            if file == '.svn':
                self.log.warning("[INFO] Do not parse file {0}".format(filePath))
            else :
                files.append(file)
        
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
            group = MessageGroup.MessageGroup(file, tmpMessages)            
            # Now we try to clusterize the newly created group
            clusterer = Clusterer.Clusterer(self.zob, [group], explodeGroups=True)
            clusterer.mergeGroups()
            groups.extend( clusterer.getGroups() )
                
        # Now that all the groups are reorganized separately
        # we should consider merging them
        self.log.info("Merging the groups extracted from the different files")
        clusterer = Clusterer.Clusterer(self.zob, groups)
        clusterer.mergeGroups()
        
        # Now we execute the second part of Netzob Magical Algorithms :)
        # clean the single groups
        clusterer.mergeOrphanGroups()

        self.log.info("Time of parsing : " + str(time.time() - t1))

        for group in clusterer.getGroups() :
            self.log.debug("Group {0}".format(group.getName()))
            for message in group.getMessages() :
                self.log.debug("- "+message.getStringData())

        return clusterer.getGroups()
