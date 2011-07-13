#!/usr/bin/ python
# coding: utf8

#+---------------------------------------------- 
#| Global Imports
#+----------------------------------------------
import gtk
import os
import gobject
import pygtk
import logging
pygtk.require('2.0')

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
        groups = []

        # Retrieves all the files to parse
        files = []
        for file in os.listdir(self.path):
            filePath = self.path + "/" + file
            
            if file == '.svn':
                self.log.warning("[INFO] Do not parse file {0}".format(filePath))
            else :
                files.append(file)
        
        # compute the progression step
        # 2 steps per file
        progressionStep = 1.0 / len(files)        

        # Parse each file
        tmp_groups = []
        for file in files :
            filePath = self.path + "/" + file
            traceParser = TraceParser.TraceParser(filePath)
            # Append retrieved message to the final list
            tmpMessages = []
            tmpMessages = traceParser.parse()
            # Save the extracted messages in a dedicated group
            group = MessageGroup.MessageGroup(file, tmpMessages)
            
            # Now we try to re-organize the newly created group
            clusterer = Clusterer.Clusterer()
            for g in clusterer.reOrganize([group]) :
                tmp_groups.append(g)
            
            gobject.idle_add(self.doProgressBarStep, progressionStep)
            
        # Now that all the groups are reorganized separatly
        # we should consider merging them
        clusterer = Clusterer.Clusterer()
        for g in clusterer.reOrganizeGroups(tmp_groups) :
            groups.append(g)

        #Once files parsed, reset the progressBar
        gobject.idle_add(self.resetProgressBar)
        
        for group in groups :
            self.log.debug("Group {0}".format(group.getName()))
            for message in group.getMessages() :
                self.log.debug("- "+message.getStringData())

        return groups
        
    #+---------------------------------------------- 
    #| doProgressBarStep :
    #+----------------------------------------------    
    def doProgressBarStep(self, step):
        new_val = self.zob.progressBar.get_fraction() + step
        self.zob.progressBar.set_fraction(new_val)
        
    #+---------------------------------------------- 
    #| resetProgressBar :
    #+----------------------------------------------
    def resetProgressBar(self):
        self.zob.progressBar.set_fraction(0)
